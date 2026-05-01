import os
from cryptography.fernet import Fernet
from dotenv import load_dotenv

load_dotenv()


class TokenStore:
    """
    Minimal encrypted per-user token storage.
    For production, replace in-memory dict with PostgreSQL.
    """

    def __init__(self):
        key = os.getenv("ENCRYPTION_KEY")
        if not key:
            raise ValueError("ENCRYPTION_KEY missing in .env")

        self.cipher = Fernet(key.encode())
        self.tokens = {}

    def save_token(self, user_id: str, service: str, token: str):
        encrypted_token = self.cipher.encrypt(token.encode()).decode()

        self.tokens[(user_id, service)] = encrypted_token

    def get_token(self, user_id: str, service: str):
        encrypted_token = self.tokens.get((user_id, service))

        if not encrypted_token:
            return None

        return self.cipher.decrypt(encrypted_token.encode()).decode()

    def disconnect(self, user_id: str, service: str):
        self.tokens.pop((user_id, service), None)

    def is_connected(self, user_id: str, service: str) -> bool:
        return (user_id, service) in self.tokens