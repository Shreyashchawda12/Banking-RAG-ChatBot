import os
import shutil

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

from app.retrieval.vector_store import VectorStore
from app.database.duckdb_engine import DuckDBEngine
from app.ingestion.file_validator import FileValidator
from app.ingestion.parser import FileParser
from app.ingestion.chunker import DataChunker
from app.agents.graph import BankingRAGGraph

from app.integrations.token_store import TokenStore
from app.integrations.oauth_service import OAuthService
from app.integrations.mcp_tools import MCPTools
from datetime import datetime

activity_logs = []


def log_activity(agent: str, action: str, status: str):
    activity_logs.append({
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "agent": agent,
        "action": action,
        "status": status
    })

app = FastAPI(
    title="Banking Multi-Agent RAG Chatbot API",
    version="1.0.0"
)

UPLOAD_DIR = "artifacts/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# Core RAG objects
vector_store = VectorStore()
db_engine = DuckDBEngine()
rag_graph = BankingRAGGraph(vector_store, db_engine)


# Integration objects
token_store = TokenStore()
oauth_service = OAuthService(token_store)
mcp_tools = MCPTools(token_store)

DEFAULT_USER_ID = "demo_user"


class ChatRequest(BaseModel):
    query: str


class ChatResponse(BaseModel):
    answer: str


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "message": "Banking RAG API is running"
    }

@app.get("/logs")
def get_logs():
    return activity_logs[-20:]


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    validation = FileValidator.validate(file.filename)

    if not validation.is_valid:
        raise HTTPException(
            status_code=400,
            detail=validation.message
        )

    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    parsed_file = FileParser.parse(file_path)

    total_rows = 0
    total_tables = 0

    for table in parsed_file.tables:
        df = table.dataframe

        # 🔥 CRITICAL FIX 1: Normalize column names
        df.columns = df.columns.str.lower()

        # 🔥 CRITICAL FIX 2: Clean amount column
        if "amount" in df.columns:
            df["amount"] = (
                df["amount"]
                .astype(str)
                .str.replace(",", "")
                .str.replace("₹", "")
            )
            df["amount"] = df["amount"].astype(float)

        total_rows += len(df)
        total_tables += 1

        if validation.file_extension == ".csv":
            safe_table_name = "transactions"
        else:
            safe_table_name = table.table_name.replace(" ", "_").lower()

        # 🔥 CRITICAL FIX 3: Replace table (avoid duplicates)
        db_engine.register_table(safe_table_name, df)

        chunks = DataChunker.chunk_table(
            df=df,
            table_name=table.table_name,
            file_name=file.filename
        )

        vector_store.add_chunks(chunks)

    return {
        "status": "success",
        "file_name": file.filename,
        "tables_indexed": total_tables,
        "rows_indexed": total_rows,
        "message": "File uploaded and indexed successfully."
    }
