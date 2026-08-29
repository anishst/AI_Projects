import os
from langchain_community.document_loaders import DirectoryLoader, TextLoader, CSVLoader
from langchain_experimental.text_splitter import SemanticChunker
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma

def build_or_get_retriever(data_folder="./data", persist_directory="./chroma_db"):
    # 1. Initialize Embedding Model
    embeddings = OllamaEmbeddings(model="mxbai-embed-large")

    # 2. Check if persistent vector database already exists
    if os.path.exists(persist_directory) and os.listdir(persist_directory):
        print("Loading existing Chroma vector database...")
        vector_db = Chroma(
            persist_directory=persist_directory,
            embedding_function=embeddings
        )
    else:
        print(f"Loading documents from directory: {data_folder}...")
        
        # Load standard text/markdown files
        text_loader = DirectoryLoader(
            data_folder,
            glob="**/*.txt",
            loader_cls=TextLoader,
            loader_kwargs={"encoding": "utf-8"}
        )
        
        # Load CSV files using CSVLoader
        csv_loader = DirectoryLoader(
            data_folder,
            glob="**/*.csv",
            loader_cls=CSVLoader,
            loader_kwargs={"encoding": "utf-8"}
        )

        # Execute loading for all file types
        documents = text_loader.load() + csv_loader.load()
        print(f"Loaded {len(documents)} document record(s).")

        # 3. Apply Semantic Chunking based on embedding distance breaks
        print("Splitting documents semantically...")
        text_splitter = SemanticChunker(
            embeddings,
            breakpoint_threshold_type="percentile"  # Options: "percentile", "standard_deviation", "interquartile"
        )
        chunks = text_splitter.split_documents(documents)
        print(f"Created {len(chunks)} semantic chunks.")

        # 4. Store in Chroma Vector Database with persistence
        print("Creating Chroma vector store...")
        vector_db = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            persist_directory=persist_directory
        )

    return vector_db.as_retriever(search_kwargs={"k": 4})