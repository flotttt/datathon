"""
Stockage et retrieval vectoriel avec Chroma DB.

Nécessite :
    - Chroma DB en cours d'exécution (docker compose up -d)
    - MISTRAL_API_KEY pour les embeddings Mistral
      (sinon fallback sur l'embedding function par défaut de Chroma)
"""
from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Any

import pandas as pd
from dotenv import load_dotenv

load_dotenv()

# On essaie d'abord Mistral embeddings ; sinon Chroma default (local)
try:
    from langchain_mistralai import MistralAIEmbeddings

    _mistral_available = bool(os.getenv("MISTRAL_API_KEY"))
except Exception:
    _mistral_available = False

if _mistral_available:
    from chromadb import HttpClient
    from chromadb.utils.embedding_functions import EmbeddingFunction

    class _MistralEmbeddingFunction(EmbeddingFunction):
        """Wrapper Chroma autour des embeddings Mistral."""

        def __init__(self, api_key: str | None = None, model: str = "mistral-embed"):
            self.embedder = MistralAIEmbeddings(
                api_key=api_key or os.getenv("MISTRAL_API_KEY"),
                model=model,
            )

        def __call__(self, input: list[str]) -> list[list[float]]:
            return self.embedder.embed_documents(input)

    DEFAULT_EMBEDDING_MODEL = "mistral-embed"
else:
    from chromadb import HttpClient
    from chromadb.utils.embedding_functions import (
        DefaultEmbeddingFunction as _DefaultEmbeddingFunction,
    )

    _MistralEmbeddingFunction = None  # type: ignore
    DEFAULT_EMBEDDING_MODEL = "default"


CHROMA_HOST = os.getenv("CHROMA_HOST", "localhost")
CHROMA_PORT = int(os.getenv("CHROMA_PORT", "8000"))
COLLECTION_NAME = os.getenv("CHROMA_COLLECTION", "ultia_cnc_tweets")
BATCH_SIZE = int(os.getenv("CHROMA_BATCH_SIZE", "64"))


def get_chroma_client() -> HttpClient:
    return HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)


def get_embedding_function():
    if _mistral_available:
        return _MistralEmbeddingFunction()
    return _DefaultEmbeddingFunction()


def get_or_create_collection(client: HttpClient | None = None):
    if client is None:
        client = get_chroma_client()
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=get_embedding_function(),
        metadata={"hnsw:space": "cosine"},
    )


def index_tweets(
    df: pd.DataFrame,
    text_column: str = "text",
    id_column: str = "postID",
    batch_size: int = BATCH_SIZE,
    progress_every: int = 256,
) -> int:
    """Indexe un DataFrame de tweets dans Chroma. Retourne le nombre de documents indexés."""
    collection = get_or_create_collection()

    # Supprime les doublons d'ID
    df = df.drop_duplicates(subset=[id_column])
    total = len(df)

    for start in range(0, total, batch_size):
        end = min(start + batch_size, total)
        batch = df.iloc[start:end]

        ids = [str(x) for x in batch[id_column].tolist()]
        documents = [str(x) for x in batch[text_column].tolist()]
        metadatas = [
            {
                "author": str(row.get("Author", "")),
                "date": str(row.get("Date", "")),
                "sentiment": str(row.get("Sentiment", "")),
                "likes": int(row.get("Likes", 0) or 0),
                "shares": int(row.get("Shares", 0) or 0),
                "comments": int(row.get("Comments", 0) or 0),
                "url": str(row.get("Url", "")),
            }
            for _, row in batch.iterrows()
        ]

        collection.add(ids=ids, documents=documents, metadatas=metadatas)

        if (end % progress_every) < batch_size:
            print(f"  indexés : {end}/{total}")

        # Petite pause pour respecter le rate limit du free tier Mistral
        if _mistral_available and end < total:
            time.sleep(0.5)

    return total


def query_tweets(
    question: str,
    n_results: int = 10,
    where: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Récupère les tweets les plus pertinents pour une question."""
    collection = get_or_create_collection()
    return collection.query(
        query_texts=[question],
        n_results=n_results,
        where=where,
        include=["documents", "metadatas", "distances"],
    )


def format_retrieved_context(results: dict[str, Any]) -> str:
    """Formate les résultats Chroma en contexte lisible pour un LLM."""
    lines = ["# Tweets pertinents retrouvés\n"]
    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    for idx, (doc, meta, dist) in enumerate(zip(documents, metadatas, distances), 1):
        lines.append(
            f"{idx}. [{meta.get('date', '?')}] @{meta.get('author', '?')} "
            f"(likes={meta.get('likes', 0)}, RT={meta.get('shares', 0)}, dist={dist:.3f})\n"
            f"   {doc}\n"
        )
    return "\n".join(lines)


def is_indexed() -> bool:
    """Vérifie si la collection contient déjà des documents."""
    try:
        collection = get_or_create_collection()
        return collection.count() > 0
    except Exception:
        return False


def collection_count() -> int:
    collection = get_or_create_collection()
    return collection.count()


if __name__ == "__main__":
    from data_utils import load_corpus, filter_keyword

    print("Chargement du corpus...")
    df = load_corpus()
    focus_df = filter_keyword(df, "ultia")
    print(f"Indexation de {len(focus_df)} tweets liés à Ultia...")
    count = index_tweets(focus_df)
    print(f"Indexation terminée : {count} tweets dans Chroma.")
