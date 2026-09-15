"""No model, network, or Ragas imports needed for budget regression checks."""
import runpy
from pathlib import Path
import pytest

check = runpy.run_path(str(Path(__file__).resolve().parents[1] / 'evaluate_ragas.py'),
                      run_name='budget_test')['check_judge_budget']

class Tokenizer:
    def __init__(self, tokens):
        self.tokens = tokens

    def apply_chat_template(self, messages, **kwargs):
        assert kwargs['enable_thinking'] is False
        assert kwargs['add_generation_prompt'] is True
        return [0] * self.tokens

def test_long_text_is_not_counted_as_bytes():
    assert check(Tokenizer(2000), 'word ' * 3000,
                 {'judge_output_tokens': 1024, 'judge_context_tokens': 8192}) == 2000

def test_real_token_overflow_is_rejected():
    with pytest.raises(ValueError, match='8000 input tokens'):
        check(Tokenizer(8000), 'text',
              {'judge_output_tokens': 1024, 'judge_context_tokens': 8192})
