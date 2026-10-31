"""
A minimal, dependency-light RAG chat app built directly on Ollama's HTTP API
(no langchain/vector-db) — good for understanding what RAG actually does
under the hood: chunk -> embed -> cosine-similarity retrieve -> stuff into prompt.

Prerequisites:
    ollama pull nomic-embed-text
    ollama pull qwen3:0.6b
    ollama serve   (or just have the Ollama desktop app running)

Usage:
    uv run simple_rag.py
"""

import sys
import requests
import numpy as np
from pathlib import Path

OLLAMA = 'http://localhost:11434'
EMBED_MODEL = 'nomic-embed-text'
CHAT_MODEL = 'qwen3:0.6b'
DOCS_FOLDER = Path(__file__).parent / "docs"
TOP_K = 3


def embed(texts):
    """Embed a string or list of strings. Always returns a 2D np.array (n_texts, dim)."""
    r = requests.post(f'{OLLAMA}/api/embed', json={
        'model': EMBED_MODEL,
        'input': texts,  # /api/embed takes 'input' (str or list[str]), not 'prompt'
    })
    r.raise_for_status()
    return np.array(r.json()['embeddings'])


def ask(question, context):
    r = requests.post(f'{OLLAMA}/api/chat', json={
        'model': CHAT_MODEL,
        'messages': [
            {'role': 'system', 'content': context},
            {'role': 'user', 'content': question},
        ],
        'stream': False,  # without this, Ollama streams newline-delimited JSON chunks,
                          # which breaks r.json() with "Extra data" errors
    })
    r.raise_for_status()
    return r.json()['message']['content']


def load_chunks(docs_folder):
    """Split every .md file in docs_folder into paragraph-sized chunks."""
    chunks = []
    for file in sorted(docs_folder.glob("*.md")):
        paragraphs = [p.strip() for p in file.read_text(encoding='utf-8').split('\n\n') if p.strip()]
        chunks.extend(paragraphs)
        print(f"Processed {file.name}: {len(paragraphs)} chunks")
    return chunks


def build_index(chunks):
    """Embed all chunks once up front so retrieval is just a similarity lookup."""
    return embed(chunks)


def retrieve(question, chunks, chunk_vectors, k=TOP_K):
    q = embed([question])[0]
    scores = chunk_vectors @ q / (np.linalg.norm(chunk_vectors, axis=1) * np.linalg.norm(q))
    top_indices = np.argsort(scores)[::-1][:k]
    return [chunks[i] for i in top_indices]


def build_prompt(question, context_chunks):
    context = "\n\n---\n\n".join(context_chunks)
    return f"""Answer the question based on the context below. If the answer isn't in the context, say "I don't know".

Context:
{context}

Question: {question}"""


def main():
    if not DOCS_FOLDER.exists() or not any(DOCS_FOLDER.glob("*.md")):
        print(f"No .md files found in {DOCS_FOLDER}. Add some docs and try again.")
        return

    chunks = load_chunks(DOCS_FOLDER)
    print(f"Total chunks: {len(chunks)}")

    chunk_vectors = build_index(chunks)
    print(f"Indexed {len(chunks)} chunks\n")

    print("RAG chat ready. Ask a question, or type 'q' to quit.")
    while True:
        question = input("\nAsk a question: ").strip()
        if question.lower() in ('q', 'quit', 'exit'):
            break
        if not question:
            continue

        context_chunks = retrieve(question, chunks, chunk_vectors)
        prompt = build_prompt(question, context_chunks)
        print(ask(question, prompt))


if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print(f"\nCouldn't reach Ollama at {OLLAMA}. Is it running? (`ollama serve`)")
        sys.exit(1)
    except (KeyboardInterrupt, EOFError):
        print("\nBye!")
