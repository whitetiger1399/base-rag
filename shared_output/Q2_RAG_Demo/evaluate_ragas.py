"""Sequential, checkpointed Ragas 0.1.21 evaluation. No work at import time."""
from __future__ import annotations

import argparse
import asyncio
import csv
import hashlib
import json
import math
import os
from pathlib import Path
from datetime import datetime, timezone
from dataclasses import asdict, replace

ROOT = Path(__file__).resolve().parent


def check_judge_budget(tokenizer, text, cfg):
    tokens = len(tokenizer.apply_chat_template(
        [{'role': 'user', 'content': text}], tokenize=True,
        add_generation_prompt=True, enable_thinking=False,
    ))
    if tokens + cfg['judge_output_tokens'] + 128 > cfg['judge_context_tokens']:
        raise ValueError(f"Judge context overflow: {tokens} input tokens + "
                         f"{cfg['judge_output_tokens']} output + 128 reserve exceeds "
                         f"{cfg['judge_context_tokens']}; metric skipped without truncation.")
    return tokens


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, default=str).encode()).hexdigest()


def write_json(path, value):
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(value, indent=2, default=str, allow_nan=False))
    temporary.replace(path)


def append(path, value):
    with path.open('a', encoding='utf-8') as handle:
        handle.write(json.dumps(value, default=str, allow_nan=False) + '\n')
        handle.flush()
        os.fsync(handle.fileno())


def read_log(path):
    if not path.exists():
        return []
    records = []
    with path.open('rb+') as handle:
        while True:
            offset = handle.tell()
            line = handle.readline()
            if not line:
                break
            if not line.endswith(b'\n'):
                handle.truncate(offset)
                break
            records.append(json.loads(line))
    return records


def report(folder, selected, metrics):
    latest = {(r['id'], r['metric']): r for r in read_log(folder / 'metrics.jsonl')}
    summary = {}
    for name in metrics:
        rows = [latest.get((qid, name), {}) for qid in selected]
        values = [r['value'] for r in rows if r.get('status') == 'ok']
        summary[name] = {'mean': sum(values) / len(values) if values else None,
                         'valid': len(values), 'selected': len(selected),
                         'failed': sum(r.get('status') == 'error' for r in rows),
                         'not_applicable': sum(r.get('status') == 'not_applicable' for r in rows)}
    write_json(folder / 'summary.json', summary)
    with (folder / 'scores.csv').open('w', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=['id', 'metric', 'value', 'status', 'error'])
        writer.writeheader()
        writer.writerows(latest.values())
    lines = ['# Ragas results', '', 'Development smoke benchmark; not an independent test score.', '',
             '| Metric | Mean | Valid / selected | Errors | N/A |', '|---|---:|---:|---:|---:|']
    for name, s in summary.items():
        lines.append(f"| {name} | {s['mean']} | {s['valid']}/{s['selected']} | {s['failed']} | {s['not_applicable']} |")
    (folder / 'report.md').write_text('\n'.join(lines) + '\n')
    return summary


