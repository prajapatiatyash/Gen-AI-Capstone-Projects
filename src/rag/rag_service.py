from src.rag.embedder import embed_texts
from src.rag.milvus_store import search
from src.llm.client import chat
import json

def retrieve_and_answer(query, user_context=""):
    # Embed query, search milvus, then call LLM with context
    q_emb = embed_texts([query])[0]
    hits = search(q_emb, top_k=4)
    snippets = "\n\n".join([h["text"] for h in hits if h["text"]])
    prompt = f"Context snippets:\n{snippets}\n\nUser context: {user_context}\n\nQuestion:{query}\nAnswer concisely and reference policy snippets."
    answer = chat(prompt)
    return {"answer": answer, "snippets": snippets}
