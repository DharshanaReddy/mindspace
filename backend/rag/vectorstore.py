"""
ChromaDB vector store for mental health knowledge retrieval.
Provides grounded, evidence-based context to the Kai chatbot via semantic search.
"""

import chromadb
from chromadb.utils import embedding_functions
from langsmith import traceable
import os
import logging
from .knowledge_base import MENTAL_HEALTH_DOCUMENTS

logger = logging.getLogger(__name__)

_collection = None
COLLECTION_NAME = "mental_health_knowledge"


def _get_collection() -> chromadb.Collection:
    global _collection
    if _collection is not None:
        return _collection

    client = chromadb.Client()
    ef = embedding_functions.OpenAIEmbeddingFunction(
        api_key=os.getenv("OPENAI_API_KEY"),
        model_name="text-embedding-3-small",
    )

    try:
        _collection = client.get_collection(COLLECTION_NAME, embedding_function=ef)
    except Exception:
        _collection = client.create_collection(COLLECTION_NAME, embedding_function=ef)
        _collection.add(
            ids=[d["id"] for d in MENTAL_HEALTH_DOCUMENTS],
            documents=[d["content"] for d in MENTAL_HEALTH_DOCUMENTS],
            metadatas=[d["metadata"] for d in MENTAL_HEALTH_DOCUMENTS],
        )
        logger.info(f"Seeded {len(MENTAL_HEALTH_DOCUMENTS)} mental health docs into ChromaDB")

    return _collection


@traceable(name="mental-health-rag-retrieval")
def retrieve_mental_health_context(query: str, n_results: int = 3) -> tuple[str, list[str]]:
    """
    Retrieve relevant mental health knowledge for Kai's responses.
    Returns (context_text, source_ids) for transparency.
    """
    try:
        col = _get_collection()
        results = col.query(query_texts=[query], n_results=n_results)
        docs = results.get("documents", [[]])[0]
        ids = results.get("ids", [[]])[0]
        context = "\n\n---\n\n".join(docs) if docs else ""
        return context, ids
    except Exception as e:
        logger.warning(f"RAG retrieval failed: {e}")
        return "", []
