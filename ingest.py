import os
from langchain_community.document_loaders import (
    PyMuPDFLoader, 
    TextLoader, 
    CSVLoader, 
    Docx2txtLoader
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

def ingest_file(file_path: str):
    """Detects file type, loads it, and saves to the local Chroma DB."""
    print(f"Processing: {file_path}")
    
    ext = os.path.splitext(file_path)[1].lower()
    
    if ext == ".pdf":
        loader = PyMuPDFLoader(file_path)
    elif ext == ".docx":
        loader = Docx2txtLoader(file_path)
    elif ext == ".csv":
        loader = CSVLoader(file_path)
    elif ext in [".txt", ".md"]:
        loader = TextLoader(file_path)
    else:
        raise ValueError(f"Unsupported file format: {ext}")

    docs = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    splits = text_splitter.split_documents(docs)

    hf_embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': False}
    )

    Chroma.from_documents(
        documents=splits, 
        embedding=hf_embeddings,
        persist_directory="./chroma_db"
    )
    print(f"Successfully added {file_path} to Vector DB!")

if __name__ == "__main__":
    # ingest_file("sample.pdf")
    pass