import os
import uuid
import requests
from urllib.parse import urlencode
from dotenv import load_dotenv

load_dotenv()


class OAuthService:
    """
    Minimal OAuth URL generation and callback token exchange.
    """

    def __init__(self, token_store):
        self.token_store = token_store
        self.oauth_states = {}

    def create_google_auth_url(self, user_id: str):
        state = str(uuid.uuid4())
        self.oauth_states[state] = user_id

        params = {
            "client_id": os.getenv("GOOGLE_CLIENT_ID"),
            "redirect_uri": os.getenv("GOOGLE_REDIRECT_URI"),
            "response_type": "code",
            "scope": (
                "https://www.googleapis.com/auth/gmail.send "
                "https://www.googleapis.com/auth/calendar.events"
            ),
            "access_type": "offline",
            "prompt": "consent",
            "state": state,
        }

        return "https://accounts.google.com/o/oauth2/v2/auth?" + urlencode(params)

    def exchange_google_code(self, code: str, state: str):
        user_id = self.oauth_states.get(state)

        if not user_id:
            raise ValueError("Invalid OAuth state")

        response = requests.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": code,
                "client_id": os.getenv("GOOGLE_CLIENT_ID"),
                "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
                "redirect_uri": os.getenv("GOOGLE_REDIRECT_URI"),
                "grant_type": "authorization_code",
            },
            timeout=20,
        )

        token_data = response.json()
        access_token = token_data.get("access_token")

        if not access_token:
            raise ValueError(f"Google token exchange failed: {token_data}")

        self.token_store.save_token(user_id, "google", access_token)
        return user_id

    def create_slack_auth_url(self, user_id: str):
        state = str(uuid.uuid4())
        self.oauth_states[state] = user_id

        params = {
            "client_id": os.getenv("SLACK_CLIENT_ID"),
            "scope": "chat:write",
            "redirect_uri": os.getenv("SLACK_REDIRECT_URI"),
            "state": state,
        }

        return "https://slack.com/oauth/v2/authorize?" + urlencode(params)

    def exchange_slack_code(self, code: str, state: str):
        user_id = self.oauth_states.get(state)

        if not user_id:
            raise ValueError("Invalid OAuth state")

        response = requests.post(
            "https://slack.com/api/oauth.v2.access",
            data={
                "code": code,
                "client_id": os.getenv("SLACK_CLIENT_ID"),
                "client_secret": os.getenv("SLACK_CLIENT_SECRET"),
                "redirect_uri": os.getenv("SLACK_REDIRECT_URI"),
            },
            timeout=20,
        )

        token_data = response.json()
        access_token = token_data.get("access_token")

        if not access_token:
            raise ValueError(f"Slack token exchange failed: {token_data}")

        self.token_store.save_token(user_id, "slack", access_token)
        return user_id