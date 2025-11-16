from pymilvus import connections, utility, Collection, FieldSchema, CollectionSchema, DataType
import yaml
import os

cfg_path = os.getenv("MILVUS_CONFIG_PATH", "config/milvus.yaml")
with open(cfg_path, "r") as f:
    cfg = yaml.safe_load(f)["milvus"]

MILVUS_URI = os.getenv("MILVUS_URI", cfg.get("uri"))
MILVUS_TOKEN = os.getenv("MILVUS_TOKEN", cfg.get("token"))
COLLECTION_NAME = cfg.get("collection_name", "travel_policy_embeddings")
DIM = cfg.get("dim", 1536)

def connect():
    connections.connect(uri=MILVUS_URI, token=MILVUS_TOKEN)

def ensure_collection():
    connect()
    if utility.has_collection(COLLECTION_NAME):
        return
    fields = [
        FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
        FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=DIM),
        FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=65535)
    ]
    schema = CollectionSchema(fields, description="travel policy store")
    Collection(name=COLLECTION_NAME, schema=schema)

def upsert(texts, embeddings):
    """
    texts: list[str], embeddings: list[list[float]]
    """
    connect()
    ensure_collection()
    col = Collection(COLLECTION_NAME)
    entities = [
        embeddings,
        texts
    ]
    # pymilvus expects column-wise data; using field order
    col.insert([None, embeddings, texts])  # None for auto id
    col.flush()

def search(query_embedding, top_k=4):
    connect()
    col = Collection(COLLECTION_NAME)
    search_params = {"metric_type":"L2", "params":{"nprobe":10}}
    res = col.search([query_embedding], "embedding", search_params, top_k, output_fields=["text"])
    # res is list of QueryResult
    hits = []
    for hit in res[0]:
        hits.append({"id": hit.id, "text": hit.entity.get("text")})
    return hits
