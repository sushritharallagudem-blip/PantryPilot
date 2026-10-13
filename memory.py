

from pathlib import Path
from datetime import datetime, timezone

from qdrant_client import QdrantClient, models
from fastembed import TextEmbedding

BASE_DIR = Path(__file__).parent
QDRANT_PATH = BASE_DIR / "qdrant_data"
COLLECTION_NAME = "pantrypilot_memories"

client = QdrantClient(path=str(QDRANT_PATH))
embedding_model = TextEmbedding("BAAI/bge-small-en-v1.5")
VECTOR_SIZE = 384


def initialize_memory():
    if not client.collection_exists(COLLECTION_NAME):
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=models.VectorParams(
                size=VECTOR_SIZE,
                distance=models.Distance.COSINE,
            ),
        )


def remember(text: str, category: str = "general"):
    text = text.strip()
    if not text:
        return

    import hashlib

    memory_id = hashlib.md5(
        f"{category}:{text}".encode("utf-8")
    ).hexdigest()

    vector = list(embedding_model.query_embed(text))[0].tolist()

    client.upsert(
        collection_name=COLLECTION_NAME,
        points=[
            models.PointStruct(
                id=memory_id,
                vector=vector,
                payload={
                    "text": text,
                    "category": category,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                },
            )
        ],
    )



def recall(query: str, limit: int = 3):
    vector = list(embedding_model.query_embed(query))[0].tolist()

    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=vector,
        limit=max(limit * 3, limit),
        with_payload=True,
    ).points

    memories = []
    seen = set()

    for point in results:
        if not point.payload:
            continue

        text = point.payload.get("text", "").strip()

        if text and text not in seen:
            seen.add(text)
            memories.append(text)

        if len(memories) >= limit:
            break

    return memories


initialize_memory()


