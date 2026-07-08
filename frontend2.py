import os
import uuid
import logging
import streamlit as st
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# --- IMPORT THE AGENT ---
from main import app 

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Sealine AI Travel", page_icon="✈️", layout="centered")

load_dotenv()

# --- STYLISH CSS (GLASSMORPHISM) ---
st.markdown("""
<style>
    /* Clean up the top padding */
    .block-container {
        padding-top: 3rem;
        padding-bottom: 3rem;
    }
    
    /* Global Background Image with Dark Overlay */
    .stApp {
        background-image: linear-gradient(rgba(14, 17, 23, 0.85), rgba(14, 17, 23, 0.85)), url("https://images.unsplash.com/photo-1499856871958-5b9627545d1a?q=80&w=2560&auto=format&fit=crop");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    
    /* Ensure all text is bright white and highly readable */
    p, li, span, h1, h2, h3 {
        color: #ffffff !important;
        text-shadow: 0px 2px 4px rgba(0,0,0,0.9) !important;
        font-weight: 500;
    }

    /* Make the info box (welcome screen) have a dark, translucent background */
    div[data-testid="stAlert"] {
        background-color: rgba(0, 0, 0, 0.6) !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
    }

    /* Style headers for clarity */
    .main-title {
        text-align: center;
        font-weight: 800;
        font-size: 3rem;
        margin-bottom: 0.5rem;
        color: #ffffff;
        text-shadow: 0px 2px 10px rgba(0,0,0,0.5); 
    }
    .sub-title {
        text-align: center;
        color: #b0bec5;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR CONTROL PANEL ---
with st.sidebar:
    st.title("🛠️ Session Controls")
    # Generate a unique thread ID for the session if it doesn't exist
    if "thread_id" not in st.session_state:
        st.session_state.thread_id = str(uuid.uuid4())
        logger.info(f"Generated new session thread ID: {st.session_state.thread_id}")

    thread_input = st.text_input("Active Thread ID (Database Memory Key):", value=st.session_state.thread_id)
    st.session_state.thread_id = thread_input
    
    st.write("---")
    if st.button("🔄 Clear Current UI Chat Screen"):
        st.session_state.chat_history = []
        st.session_state.thread_id = str(uuid.uuid4())
        st.rerun()

# --- UI LAYOUT ---
st.markdown('<div class="main-title">Where to next?</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Chat with our autonomous agents to build and refine your perfect itinerary.</div>', unsafe_allow_html=True)

# --- MULTI-USER / CONVERSATIONAL SESSION STATE ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- RENDER THE CONVERSATION HISTORY ---
if not st.session_state.chat_history:
    st.info("👋 **Welcome to Sealine AI!** I am your autonomous travel planner.\n\nTry asking me to:\n- *Plan a 3-day romantic getaway to Paris*\n- *Find cheap flights to Tokyo next month*\n- *Build a budget-friendly itinerary for Rome*")
else:
    for role, text in st.session_state.chat_history:
        if role == "user":
            with st.chat_message("user", avatar="👤"):
                st.markdown(text)
        elif role == "assistant":
            with st.chat_message("assistant", avatar="✈️"):
                st.markdown(text)

# --- THE LIVE CHAT INTERFACE ---
# Pass the stable thread ID to the LangGraph runtime state configuration dict
config = {
    "configurable": {"thread_id": st.session_state.thread_id},
    "recursion_limit": 30
}

if prompt := st.chat_input("e.g., Plan a 3-day trip from NYC to London for 2 adults..."):
    
    # 1. Render user prompt instantly in the UI
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)
    
    # 2. Save it to Streamlit's local UI cache
    st.session_state.chat_history.append(("user", prompt))
    logger.info(f"User [{st.session_state.thread_id}] input: {prompt}")
    
    # 3. Process through the LangGraph Agent
    with st.chat_message("assistant", avatar="✈️"):
        status = st.status("Thinking...", expanded=True)
        try:
            # We use stream instead of invoke to capture intermediate tool calls
            for event in app.stream({"messages": [HumanMessage(content=prompt)]}, config=config, stream_mode="values"):
                last_msg = event["messages"][-1]
                
                # Check if the agent decided to call a tool
                if last_msg.type == "ai" and getattr(last_msg, "tool_calls", None):
                    for tc in last_msg.tool_calls:
                        status.write(f"🔍 Agent is using tool: `{tc['name']}`")
                        
            status.update(label="Finished planning!", state="complete", expanded=False)
            
            # The final state will contain the complete history
            final_answer = event["messages"][-1].content
            
            # Render the final comprehensive markdown payload
            st.markdown(final_answer)
            
            # Save the AI's response to Streamlit's local UI cache
            st.session_state.chat_history.append(("assistant", final_answer))
            logger.info(f"Agent [{st.session_state.thread_id}] successfully responded.")
            
        except Exception as e:
            logger.error(f"Error during agent invocation: {e}", exc_info=True)
            st.error(f"An error occurred while routing your request: {e}")