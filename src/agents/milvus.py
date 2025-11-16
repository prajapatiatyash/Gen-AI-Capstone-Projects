# src/agents/milvus_setup.py
from pymilvus import connections, FieldSchema, CollectionSchema, DataType, Collection
from langchain_classic.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OpenAIEmbeddings
import os
import yaml
from pymilvus import utility


_milvus_cfg_path = os.getenv("MILVUS_CONFIG_PATH", "config/milvus.yaml")

with open(_milvus_cfg_path) as f:
    cfg = yaml.safe_load(f)
MILVUS_URI = cfg["milvus"]["uri"]
MILVUS_TOKEN = cfg["milvus"]["token"]
COLLECTION_NAME = cfg["milvus"]["collection_name"]
DIM = cfg["milvus"]["dim"]


def setup_milvus():
    # Connect to Zilliz Cloud Milvus
    connections.connect(
        alias="default",
        uri=MILVUS_URI,
        token=MILVUS_TOKEN
    )

    # Check if collection exists
    if utility.has_collection(COLLECTION_NAME):
        collection = Collection(COLLECTION_NAME, using="default")
    else:
        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=DIM),
            FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=65535)
        ]
        schema = CollectionSchema(fields, description="Travel Policy Documents")
        collection = Collection(COLLECTION_NAME, schema=schema, using="default")

    collection.load()
    return collection

def ingest_document(file_path, collection):
    with open(file_path, "r") as f:
        text = f.read()
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_text(text)
    embeddings_model = OpenAIEmbeddings()
    vectors = [embeddings_model.embed_text(c) for c in chunks]
    collection.insert([list(range(len(chunks))), vectors, chunks])
    collection.load()

def query_policy(question, collection, top_k=3):
    embedding = OpenAIEmbeddings().embed_text(question)
    search_params = {"metric_type": "IP", "params": {"nprobe": 10}}
    results = collection.search([embedding], "embedding", search_params, limit=top_k, output_fields=["text"])
    context = " ".join([res.entity.get("text") for res in results[0]])
    return context