def detect_intent(query: str):
    query = query.lower()

    if any(word in query for word in ["email", "mail", "gmail"]):
        return "gmail"

    if any(word in query for word in ["meeting", "schedule", "calendar"]):
        return "calendar"

    if any(word in query for word in ["slack", "alert", "notify"]):
        return "slack"

    return "rag"

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    query = request.query
    intent = detect_intent(query)

    # 🔹 Log intent detection
    log_activity("Intent Router", f"Detected intent: {intent}", "success")

    # -------------------------
    # Gmail Tool
    # -------------------------
    if intent == "gmail":
        try:
            result = mcp_tools.send_gmail_confirmation(
                DEFAULT_USER_ID,
                "Your banking request has been received."
            )

            log_activity("Gmail Tool", "Sent confirmation email", "success")

            return ChatResponse(
                answer="✅ Gmail confirmation sent successfully."
                if result["success"]
                else f"❌ Gmail failed: {result['message']}"
            )

        except Exception as e:
            log_activity("Gmail Tool", str(e), "failed")
            return ChatResponse(answer=f"❌ Gmail error: {str(e)}")

    # -------------------------
    # Calendar Tool
    # -------------------------
    elif intent == "calendar":
        try:
            result = mcp_tools.create_calendar_event(
                DEFAULT_USER_ID,
                "Banking Relationship Manager Call"
            )

            log_activity("Calendar Tool", "Meeting scheduled", "success")

            return ChatResponse(
                answer="✅ Meeting scheduled successfully."
                if result["success"]
                else f"❌ Calendar failed: {result['message']}"
            )

        except Exception as e:
            log_activity("Calendar Tool", str(e), "failed")
            return ChatResponse(answer=f"❌ Calendar error: {str(e)}")

    # -------------------------
    # Slack Tool
    # -------------------------
    elif intent == "slack":
        try:
            result = mcp_tools.send_slack_alert(
                DEFAULT_USER_ID,
                "High priority banking query received."
            )

            log_activity("Slack Tool", "Slack alert sent", "success")

            return ChatResponse(
                answer="✅ Slack alert sent successfully."
                if result["success"]
                else f"❌ Slack failed: {result['message']}"
            )

        except Exception as e:
            log_activity("Slack Tool", str(e), "failed")
            return ChatResponse(answer=f"❌ Slack error: {str(e)}")

    # -------------------------
    # RAG + Aggregation Flow
    # -------------------------
    else:
        try:
            result = rag_graph.invoke(query)

            log_activity("LangGraph RAG", "Processed banking query", "success")

            return ChatResponse(
                answer=result.get("answer", "No response generated.")
            )

        except Exception as e:
            print("LangGraph failed:", e)
            log_activity("LangGraph RAG", str(e), "failed")

            query_lower = query.lower()

            # 🔹 Aggregation fallback
            if any(word in query_lower for word in [
                "total", "sum", "average", "count",
                "top", "category", "breakdown"
            ]):
                fallback = rag_graph._aggregation_agent({
                    "query": query,
                    "query_type": "aggregation",
                    "context": [],
                    "answer": ""
                })

                log_activity("Fallback Aggregation", "Executed fallback SQL", "success")

                return ChatResponse(
                    answer=fallback.get("context", ["Error"])[0]
                )

            # 🔹 Lookup fallback
            fallback = rag_graph._lookup_agent({
                "query": query,
                "query_type": "lookup",
                "context": [],
                "answer": ""
            })

            log_activity("Fallback Lookup", "Executed fallback retrieval", "success")

            return ChatResponse(
                answer=" ".join(fallback.get("context", ["No data found"]))
            )
# -------------------------
# Google OAuth
# -------------------------

@app.get("/oauth/google/connect")
def connect_google():
    auth_url = oauth_service.create_google_auth_url(DEFAULT_USER_ID)
    return {"auth_url": auth_url}


@app.get("/oauth/google/callback")
def google_callback(code: str, state: str = ""):
    oauth_service.exchange_google_code(code, state)
    return RedirectResponse("http://localhost:8501")


# -------------------------
# Slack OAuth
# -------------------------

@app.get("/oauth/slack/connect")
def connect_slack():
    auth_url = oauth_service.create_slack_auth_url(DEFAULT_USER_ID)
    return {"auth_url": auth_url}


@app.get("/oauth/slack/callback")
def slack_callback(code: str, state: str):
    oauth_service.exchange_slack_code(code, state)
    return RedirectResponse("http://localhost:8501")


# -------------------------
# Integration Status
# -------------------------

@app.get("/integrations/status")
def integration_status():
    return {
        "google": token_store.is_connected(DEFAULT_USER_ID, "google"),
        "slack": token_store.is_connected(DEFAULT_USER_ID, "slack"),
    }


# -------------------------
# MCP Tool Test Endpoints
# -------------------------

@app.post("/mcp/test-gmail")
def test_gmail():
    return mcp_tools.send_gmail_confirmation(
        DEFAULT_USER_ID,
        "Your banking request has been received."
    )


@app.post("/mcp/test-calendar")
def test_calendar():
    return mcp_tools.create_calendar_event(
        DEFAULT_USER_ID,
        "Banking Relationship Manager Call"
    )


@app.post("/mcp/test-slack")
def test_slack():
    return mcp_tools.send_slack_alert(
        DEFAULT_USER_ID,
        "High priority banking query received."
    )