async def execute(cfg, folder, records, manifest):
    # Lazy imports keep --help usable before evaluation dependencies are installed.
    import aiohttp
    import requests
    import torch
    from importlib.metadata import version
    from langchain_core.outputs import Generation, LLMResult
    from langchain_core.embeddings import Embeddings
    from transformers import AutoTokenizer
    from ragas.llms import BaseRagasLLM
    from ragas.embeddings import LangchainEmbeddingsWrapper
    from ragas.run_config import RunConfig
    from ragas import metrics as available
    from src.config import SETTINGS
    from src.rag import MalawiRAG
    from src.generation import _select_context, generate_answer

    if version('ragas') != '0.1.21':
        raise ValueError('This adapter requires ragas==0.1.21; install requirements.txt.')
    torch.set_num_threads(cfg['cpu_threads'])
    run_config = RunConfig(max_workers=1, max_retries=1, timeout=cfg['http_timeout_seconds'])
    deadline = aiohttp.ClientTimeout(total=cfg['http_timeout_seconds'], connect=10)
    async with aiohttp.ClientSession(timeout=deadline) as session:
        async with session.get(SETTINGS.ollama_url.rstrip('/') + '/api/tags') as response:
            response.raise_for_status()
            tags = await response.json()
        model = next((m for m in tags['models'] if m['name'] == SETTINGS.ollama_model), None)
        if model is None:
            raise ValueError(f'Ollama model missing: {SETTINGS.ollama_model}')
        model_digest = model.get('digest')
        if manifest.get('model_digest') not in (None, model_digest):
            raise ValueError('Model changed; start a new run.')
        manifest['model_digest'] = model_digest
        write_json(folder / 'manifest.json', manifest)

        tokenizer = AutoTokenizer.from_pretrained(
            cfg.get('judge_tokenizer', 'Qwen/Qwen3-8B'), trust_remote_code=False,
            local_files_only=cfg.get('tokenizer_local_files_only', False),
        )

        class Judge(BaseRagasLLM):
            def generate_text(self, *args, **kwargs):
                raise RuntimeError('Use asynchronous scoring in the single owned event loop.')

            async def agenerate_text(self, prompt, n=1, temperature=None, stop=None, callbacks=None):
                text = prompt.to_string()
                check_judge_budget(tokenizer, text, cfg)
                generations = []
                for _ in range(n):
                    async with session.post(SETTINGS.ollama_url.rstrip('/') + '/api/chat', json={
                        'model': SETTINGS.ollama_model, 'think': False, 'stream': False,
                        'messages': [{'role': 'user', 'content': text}],
                        'options': {'temperature': 0, 'num_ctx': cfg['judge_context_tokens'],
                                    'num_predict': cfg['judge_output_tokens'], 'stop': stop or []},
                    }) as response:
                        response.raise_for_status()
                        payload = await response.json()
                    append(folder / 'judge_calls.jsonl', {'prompt': text, 'response': payload})
                    if payload.get('done_reason') == 'length':
                        raise ValueError('Judge output truncated; no score accepted.')
                    generations.append(Generation(text=payload['message']['content']))
                return LLMResult(generations=[generations])

        llm = Judge(run_config=run_config)
        # Share the retriever's existing MiniLM instance; no second model or pool.
        from src.retrieval import HybridRetriever
        retriever = HybridRetriever(SETTINGS)
        retriever.encoder.to('cpu')

        class LocalEmbeddings(Embeddings):
            def embed_documents(self, texts):
                return retriever.encoder.encode(texts, normalize_embeddings=True,
                                                batch_size=8).tolist()

            def embed_query(self, text):
                return self.embed_documents([text])[0]

            async def aembed_documents(self, texts):
                return self.embed_documents(texts)

            async def aembed_query(self, text):
                return self.embed_query(text)

        embeddings = LangchainEmbeddingsWrapper(LocalEmbeddings())
        metrics = []
        for name in cfg['metrics']:
            import copy
            metric = copy.deepcopy(getattr(available, name))
            if hasattr(metric, 'llm'):
                metric.llm = llm
            if hasattr(metric, 'embeddings'):
                metric.embeddings = embeddings
            metric.init(run_config)
            metrics.append(metric)

        captured = []
        def generator(question, results, settings):
            _, included = _select_context(results, settings.max_context_chars)
            captured.extend(item.chunk.text for item in included)
            # Extend transport patience only; preserve prompts and generation budgets.
            generation_settings = replace(settings, request_timeout_seconds=cfg['generation_timeout_seconds'])
            return generate_answer(question, results, generation_settings)

        rag = MalawiRAG(settings=SETTINGS, retriever=retriever, answer_generator=generator)
        answers = {r['id']: r for r in read_log(folder / 'answers.jsonl')}
        scored = {(r['id'], r['metric']): r for r in read_log(folder / 'metrics.jsonl')}
        failures = 0
        for index, source in enumerate(records, 1):
            qid = source['ID']
            print(f'[{index}/{len(records)}] {qid}: answer', flush=True)
            if qid not in answers:
                captured.clear()
                try:
                    result = rag.ask(source['Question Text'])
                except requests.RequestException as exc:
                    append(folder / 'errors.jsonl', {
                        'id': qid, 'stage': 'answer', 'error': f'{type(exc).__name__}: {exc}',
                        'timeout_seconds': cfg['generation_timeout_seconds'],
                    })
                    raise SystemExit(
                        f'Answer generation failed for {qid}: {exc}. '
                        f'Progress saved in {folder}. Confirm Ollama is idle before resuming; '
                        'no automatic retry was submitted.'
                    ) from None
                answers[qid] = {'id': qid, 'question': source['Question Text'], 'answer': result.answer,
                               'contexts': list(captured), 'ground_truth': source['Question Answer'],
                               'retrieval_contexts': [r.chunk.text for r in result.retrieved],
                               'retrieved': [r.to_dict() for r in result.retrieved],
                               'abstained': result.abstained, 'quarantined_ids': result.quarantined_ids}
                append(folder / 'answers.jsonl', answers[qid])
            row = answers[qid]
            for metric in metrics:
                key = (qid, metric.name)
                if key in scored and scored[key]['status'] != 'error':
                    continue
                print(f'[{index}/{len(records)}] {qid}: {metric.name}', flush=True)
                entry = {'id': qid, 'metric': metric.name, 'value': None, 'status': 'ok', 'error': ''}
                try:
                    if row['abstained'] and metric.name == 'faithfulness':
                        entry['status'] = 'not_applicable'
                    else:
                        metric_row = dict(row)
                        if metric.name in ('context_precision', 'context_recall'):
                            metric_row['contexts'] = row['retrieval_contexts']
                        value = float(await metric.ascore(metric_row, timeout=cfg['metric_timeout_seconds']))
                        if not math.isfinite(value):
                            raise ValueError('Metric returned a non-finite score')
                        entry['value'] = value
                    failures = 0
                except Exception as exc:
                    entry.update(status='error', error=f'{type(exc).__name__}: {exc}')
                    print(f'  {entry["error"]}', flush=True)
                    # Data/schema/context errors are metric failures, not infrastructure.
                    # A timeout may leave Ollama working: stop safely, never overlap retries.
                    fatal = isinstance(exc, (asyncio.TimeoutError, aiohttp.ClientError))
                    failures = cfg['failure_limit'] if fatal else 0
                append(folder / 'metrics.jsonl', entry)
                report(folder, [r['ID'] for r in records], cfg['metrics'])
                if failures >= cfg['failure_limit']:
                    raise RuntimeError(f"Ollama transport failed for {qid}/{metric.name}: {entry['error']}. "
                                       'Saved completed work; confirm Ollama is idle before resuming.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, default=ROOT / 'evaluation_config.json')
    parser.add_argument('--resume', type=Path, help='Existing run directory; skips saved answers and successful metrics')
    args = parser.parse_args()
    cfg = json.loads(args.config.read_text())
    cfg.setdefault('generation_timeout_seconds', 600)
    for key in ('max_questions', 'cpu_threads', 'judge_context_tokens', 'judge_output_tokens',
                'http_timeout_seconds', 'metric_timeout_seconds', 'generation_timeout_seconds', 'failure_limit'):
        if not isinstance(cfg[key], int) or cfg[key] < 1:
            raise ValueError(f'{key} must be a positive integer')
    allowed_metrics = {'faithfulness', 'answer_relevancy', 'context_precision', 'context_recall', 'answer_correctness', 'answer_similarity'}
    if not cfg['metrics'] or len(set(cfg['metrics'])) != len(cfg['metrics']) or not set(cfg['metrics']).issubset(allowed_metrics):
        raise ValueError('Configure unique supported metric names')
    if cfg['judge_context_tokens'] <= cfg['judge_output_tokens'] + 128:
        raise ValueError('Judge context must leave room for the input prompt')
    if cfg['cpu_threads'] > 2:
        raise ValueError('M1 profile caps CPU threads at two')
    for name in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS'):
        os.environ[name] = str(cfg['cpu_threads'])
    os.environ['TOKENIZERS_PARALLELISM'] = 'false'
    os.environ['RAGAS_DO_NOT_TRACK'] = 'true'
    from src.config import SETTINGS
    dataset = ROOT / cfg['train_csv']
    with dataset.open(encoding='utf-8-sig', newline='') as handle:
        rows = list(csv.DictReader(handle))
    required = {'ID', 'Question Text', 'Question Answer'}
    if not rows or not required.issubset(rows[0]):
        raise ValueError('Expected labeled Train.csv schema')
    if len({r['ID'] for r in rows}) != len(rows):
        raise ValueError('Duplicate question IDs')
    if any(not r[k].strip() for r in rows for k in required):
        raise ValueError('Missing question, ID, or reference answer')
    # Stable selection independent of CSV order; saved IDs define this development smoke set.
    rows.sort(key=lambda r: digest([cfg['seed'], r['ID']]))
    rows = rows[:cfg['max_questions']]
    fingerprint = digest({'config': cfg, 'settings': asdict(SETTINGS),
                          'data': hashlib.sha256(dataset.read_bytes()).hexdigest(),
                          'code': {str(p.relative_to(ROOT)): digest(p.read_text()) for p in [Path(__file__), *sorted((ROOT / 'src').glob('*.py'))]},
                          'index': SETTINGS.manifest_path.read_text()})
    output = ROOT / cfg['output_dir']
    output.mkdir(parents=True, exist_ok=True)
    import fcntl
    with (output / '.evaluation.lock').open('w') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise SystemExit('Another evaluator is running for this output directory.')
        folder = args.resume.resolve() if args.resume else output / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
        folder.mkdir(parents=True, exist_ok=True)
        manifest_path = folder / 'manifest.json'
        manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {
            'fingerprint': fingerprint, 'selected_ids': [r['ID'] for r in rows], 'config': cfg,
            'application_settings': asdict(SETTINGS), 'split': 'development smoke; not held-out', 'ragas_version': '0.1.21'}
        if manifest['fingerprint'] != fingerprint:
            raise ValueError('Resume inputs/config/code changed; start a new run.')
        manifest['status'] = 'running'
        write_json(manifest_path, manifest)
        print(f'Run directory: {folder}', flush=True)
        try:
            asyncio.run(execute(cfg, folder, rows, manifest))
            scores = report(folder, manifest['selected_ids'], cfg['metrics'])
            manifest['status'] = 'partial' if any(v['failed'] for v in scores.values()) else 'completed'
        except BaseException:
            manifest['status'] = 'interrupted_or_failed'
            raise
        finally:
            write_json(manifest_path, manifest)
            report(folder, manifest['selected_ids'], cfg['metrics'])


if __name__ == '__main__':
    main()
