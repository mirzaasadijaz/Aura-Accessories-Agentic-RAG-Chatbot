import streamlit as st
import os
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from agent import get_agent
from ingest import ingest_file # Import our new fast ingestion script

load_dotenv()

st.set_page_config(page_title="Agentic RAG Chatbot", page_icon="🤖", layout="wide")

# ---- SIDEBAR: FILE UPLOADER ----
with st.sidebar:
    st.header("📂 Upload Documents")
    st.write("Upload PDFs, Word docs, CSVs, or Text files.")
    
    uploaded_file = st.file_uploader(
        "Choose a file", 
        type=["pdf", "docx", "csv", "txt", "md"]
    )
    
    if uploaded_file is not None:
        if st.button("Process & Learn Data"):
            with st.spinner("Parsing and vectorizing..."):
                # Save file temporarily to disk
                temp_path = os.path.join(".", uploaded_file.name)
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                # Run the fast ingestion
                try:
                    ingest_file(temp_path)
                    st.success(f"Learned: {uploaded_file.name}")
                except Exception as e:
                    st.error(f"Error: {e}")
                finally:
                    # Clean up the temporary file
                    if os.path.exists(temp_path):
                        os.remove(temp_path)

# ---- MAIN CHAT INTERFACE ----
st.title("Enterprise AI: Hybrid Search")
st.markdown("Ask questions about your uploaded documents or search the live web.")

# Initialize the LangGraph agent
if "agent" not in st.session_state:
    st.session_state.agent = get_agent()

# Initialize chat history state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Re-render chat history
for msg in st.session_state.messages:
    role = "user" if isinstance(msg, HumanMessage) else "assistant"
    with st.chat_message(role):
        st.markdown(msg.content)

# Handle new user input
if prompt := st.chat_input("Ask a question..."):
    with st.chat_message("user"):
        st.markdown(prompt)
    
    user_msg = HumanMessage(content=prompt)
    st.session_state.messages.append(user_msg)
    
    with st.chat_message("assistant"):
        with st.spinner("Agent is routing and searching..."):
            response_state = st.session_state.agent.invoke(
                {"messages": st.session_state.messages}
            )
            final_message = response_state["messages"][-1]
            st.markdown(final_message.content)
            
    st.session_state.messages.append(final_message)