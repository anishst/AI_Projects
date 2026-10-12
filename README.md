# AI Projects

A dedicated testing ground for evaluating state-of-the-art AI models and integration APIs.

## Setup

This repo uses [uv](https://docs.astral.sh/uv/) for dependency management (see `pyproject.toml` / `uv.lock`). Secrets (API keys) are kept in a local `.env` file (gitignored) and loaded via `python-dotenv`.

```
uv sync
```

## Learnings so far, by subfolder

### `googleai_related/` — Google Gemini / `google-genai`

- Install the official SDK + dotenv helper: `pip install google-genai python-dotenv`.
- Auth via `.env`: `GEMINI_API_KEY=your_actual_api_key_here`.
- `genai.Client()` automatically picks up `GEMINI_API_KEY` from the environment — no need to pass it explicitly (though you can via `genai.Client(api_key=...)`).
- Text generation uses `client.models.generate_content(model=..., contents=..., config={...})`; a `system_instruction` can be passed inside `config` to steer the model's persona/behavior.
- `image.py` explores Gemini's image-related capabilities.

### `openai_related/` — OpenAI API

- Install: `openai`, `python-dotenv`.
- Auth via `.env`: `OPENAI_API_KEY=your_openapi_api_key_here`.
- `OpenAI()` client also auto-reads the key from the environment once `load_dotenv()` has run.
- Basic chat completions use `client.chat.completions.create(model=..., messages=[...])`.
- See the [OpenAI quickstart docs](https://developers.openai.com/api/docs/quickstart?desktop-os=windows) for more.

### `langchain_related/` — LangChain (Ollama, OpenAI, RAG)

General reference: [Private AI Workflows with LangChain + Ollama](https://codecut.ai/private-ai-workflows-langchain-ollama/).

- **Ollama basics**: install [Ollama](https://ollama.com/download), pull a model (`ollama pull qwen3:0.6b`), and serve it (`ollama run qwen3:0.6b`). `OllamaLLM`/`ChatOllama` from `langchain_ollama` connect to a local Ollama server (default `http://localhost:11434`).
- **`text_completion_model/`**: minimal example of plain text completion via `OllamaLLM.invoke(prompt)`, plus a `cli_chat.py` for an interactive loop.
- **`local_rag_llm/`**: local RAG over a CSV of restaurant reviews using `OllamaLLM` (`llama3.2`) + `langchain-chroma` for the vector store, with `mxbai-embed-large` as the embedding model. Pattern: build a `retriever` in `vector.py`, then combine `retriever.invoke(question)` results into a prompt template passed through a `prompt | model` chain.
- **`local_rag_llm_semantic/`**: same local-RAG pattern but with semantic chunking (`langchain-experimental`) and PDF loading (`pypdf`) instead of fixed-size chunking — chunk boundaries follow semantic shifts in the text rather than a fixed character count.
- **`openai_rag_pdf/`**: RAG pipeline using OpenAI embeddings (`text-embedding-3-large`) instead of local models, with `Qdrant` (via `langchain-qdrant`, run through `docker-compose.yml`) as the vector store. Flow: `PyPDFLoader` → `RecursiveCharacterTextSplitter` (chunk_size=1000, overlap=400) → `OpenAIEmbeddings` → `QdrantVectorStore.from_documents(...)`. Requires a `QDRANT_URL` env var and a running Qdrant instance.
- Root-level `chat.py` demonstrates `ChatOllama` with `SystemMessage`/`HumanMessage` for a system+user chat-style call (vs. the plain-text `OllamaLLM.invoke` style).
