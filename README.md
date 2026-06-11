# SEC Knowledge Graph RAG Explorer

<img width="990" height="827" alt="image" src="https://github.com/user-attachments/assets/8ecb431b-bd9e-4e51-9bf1-64f364477e98" />

---

This is an production ready Knowledge Graph RAG (Retrieval Augmented Generation) system built to parse, model, and analyze interconnected corporate risk factors across SEC 10-K filings using **LlamaIndex**, **Neo4j AuraDB**, and **Groq (Llama 3.3 70B)**.

Unlike traditional Vector RAG setups that isolate information into independent text chunks, this architecture maps semantic relationships into a Graph Database, enabling **multi-hop reasoning** and revealing systemic single points of failure across corporate supply chains.

## 🏗️ System Architecture

The pipeline processes unstructured SEC 10-K documents through three distinct engineering phases:

1. **Ingestion & Extraction:** Unstructured PDF/Text filings are parsed and chunked. Entities and semantic relationships are extracted via an asynchronous pipeline using an LLM.
2. **Graph Modeling (Neo4j AuraDB):** Extracted nodes (Companies, Suppliers, Regulations, Financial Impacts) and edges (Relationships, Dependencies) are pushed to a cloud Neo4j instance.
3. **Deterministic Hybrid Inference:** A Streamlit web interface communicates with the graph. User queries trigger a hybrid vector-and-graph retrieval pattern, feeding structured sub-graphs into a flagship Llama-3.3-70B model.

### Database Visualization
Below is a structural view of the compiled Knowledge Graph inside Neo4j AuraDB, illustrating the complex, multi-layered dependencies between companies, their operational jurisdictions, and global supply chains.

<img width="755" height="473" alt="image" src="https://github.com/user-attachments/assets/26848681-8fd0-40e7-8061-d511e2470d9a" />

<img width="537" height="507" alt="image" src="https://github.com/user-attachments/assets/beaf194f-276c-49e4-997e-9edbc73d8461" />

---

## 🛠️ Key Engineering Features Solved

### 1. Eliminating Parametric Hallucinations
Standard LLMs tend to pull outside knowledge or hallucinate entities when asked broad compliance questions. This system implements an absolute boundary condition via a custom **System Prompt Noise Filter** and strict context fencing (`temperature=0.0`). The model is algorithmically prohibited from outputting secondary entities (like law firms or previous companies listed in executive biographies) that naturally pollute unstructured financial documents.

### 2. Multi-Hop Dependency Resolution
Standard Vector RAG completely misses scenarios where Entity A is connected to Entity C solely through an intermediate Entity B. By leveraging structural paths inside Neo4j, this system executes multi-hop traversal effortlessly.

**Example Production Query:**
> *"In what ways do export controls on AI hardware create a cascading negative impact on cloud service providers (CSPs) and downstream customers?"*

Instead of matching raw keywords, the engine maps:
`Export Controls` ➔ `Restricts Hardware` ➔ `NVIDIA Distribution` ➔ `Impacts Infrastructure` ➔ `Cloud Service Providers`


---

## 🚀 Technical Stack

* **Orchestration & Data Framework:** LlamaIndex
* **Graph Database:** Neo4j AuraDB (Cloud)
* **Embedding Model:** `BAAI/bge-small-en-v1.5` via HuggingFace
* **Inference Engine:** Groq Cloud (`llama-3.3-70b-versatile`)
* **Frontend UI:** Streamlit Framework

---
