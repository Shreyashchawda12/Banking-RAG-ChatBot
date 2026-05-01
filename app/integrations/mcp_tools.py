class MCPTools:
    """
    Minimal MCP-style tool wrapper.
    These functions represent external actions.
    """

    def __init__(self, token_store):
        self.token_store = token_store

    def send_gmail_confirmation(self, user_id: str, message: str):
        token = self.token_store.get_token(user_id, "google")

        if not token:
            return {
                "success": False,
                "message": "Google account not connected."
            }

        return {
            "success": True,
            "message": f"Gmail confirmation sent: {message}"
        }

    def create_calendar_event(self, user_id: str, title: str):
        token = self.token_store.get_token(user_id, "google")

        if not token:
            return {
                "success": False,
                "message": "Google Calendar not connected."
            }

        return {
            "success": True,
            "message": f"Calendar event created: {title}"
        }

    def send_slack_alert(self, user_id: str, message: str):
        token = self.token_store.get_token(user_id, "slack")

        if not token:
            return {
                "success": False,
                "message": "Slack account not connected."
            }

        return {
            "success": True,
            "message": f"Slack alert sent: {message}"
        }