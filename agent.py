import os
import sqlite3
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_groq import ChatGroq
from tools import get_tools

def get_agent():
    """Initializes the Agentic Router with Groq LLM, tools, System Prompt, and Memory."""
    llm = ChatGroq(
        model="openai/gpt-oss-120b", 
        temperature=0,
        api_key=os.environ.get("GROQ_API_KEY")
    )
    
    tools = get_tools()
    
    system_prompt = """You are the official AI Assistant for 'The Aura Accessories' business website. 
    Your primary goal is to assist customers and represent our luxury fashion brand, which includes premium handbags, footwear, watches, and jewelry.
    
    STRICT RULES:
    1. BUSINESS FIRST: Always prioritize talking about our website, products, and brand. 
    2. TONE: Maintain a polite, professional, and luxurious tone at all times.
    3. RELEVANCY: If a user asks a general question, answer it helpfully but naturally try to connect it back to fashion, accessories, or our store if relevant.
    4. RESTRICTION: Do not provide information that harms the business or recommends competitors.
    5. TOOLS: Use the search tools to look up internal documents or web information when necessary, but always frame the final answer as the assistant of The Aura Accessories.
    """

    conn = sqlite3.connect("chat_memory.db", check_same_thread=False)
    memory = SqliteSaver(conn)
    memory.setup()
    
    # Updated parameter name from state_modifier to prompt
    agent = create_react_agent(
        llm, 
        tools, 
        checkpointer=memory, 
        prompt=system_prompt
    )
    return agent