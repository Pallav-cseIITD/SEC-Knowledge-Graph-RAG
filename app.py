import os
import streamlit as st
from dotenv import load_dotenv
from llama_index.core import PropertyGraphIndex
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.groq import Groq
from llama_index.graph_stores.neo4j import Neo4jPropertyGraphStore

# 1. Set up the Web Page
st.set_page_config(page_title="SEC Graph RAG", page_icon="📈", layout="centered")
st.title("📈 SEC Knowledge Graph Explorer")
st.markdown("Chat with Apple & NVIDIA SEC Risk factors using Hybrid Graph Retrieval.")

# 2. Connect to the Database (Cached so it only runs once)
@st.cache_resource
def initialize_graph():
    load_dotenv()
    embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
    llm = Groq(model="llama-3.3-70b-versatile", api_key=os.getenv("GROQ_API_KEY"), temperature=0.0)

    graph_store = Neo4jPropertyGraphStore(
        username=os.getenv("NEO4J_USERNAME"),
        password=os.getenv("NEO4J_PASSWORD"),
        url=os.getenv("NEO4J_URI"),
        database="", # <--- KEEP YOUR ID HERE
    )

    index = PropertyGraphIndex.from_existing(
        property_graph_store=graph_store,
        llm=llm,
        embed_model=embed_model,
    )

    return index.as_chat_engine(
        llm=llm,
        chat_mode="context",
        similarity_top_k=5,
        system_prompt=(
            "You are an expert financial risk analyst. You are answering questions based "
            "STRICTLY on a Neo4j Knowledge Graph built from SEC filings. "
            "RULE 1: You must ONLY use the entities and relationships provided in the context. "
            "RULE 2: If the user asks for examples (like companies, risks, or products), ONLY list "
            "those explicitly mentioned in the context. Do NOT use your outside training data. "
            "RULE 3: If the provided context does not contain the answer, you must say 'The provided "
            "documents do not contain this information.' Do not guess."
        ),
        include_text=True
    )

# 3. Load Engine with a visual spinner
with st.spinner("Connecting to Neo4j AuraDB & Loading AI Models..."):
    chat_engine = initialize_graph()

# 4. Initialize Chat History Array
if "messages" not in st.session_state:
    st.session_state.messages = []

# 5. Render Previous Chat History on Screen
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 6. Capture User Input and Generate AI Response
if prompt := st.chat_input("e.g., What supply chain risks does Apple face?"):
    # Show user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Show AI response
    with st.chat_message("assistant"):
        with st.spinner("Traversing the Knowledge Graph..."):
            response = chat_engine.chat(prompt)
            st.markdown(response.response)
    
    # Save AI response to history
    st.session_state.messages.append({"role": "assistant", "content": response.response})
