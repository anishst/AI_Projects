"""
Same minimal, dependency-light RAG pattern as simple_rag.py, but chunking
CSV rows instead of markdown paragraphs: chunk -> embed -> cosine-similarity
retrieve -> stuff into prompt. Built directly on Ollama's HTTP API (no
langchain/vector-db).

Prerequisites:
    ollama pull nomic-embed-text
    ollama pull qwen3:0.6b
    ollama serve   (or just have the Ollama desktop app running)

Usage:
    uv run simple_rag_csv.py
"""

import sys
import requests
import numpy as np
import pandas as pd
from pathlib import Path

OLLAMA = 'http://localhost:11434'
EMBED_MODEL = 'nomic-embed-text'
CHAT_MODEL = 'qwen3:0.6b'
DATA_FOLDER = Path(__file__).parent / "data"
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


def load_chunks(data_folder):
    """Turn every row of every .csv file in data_folder into one text chunk."""
    chunks = []
    for file in sorted(data_folder.glob("*.csv")):
        df = pd.read_csv(file).dropna(how="all")
        row_count = 0
        for _, row in df.iterrows():
            row = row.dropna()
            if row.empty:
                continue
            fields = "\n".join(f"{column}: {value}" for column, value in row.items())
            chunks.append(f"Source: {file.name}\n{fields}")
            row_count += 1
        print(f"Processed {file.name}: {row_count} chunks")
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
    return f"""Answer the question based on the context below, which comes from rows of a CSV
file. If the answer isn't in the context, say "I don't know".

Context:
{context}

Question: {question}"""


def main():
    if not DATA_FOLDER.exists() or not any(DATA_FOLDER.glob("*.csv")):
        print(f"No .csv files found in {DATA_FOLDER}. Add some data and try again.")
        return

    chunks = load_chunks(DATA_FOLDER)
    print(f"Total chunks: {len(chunks)}")

    chunk_vectors = build_index(chunks)
    print(f"Indexed {len(chunks)} chunks\n")

    print("CSV RAG chat ready. Ask a question, or type 'q' to quit.")
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
