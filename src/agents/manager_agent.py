# src/agents/manager_agent.py
from src.db.travel_queries import get_pending_manager_tickets, get_indent_details, approve_manager_ticket, get_user_details

class ManagerAgent:
    def __init__(self, user, sessions):
        self.user = user
        self.sessions = sessions

    def handle_message(self, message: str):
        # simple commands: "list pending", "details TIXxxx", "approve TIXxxx"
        text = message.strip().lower()
        if "list" in text and "pending" in text:
            return get_pending_manager_tickets(self.user["employee_id"])
        if text.startswith("details"):
            # format: details TIX001
            parts = message.split()
            if len(parts) >= 2:
                indent_id = parts[1].strip()
                return get_indent_details(indent_id)
            return {"error":"usage: details <INDENT_ID>"}
        if text.startswith("approve"):
            parts = message.split()
            if len(parts) >= 2:
                indent_id = parts[1].strip()
                approve_manager_ticket(indent_id, self.user["employee_id"])
                return {"message":"Approved", "indent_id": indent_id}
            return {"error":"usage: approve <INDENT_ID>"}
        return {"help":"Commands: 'list pending', 'details <INDENT>', 'approve <INDENT>'"}
