import os
import requests
from dotenv import load_dotenv

load_dotenv()

SLACK_TOKEN = os.getenv("SLACK_BOT_TOKEN")


def send_slack_message(channel: str, text: str):
    if not SLACK_TOKEN:
        return {
            "ok": False,
            "error": "SLACK_BOT_TOKEN not found in .env"
        }

    url = "https://slack.com/api/chat.postMessage"

    headers = {
        "Authorization": f"Bearer {SLACK_TOKEN}",
        "Content-Type": "application/json; charset=utf-8"
    }

    data = {
        "channel": channel,
        "text": text
    }

    response = requests.post(
        url,
        json=data,
        headers=headers,
        timeout=20
    )

    return response.json()