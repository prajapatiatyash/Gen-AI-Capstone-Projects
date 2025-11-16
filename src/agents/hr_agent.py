# src/agents/hr_agent.py
from src.db.travel_queries import get_pending_hr_tickets, get_employee_by_indent, approve_hr_ticket, book_flight, book_hotel

class HRAgent:
    def __init__(self, user, sessions):
        self.user = user
        self.sessions = sessions

    def handle_message(self, message: str):
        text = message.strip().lower()
        if "list" in text and "pending" in text:
            return get_pending_hr_tickets()
        if text.startswith("details"):
            parts = message.split()
            if len(parts) >= 2:
                indent = parts[1].strip()
                return get_employee_by_indent(indent)
            return {"error":"usage: details <INDENT_ID>"}
        if text.startswith("approve"):
            parts = message.split()
            if len(parts) >= 2:
                indent = parts[1].strip()
                approve_hr_ticket(indent, self.user["employee_id"])
                # do booking as follow-up
                flight = book_flight(indent)
                hotel = book_hotel(indent)
                return {"message":"Approved & Booked", "flight": flight, "hotel": hotel}
            return {"error":"usage: approve <INDENT_ID>"}
        return {"help":"Commands: 'list pending', 'details <INDENT>', 'approve <INDENT>'"}
