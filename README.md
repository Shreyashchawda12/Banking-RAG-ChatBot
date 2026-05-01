# 🏦 Banking Multi-Agent RAG Chatbot

A production-ready **AI-powered banking assistant** built using **LangGraph, RAG, DuckDB, and MCP integrations (Gmail, Slack, Calendar)**.

This system combines **LLM reasoning + SQL accuracy + real-world tool integrations** to deliver reliable banking insights.

---

## 🚀 Features

### 💬 Chat with Banking Data
- Ask natural language questions
- Multi-turn conversation support
- Context-aware responses

---

### 📊 Hybrid RAG + SQL Intelligence
- **RAG (Vector Search)** → descriptive queries  
- **DuckDB SQL** → accurate aggregation  

**Examples:**
- "Show my transactions" → RAG  
- "Total amount spent" → SQL  

---

### 🧠 Multi-Agent Architecture (LangGraph)

Agents used:

- 🔍 **Lookup Agent** → retrieves data from vector DB  
- 📈 **Aggregation Agent** → executes SQL queries  
- 🤖 **LLM Agent** → generates responses  
- 🔌 **Tool Agent** → Gmail, Slack, Calendar  

---

### 🔌 MCP Tool Integrations

| Tool | Action |
|------|------|
| Gmail | Send confirmation emails |
| Calendar | Schedule meetings |
| Slack | Send alerts |

---

### 🔐 OAuth2 Authentication

- Google (Gmail + Calendar)
- Slack OAuth
- Secure token storage
- Multi-user support

---

### 📂 File Upload Support

Supports only:
- `.csv`
- `.xlsx`

Automatically:
- Parses data
- Creates embeddings
- Enables querying

---

### 📜 Agent Activity Tracking

- Logs agent execution
- Shows tool usage
- Improves explainability

---

## 🏗️ Architecture



---

## 🧩 Tech Stack

| Layer | Technology |
|------|----------|
| Frontend | Streamlit |
| Backend | FastAPI |
| Orchestration | LangGraph |
| LLM | OpenAI / Groq |
| Vector DB | Chroma / FAISS |
| SQL Engine | DuckDB |
| Auth | OAuth2 |
| Integrations | Gmail, Slack, Calendar |

---

## ⚙️ Setup Instructions

### 1️ Clone Repo

```bash
git clone https://github.com/your-username/banking-rag-chatbot.git
cd banking-rag-chatbot
```

### 2 Clone Repo

```bash
uv venv
uv pip install -r requirements.txt
```
### 4 Run Backend (FastAPI)
```bash
uv run uvicorn app.main:app --reload
```
👉 Runs at:
http://127.0.0.1:8000

### 4 Run Frontend (Streamlit)
```bash
uv run streamlit run streamlit_app.py
```
