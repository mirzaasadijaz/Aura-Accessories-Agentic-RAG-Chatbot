import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_community.tools.tavily_search import TavilySearchResults

# Import the core Tool class instead of the buggy helper function
from langchain_core.tools import Tool 

def get_tools():
    """Initializes and returns the internal and external search tools."""
    tools_list = []
    
    if os.path.exists("./chroma_db"):
        # Use the exact same local model used during ingestion
        hf_embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': False}
        )
        
        vectorstore = Chroma(
            persist_directory="./chroma_db", 
            embedding_function=hf_embeddings
        )
        retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
        
        # Manually create the tool to bypass all import errors
        vector_tool = Tool(
            name="search_internal_docs",
            description="Use this tool to search internal company documents, manuals, and policies. Input should be a search query.",
            func=lambda query: retriever.invoke(query)
        )
        tools_list.append(vector_tool)
    else:
        print("Warning: ./chroma_db not found. Agent will only use web search.")

    web_tool = TavilySearchResults(max_results=3, include_answer=True)
    tools_list.append(web_tool)
    
    return tools_list