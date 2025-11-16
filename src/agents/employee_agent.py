# src/agents/employee_agent.py
from src.llm.client import chat
from src.db.travel_queries import get_user_details, fetch_flights, fetch_eligible_hotels, create_travel_indent
from src.agents.milvus import setup_milvus, query_policy

class EmployeeAgent:
    def __init__(self, user, sessions):
        self.user = user
        self.sessions = sessions
        self.milvus_collection = setup_milvus()  # load Milvus

    def _get_session(self):
        return self.sessions.setdefault(self.user["employee_id"], {"step":"start", "collected": {}, "pending_intent": None})

    def handle_message(self, message: str):
        sess = self._get_session()
        # --- greeting check ---
        greetings = ["hi", "hello", "hey", "greetings", "good morning", "good afternoon", "good evening"]
        if message.strip().lower() in greetings:
            prompt = f"You are a helpful travel assistant. Respond conversationally to the user's greeting: '{message}'."
            answer = chat(prompt)
            return {"message": answer}
        # --- RAG check ---
        if "policy" in message.lower() or "rule" in message.lower():
            context = query_policy(message, self.milvus_collection)
            prompt = f"Answer the user's question based on the travel policy:\n{context}\n\nUser Question: {message}"
            answer = chat(prompt)
            return {"message": answer}

        # --- existing multi-turn travel booking ---
        if sess["step"] == "start":
            prompt = f"Extract source_city, destination_city, start_date (YYYY-MM-DD), end_date (YYYY-MM-DD), purpose from: {message}. Return JSON."
            resp = chat(prompt)
            import json
            try:
                parsed = json.loads(resp)
            except Exception:
                sess["step"] = "awaiting_details"
                return {"ask":"Please provide source, destination, start_date, end_date, and purpose."}
            sess["collected"].update(parsed)
            sess["step"] = "show_options"
            flights = fetch_flights(parsed.get("source_city"), parsed.get("destination_city"), parsed.get("start_date"))
            hotels = fetch_eligible_hotels(self.user.get("grade"), parsed.get("destination_city"))
            sess["pending_intent"] = {"intent": parsed, "flights": flights, "hotels": hotels}
            return {"intent": parsed, "flights": flights, "hotels": hotels}

    def extract_intent(self, message):
        prompt = f"""{message}\n\nExtract JSON with keys: source_city, destination_city, start_date (YYYY-MM-DD), end_date (YYYY-MM-DD), purpose, total_days. If missing fields, return JSON with key 'ask' containing question."""
        resp = chat(prompt)
        # Attempt to parse JSON out of the response
        import json
        try:
            parsed = json.loads(resp)
            return parsed
        except Exception:
            # If LLM didn't return JSON use rag to ask clarifying Q
            return {"ask": "I couldn't parse dates/places. Please give source, destination, start_date (YYYY-MM-DD), end_date, and purpose."}

    def plan_travel(self, employee_id, message, session):
        user = get_user_details(employee_id)
        intent = self.extract_intent(message)
        if "ask" in intent:
            return {"ask": intent["ask"]}
        # fetch flights/hotels
        flights = fetch_flights(intent["source_city"], intent["destination_city"], intent.get("start_date"))
        hotels = fetch_eligible_hotels(user["grade"], intent["destination_city"])
        # Put in session
        session["pending_intent"] = {"intent": intent, "flights": flights, "hotels": hotels}
        return {"intent": intent, "flights": flights, "hotels": hotels}

    def confirm_and_create(self, employee_id, session):
        if not session.get("pending_intent"):
            return {"error":"No pending intent"}
        p = session["pending_intent"]
        # choose first options by default
        flight = p["flights"][0]
        hotel = p["hotels"][0]
        indent_id = create_travel_indent(employee_id, p["intent"], flight, hotel)
        return {"message":"Ticket created","indent_id":indent_id}
