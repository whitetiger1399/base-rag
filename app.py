import streamlit as st

from src.generation import ABSTAIN_MESSAGE
from src.rag import MalawiRAG


st.set_page_config(page_title="Malawi Public Health RAG", page_icon="🇲🇼", layout="wide")
st.title("Malawi Public Health RAG")
st.caption("Local Qwen3 assistant grounded in Malawi IDSR training guidelines")


@st.cache_resource
def load_rag() -> MalawiRAG:
    return MalawiRAG()


with st.sidebar:
    st.header("Retrieval settings")
    top_k = st.slider("Evidence chunks", min_value=3, max_value=8, value=4)
    trace = st.toggle("Trace mode", value=True)
    st.info(
        "Answers are public-health information from the supplied guidelines and "
        "are not personal medical advice."
    )

query = st.text_area(
    "Question",
    placeholder="What is community-based surveillance?",
    height=100,
)

if st.button("Ask", type="primary", disabled=not query.strip()):
    try:
        with st.spinner("Retrieving evidence and asking the local model..."):
            response = load_rag().ask(query, k=top_k)
        if response.answer == ABSTAIN_MESSAGE:
            st.warning(response.answer)
        else:
            st.markdown(response.answer)

        if trace:
            st.subheader("Retrieval trace")
            for item in response.retrieved:
                semantic = "n/a" if item.semantic_similarity is None else f"{item.semantic_similarity:.3f}"
                bm25 = "n/a" if item.bm25_score is None else f"{item.bm25_score:.3f}"
                label = (
                    f"#{item.rank} {item.chunk.chunk_id} · semantic {semantic} · "
                    f"BM25 {bm25} · hybrid {item.hybrid_score:.5f}"
                )
                with st.expander(label):
                    st.caption(
                        f"{item.chunk.source_file} · {item.chunk.section} · "
                        f"paragraphs {item.chunk.paragraph_start}–{item.chunk.paragraph_end}"
                    )
                    st.code(item.chunk.text, language=None)
    except Exception as exc:
        st.error(f"The RAG service could not answer: {exc}")
        st.caption("Run ingest.py and index.py first, and confirm Ollama is running.")
