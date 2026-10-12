from dotenv import load_dotenv
import os
from pathlib import Path
import pandas as pd
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore

load_dotenv()

data_folder = Path(__file__).parent / "data"
excel_paths = sorted(data_folder.glob("*.xlsx")) + sorted(data_folder.glob("*.xls"))

if not excel_paths:
    raise FileNotFoundError(f"No .xlsx/.xls files found in {data_folder}")

# Load every sheet of every workbook, turning each row into a Document (one row = one "chunk" of context)
docs = []
for excel_path in excel_paths:
    sheets = pd.read_excel(excel_path, sheet_name=None)
    for sheet_name, df in sheets.items():
        for row_number, row in df.iterrows():
            page_content = "\n".join(f"{column}: {value}" for column, value in row.items())
            docs.append(
                Document(
                    page_content=page_content,
                    metadata={
                        "source": str(excel_path),
                        "sheet_name": sheet_name,
                        "row_number": row_number,
                    },
                )
            )

# Split the docs into smaller chunks (rows are usually short, but keeps this consistent with index.py)
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=400
)

chunks = text_splitter.split_documents(documents=docs)

# Vector Embeddings
embedding_model = OpenAIEmbeddings(
    model="text-embedding-3-large"
)

vector_store = QdrantVectorStore.from_documents(
    documents=chunks,
    embedding=embedding_model,
    url=os.getenv("QDRANT_URL"),
    collection_name="learning_rag_excel"
)

print(f"Indexing of {len(excel_paths)} excel file(s) ({len(chunks)} chunks) done....")
