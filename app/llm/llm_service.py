import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

class LLMService:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found.")
        self.llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            api_key=os.getenv("GROQ_API_KEY")
        )

    def generate_response(self, query, context):
        prompt = f"""
        You are a banking assistant.

        User Query:
        {query}

        Context:
        {context}

        Provide a clear and concise answer.
        """

        response = self.llm.invoke(prompt)
        return response.content