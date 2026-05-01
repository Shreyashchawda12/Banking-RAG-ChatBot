import requests
import streamlit as st

API_BASE_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Banking RAG Chatbot",
    page_icon="🏦",
    layout="wide"
)

st.title("🏦 Banking Multi-Agent RAG Chatbot")

page = st.sidebar.radio(
    "Navigation",
    ["Chat", "Upload Files", "Agent Activity", "Integrations"]
)

# -------------------------
# Upload Files Page
# -------------------------
if page == "Upload Files":
    st.header("📁 File Upload & Management")

    uploaded_file = st.file_uploader(
        "Upload CSV or Excel file",
        type=["csv", "xlsx"]
    )

    if uploaded_file is not None:

        # 🔥 File validation (MANDATORY)
        if not uploaded_file.name.endswith((".csv", ".xlsx")):
            st.error("❌ Only CSV and Excel files are allowed.")
            st.stop()

        st.success(f"Selected file: {uploaded_file.name}")

        if st.button("Upload and Index"):
            files = {
                "file": (
                    uploaded_file.name,
                    uploaded_file.getvalue(),
                    uploaded_file.type
                )
            }

            with st.spinner("Uploading and indexing file..."):
                try:
                    response = requests.post(
                        f"{API_BASE_URL}/upload",
                        files=files,
                        timeout=60
                    )

                    if response.status_code == 200:
                        st.success("✅ File uploaded and indexed successfully.")
                        st.json(response.json())
                    else:
                        st.error(response.text)

                except requests.exceptions.ConnectionError:
                    st.error("FastAPI backend is not running.")

# -------------------------
# Chat Page
# -------------------------
elif page == "Chat":
    st.header("💬 Chat with Banking Data")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    user_query = st.chat_input("Ask a banking question...")

    if user_query:
        st.session_state.messages.append(
            {"role": "user", "content": user_query}
        )

        with st.chat_message("user"):
            st.write(user_query)

        with st.chat_message("assistant"):
            with st.spinner("🤖 Agent is processing..."):
                try:
                    response = requests.post(
                        f"{API_BASE_URL}/chat",
                        json={"query": user_query},
                        timeout=60
                    )

                    if response.status_code == 200:
                        answer = response.json()["answer"]
                        st.write(answer)

                        st.session_state.messages.append(
                            {"role": "assistant", "content": answer}
                        )
                    else:
                        st.error(response.text)

                except requests.exceptions.ConnectionError:
                    st.error("FastAPI backend is not running.")

    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# -------------------------
# Agent Activity Page
# -------------------------
elif page == "Agent Activity":
    st.header("📊 Agent Activity Log")

    try:
        response = requests.get(
            f"{API_BASE_URL}/logs",
            timeout=20
        )

        if response.status_code == 200:
            logs = response.json()

            if logs:
                st.table(logs)
            else:
                st.info("No activity logs yet.")

        else:
            st.error("Failed to fetch logs.")

    except requests.exceptions.ConnectionError:
        st.error("FastAPI backend is not running.")

# -------------------------
# Integrations Page
# -------------------------
elif page == "Integrations":
    st.header("🔌 MCP / OAuth2 Integrations")

    try:
        status_response = requests.get(
            f"{API_BASE_URL}/integrations/status",
            timeout=20
        )

        if status_response.status_code == 200:
            status = status_response.json()
        else:
            status = {"google": False, "slack": False}

    except requests.exceptions.ConnectionError:
        st.error("FastAPI backend is not running.")
        status = {"google": False, "slack": False}

    col1, col2, col3 = st.columns(3)

    # Google
    with col1:
        st.subheader("Google")

        if status.get("google"):
            st.success("Connected")
        else:
            st.warning("Disconnected")

        if st.button("Connect Google"):
            try:
                response = requests.get(
                    f"{API_BASE_URL}/oauth/google/connect"
                )
                auth_url = response.json()["auth_url"]
                st.markdown(f"[Click here to connect Google]({auth_url})")

            except:
                st.error("Backend not running.")

        if st.button("Test Gmail"):
            res = requests.post(f"{API_BASE_URL}/mcp/test-gmail")
            st.json(res.json())

        if st.button("Test Calendar"):
            res = requests.post(f"{API_BASE_URL}/mcp/test-calendar")
            st.json(res.json())

    # Slack
    with col2:
        st.subheader("Slack")

        if status.get("slack"):
            st.success("Connected")
        else:
            st.warning("Disconnected")

        if st.button("Connect Slack"):
            response = requests.get(f"{API_BASE_URL}/oauth/slack/connect")
            auth_url = response.json()["auth_url"]
            st.markdown(f"[Click here to connect Slack]({auth_url})")

        if st.button("Test Slack"):
            res = requests.post(f"{API_BASE_URL}/mcp/test-slack")
            st.json(res.json())

    # Status
    with col3:
        st.subheader("Status")
        st.json(status)