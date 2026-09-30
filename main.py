import os
import shutil
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from langchain_core.messages import HumanMessage

load_dotenv() 

from agent import get_agent
from ingest import ingest_file

app = FastAPI(title="Multi-User Agentic RAG API", version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

agent = get_agent()

class ChatRequest(BaseModel):
    message: str
    session_id: str = "default_user" # This acts as the unique User ID

@app.get("/")
async def serve_chat_interface():
    """Serves the main chat interface on the home page."""
    return FileResponse("ai_chatbot_interface.html")

@app.get("/upload-page")
async def serve_upload_interface():
    """Serves the file upload window."""
    return FileResponse("upload_window.html")

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """Handles multi-user chat and routes it through the AI agent."""
    user_message = request.message
    thread_id = request.session_id

    try:
        # 1. We tell LangGraph WHICH user is talking using the thread_id
        config = {"configurable": {"thread_id": thread_id}}
        
        # 2. We only send the NEW message. The checkpointer automatically 
        # fetches all previous short-term and long-term memory for this thread_id.
        response_state = agent.invoke(
            {"messages": [HumanMessage(content=user_message)]},
            config=config
        )
        
        # 3. Extract the final response
        final_message = response_state["messages"][-1]
        
        return {"response": final_message.content}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """Handles file uploads (PDF, DOCX, CSV, TXT) and ingests them into ChromaDB."""
    allowed_extensions = [".pdf", ".docx", ".csv", ".txt", ".md"]
    ext = os.path.splitext(file.filename)[1].lower()
    
    if ext not in allowed_extensions:
        raise HTTPException(status_code=400, detail="Unsupported file format.")

    # Save the uploaded file temporarily
    temp_file_path = f"temp_{file.filename}"
    try:
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Run the fast ingestion script
        ingest_file(temp_file_path)
        
        return {"status": "success", "message": f"Successfully ingested {file.filename}"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        # Clean up the temporary file after ingestion
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

@app.get("/health")
def health_check():
    return {"status": "Running"}