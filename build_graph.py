import os
import time
import math
from dotenv import load_dotenv
from llama_index.core import SimpleDirectoryReader, PropertyGraphIndex
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.groq import Groq
from llama_index.graph_stores.neo4j import Neo4jPropertyGraphStore

# 1. Load configuration
load_dotenv()

print("Initializing Local Embedding Model and Groq LLM...")
embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
llm = Groq(model="llama-3.1-8b-instant", api_key=os.getenv("GROQ_API_KEY"))

# 2. Connect to Neo4j
print("Connecting to Neo4j AuraDB...")
graph_store = Neo4jPropertyGraphStore(
    username=os.getenv("NEO4J_USERNAME"),
    password=os.getenv("NEO4J_PASSWORD"),
    url=os.getenv("NEO4J_URI"),
    database="",  # <--- KEEP YOUR EXACT ID HERE
    refresh_schema=False                           
)

# 3. Read Documents
print("Reading SEC documents...")
documents = SimpleDirectoryReader("./cleaned_data").load_data()

# 4. Manually Chunk the Text (Data Engineering!)
print("Chunking text for batch processing...")
splitter = SentenceSplitter(chunk_size=1024, chunk_overlap=100)
nodes = splitter.get_nodes_from_documents(documents)
total_nodes = len(nodes)
print(f"Total chunks created: {total_nodes}")

# 5. Initialize the Graph Index (Empty at first)
index = PropertyGraphIndex(
    nodes=[], 
    property_graph_store=graph_store,
    llm=llm,
    embed_model=embed_model,
    show_progress=True
)

# ---------------------------------------------------------
# THE THROTTLE PIPELINE (Bypasses API Limits)
# ---------------------------------------------------------
BATCH_SIZE = 4  # 4 chunks = ~4000 tokens (Safely under the 6000 limit)
WAIT_TIME = 62  # Wait 62 seconds to fully clear the Groq minute-timer

total_batches = math.ceil(total_nodes / BATCH_SIZE)

print(f"\n🚀 Beginning Extraction Pipeline ({total_batches} total batches).")
print("Go grab a coffee—this will run safely in the background.")
print("-" * 50)

for i in range(0, total_nodes, BATCH_SIZE):
    batch = nodes[i : i + BATCH_SIZE]
    current_batch = (i // BATCH_SIZE) + 1
    
    print(f"\n⚙️ Processing Batch {current_batch} of {total_batches}...")
    
    # Insert the batch into Neo4j
    index.insert_nodes(batch)
    
    # If there are still more nodes to process, sleep!
    if i + BATCH_SIZE < total_nodes:
        print(f"⏳ Batch {current_batch} complete. Sleeping for {WAIT_TIME} seconds to reset Groq limits...")
        time.sleep(WAIT_TIME)

print("\n Complete, un-truncated Knowledge Graph is built!")
