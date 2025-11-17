# streamlit_app/hr_ui.py

import streamlit as st
import requests
import json
from datetime import datetime
from typing import Dict, Any, Optional, List
# ═══════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════

API_BASE_URL = "http://localhost:8004"  # FastAPI backend URL

# ═══════════════════════════════════════════════════════════
# API HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════

def get_travel_indents_from_api() -> List[Dict]:
    """Get travel indents from backend API"""
    try:
        response = requests.get(f"{API_BASE_URL}/travel-indents", timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Failed to load travel indents: {str(e)}")
        return []

def get_chat_history(session_id: str) -> Dict:
    """Get chat history for a session"""
    try:
        response = requests.get(f"{API_BASE_URL}/sessions/{session_id}/history", timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Failed to load history: {str(e)}")
        return {"session_id": session_id, "messages": []}


def clear_chat_history(session_id: str) -> bool:
    """Clear chat history for a session"""
    try:
        response = requests.delete(f"{API_BASE_URL}/sessions/{session_id}", timeout=30)
        response.raise_for_status()
        return True
    except Exception as e:
        st.error(f"Failed to clear history: {str(e)}")
        return False


def call_chat_api(message: str, session_id: str, indent_id: str) -> Dict:
    """Call chat API with message and indent_id for context"""
    try:
        payload = {
            "message": message,
            "session_id": session_id,
            "indent_id": indent_id
        }
        
        response = requests.post(f"{API_BASE_URL}/chat", json=payload, timeout=90)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Chat API error: {str(e)}")
        return {"response": f"Error: {str(e)}", "session_id": session_id, "tools_used": [], "booking_complete": False}


def update_ticket_status_api(indent_id: str, new_status: str) -> bool:
    """Update ticket status via API"""
    try:
        response = requests.patch(
            f"{API_BASE_URL}/tickets/{indent_id}/status",
            json={"status": new_status},
            timeout=10
        )
        response.raise_for_status()
        return True
    except Exception as e:
        st.error(f"Failed to update ticket status: {str(e)}")
        return False


# ═══════════════════════════════════════════════════════════
# DATA MANAGEMENT
# ═══════════════════════════════════════════════════════════

def get_travel_data():
    """Get travel data from backend API"""
    if "travel_data" not in st.session_state or st.session_state.get("refresh_data", True):
        travel_indents = get_travel_indents_from_api()
        
        # Transform database data to match UI format
        transformed_data = []
        for indent in travel_indents:
            transformed_data.append({
                "emp_name": indent.get("employee_name", ""),
                "emp_id": indent.get("employee_id", ""),
                "grade": indent.get("grade", ""),
                "department": indent.get("department", ""),
                "email": indent.get("email", ""),
                "designation": indent.get("designation", ""),
                "purpose of booking": indent.get("purpose_of_booking", ""),
                "travel_type": indent.get("travel_type", ""),
                "travel_start_date": indent.get("travel_start_date", ""),
                "travel_end_date": indent.get("travel_end_date", ""),
                "from_city": indent.get("from_city", ""),
                "from_country": indent.get("from_country", ""),
                "to_country": indent.get("to_country", ""),
                "to_city": indent.get("to_city", ""),
                "is_approved": indent.get("is_approved", "pending"),
                "ticket_id": indent.get("indent_id", "")  # Map indent_id to ticket_id for UI
            })
        
        st.session_state.travel_data = transformed_data
        st.session_state.refresh_data = False
    
    return st.session_state.travel_data


def refresh_travel_data():
    """Force refresh travel data from backend"""
    st.session_state.refresh_data = True


# ═══════════════════════════════════════════════════════════
# STREAMLIT UI COMPONENTS
# ═══════════════════════════════════════════════════════════

def render_chat_history_management():
    """Render chat history management in sidebar"""
    st.sidebar.markdown("---")
    st.sidebar.subheader("💬 Chat History")
    
    if st.session_state.get("selected_ticket"):
        ticket_id = st.session_state.selected_ticket["ticket_id"]
        session_id = f"chat_{ticket_id}"
        
        col1, col2 = st.sidebar.columns(2)
        
        with col1:
            if st.button("📥 Load", use_container_width=True):
                with st.spinner("Loading..."):
                    history = get_chat_history(session_id)
                    
                    if history.get("messages"):
                        st.session_state.chat_history = []
                        for msg in history["messages"]:
                            if msg["role"] in ["user", "assistant"]:
                                st.session_state.chat_history.append({
                                    "role": msg["role"],
                                    "content": msg["content"]
                                })
                        st.session_state.chat_initialized = True
                        st.success(f"✓ Loaded {len(history['messages'])}")
                        st.rerun()
                    else:
                        st.info("No history")
        
        with col2:
            if st.button("🗑️ Clear", use_container_width=True):
                if clear_chat_history(session_id):
                    st.session_state.chat_history = []
                    st.session_state.chat_initialized = False
                    st.session_state.booking_complete = False
                    st.success("✓ Cleared")
                    st.rerun()
        
        # Show message count
        if st.session_state.chat_history:
            st.sidebar.caption(f"💬 {len(st.session_state.chat_history)} messages")
    else:
        st.sidebar.info("Select a ticket to manage chat")


def render_status_badge(status: str) -> str:
    """Render colored status badge"""
    status_config = {
        "saved": ("💾", "#6c757d", "DRAFT"),
        "pending": ("🕐", "#ffc107", "PENDING MANAGER"),
        "accepted_manager": ("✅", "#28a745", "APPROVED BY MANAGER"),
        "accpeted_manager": ("✅", "#28a745", "APPROVED BY MANAGER"),  # Handle typo
        "rejected_manager": ("❌", "#dc3545", "REJECTED BY MANAGER"),
        "rejected_hr": ("❌", "#dc3545", "REJECTED BY HR"),
        "completed_hr": ("✅", "#17a2b8", "BOOKING COMPLETED")
    }
    icon, color, label = status_config.get(status, ("?", "#6c757d", status.upper()))
    return f"<span style='color: {color}; font-weight: bold;'>{icon} {label}</span>"


def render_approval_badges(ticket: Dict) -> str:
    """Render workflow progress badges"""
    status = ticket.get("is_approved", "saved")
    
    badges = []
    
    # Employee Stage
    if status == "saved":
        badges.append("<span style='background: #6c757d; color: white; padding: 2px 8px; border-radius: 3px; font-size: 0.8em;'>👤 Employee ✏️</span>")
    elif status == "pending":
        badges.append("<span style='background: #ffc107; color: black; padding: 2px 8px; border-radius: 3px; font-size: 0.8em;'>👤 Employee ⏳</span>")
    else:
        badges.append("<span style='background: #28a745; color: white; padding: 2px 8px; border-radius: 3px; font-size: 0.8em;'>👤 Employee ✓</span>")
    
    # Manager Stage
    if status in ["saved", "pending"]:
        badges.append("<span style='background: #6c757d; color: white; padding: 2px 8px; border-radius: 3px; font-size: 0.8em;'>👔 Manager -</span>")
    elif status == "rejected_manager":
        badges.append("<span style='background: #dc3545; color: white; padding: 2px 8px; border-radius: 3px; font-size: 0.8em;'>👔 Manager ✗</span>")
    elif status in ["accepted_manager", "accpeted_manager", "completed_hr", "rejected_hr"]:
        badges.append("<span style='background: #28a745; color: white; padding: 2px 8px; border-radius: 3px; font-size: 0.8em;'>👔 Manager ✓</span>")
    
    # HR Stage
    if status in ["saved", "pending", "rejected_manager", "accepted_manager"]:
        badges.append("<span style='background: #6c757d; color: white; padding: 2px 8px; border-radius: 3px; font-size: 0.8em;'>🏢 HR -</span>")
    elif status == "rejected_hr":
        badges.append("<span style='background: #dc3545; color: white; padding: 2px 8px; border-radius: 3px; font-size: 0.8em;'>🏢 HR ✗</span>")
    elif status == "completed_hr":
        badges.append("<span style='background: #17a2b8; color: white; padding: 2px 8px; border-radius: 3px; font-size: 0.8em;'>🏢 HR ✓</span>")
    elif status == "rejected_hr":
        badges.append("<span style='background: #dc3545; color: white; padding: 2px 8px; border-radius: 3px; font-size: 0.8em;'>🏢 HR ✗</span>")
    elif status == "accepted_manager":
        badges.append("<span style='background: #ffc107; color: black; padding: 2px 8px; border-radius: 3px; font-size: 0.8em;'>🏢 HR ⏳</span>")
    else:
        badges.append("<span style='background: #6c757d; color: white; padding: 2px 8px; border-radius: 3px; font-size: 0.8em;'>🏢 HR -</span>")
    
    return " ".join(badges)


def render_travel_requests_table(travel_data: list):
    """Render enhanced travel requests table"""
    # Filter out rejected tickets
    filtered_data = travel_data
    st.subheader("📋 Travel Requests Dashboard")
    
    # Refresh button
    col1, col2 = st.columns([4, 1])
    with col2:
        if st.button("🔄 Refresh", use_container_width=True):
            refresh_travel_data()
            st.rerun()
    
    if not filtered_data:
        st.info("No active travel requests.")
        return
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        pending = len([t for t in filtered_data if t["is_approved"] == "pending"])
        st.metric("Pending Manager", pending)
    with col2:
        approved = len([t for t in filtered_data if t["is_approved"] in ["accepted_manager", "accpeted_manager"]])
        st.metric("Ready for HR", approved)
    with col3:
        completed = len([t for t in filtered_data if t["is_approved"] == "completed_hr"])
        st.metric("Completed", completed)
    with col4:
        total = len(filtered_data)
        st.metric("Total Active", total)
    
    st.markdown("---")
    
    # Table header
    col1, col2, col3, col4, col5, col6 = st.columns([0.7, 1.5, 1, 1.2, 1, 0.8])
    with col1:
        st.markdown("**Ticket**")
    with col2:
        st.markdown("**Employee**")
    with col3:
        st.markdown("**Department**")
    with col4:
        st.markdown("**Travel Route**")
    with col5:
        st.markdown("**Workflow Status**")
    with col6:
        st.markdown("**Action**")
    
    st.markdown("---")
    
    # Table rows
    for item in filtered_data:
        col1, col2, col3, col4, col5, col6 = st.columns([0.7, 1.5, 1, 1.2, 1, 0.8])
        
        with col1:
            st.markdown(f"**{item['ticket_id']}**")
            st.caption(f"{'🌍' if item['travel_type'] == 'international' else '🏠'} {item['travel_type']}")
        
        with col2:
            st.markdown(f"**{item['emp_name']}**")
            st.caption(f"{item['emp_id']} • {item['grade']}")
            st.caption(item['designation'])
        
        with col3:
            st.write(item['department'])
        
        with col4:
            st.markdown(f"**{item['from_city']} → {item['to_city']}**")
            st.caption(f"📅 {item['travel_start_date']}")
            st.caption(f"📅 {item['travel_end_date']}")
        
        with col5:
            st.markdown(render_approval_badges(item), unsafe_allow_html=True)
            st.markdown(render_status_badge(item['is_approved']), unsafe_allow_html=True)
        
        with col6:
            status = item["is_approved"]
            
            # Only HR can proceed with accepted_manager tickets
            if status == "accepted_manager":
                if st.button("✈️ Book", key=f"book_{item['ticket_id']}", type="primary"):
                    st.session_state.selected_ticket = item
                    st.session_state.booking_mode = "active"
                    st.session_state.chat_history = []
                    st.session_state.chat_initialized = False
                    st.session_state.booking_complete = False
                    st.rerun()
            elif status == "completed_hr":
                if st.button("👁️ View", key=f"view_{item['ticket_id']}", type="secondary"):
                    st.session_state.selected_ticket = item
                    st.session_state.booking_mode = "view"
                    st.session_state.chat_history = []
                    st.session_state.chat_initialized = False
                    st.session_state.booking_complete = True
                    st.rerun()
            else:
                st.button("⏳ Pending", key=f"wait_{item['ticket_id']}", disabled=True, type="secondary")
        
        st.markdown("---")


def render_booking_panel(ticket: Dict):
    """Render chat-based booking panel"""
    st.markdown("---")
    
    # Header with action buttons
    col1, col2, col3 = st.columns([4, 1, 1])
    with col1:
        st.subheader(f"💬 Travel Booking Chat - {ticket['ticket_id']}")
    with col2:
        # Only show reject button if not completed
        if ticket["is_approved"] == "accepted_manager" and not st.session_state.get("booking_complete", False):
            if st.button("❌ Reject", type="secondary", use_container_width=True):
                if update_ticket_status_api(ticket["ticket_id"], "rejected_hr"):
                    st.success("✓ Ticket rejected by HR")
                    refresh_travel_data()  # Refresh data from backend
                    st.session_state.booking_mode = None
                    st.session_state.selected_ticket = None
                    st.session_state.chat_history = []
                    st.session_state.chat_initialized = False
                    st.session_state.booking_complete = False
                    st.rerun()
    with col3:
        if st.button("← Back", use_container_width=True):
            st.session_state.booking_mode = None
            st.session_state.selected_ticket = None
            st.session_state.chat_history = []
            st.session_state.chat_initialized = False
            st.session_state.booking_complete = False
            st.rerun()
    
    # Ticket info
    st.caption(f"👤 {ticket['emp_name']} ({ticket['emp_id']}) | 🎯 {ticket['from_city']} → {ticket['to_city']} | 📅 {ticket['travel_start_date']} to {ticket['travel_end_date']}")
    st.markdown(render_status_badge(ticket['is_approved']), unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Initialize session state
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "booking_complete" not in st.session_state:
        st.session_state.booking_complete = False
    
    # Session ID for this ticket
    session_id = f"chat_{ticket['ticket_id']}"
    
    # Display chat messages
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
    
    # Show initial context when chat opens (not sent as message yet)
    if not st.session_state.chat_initialized and len(st.session_state.chat_history) == 0:
        with st.expander("📋 **Travel Request Details** (for your reference)", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Employee Information:**")
                st.write(f"👤 Name: {ticket['emp_name']}")
                st.write(f"🆔 ID: {ticket['emp_id']}")
                st.write(f"📊 Grade: {ticket['grade']}")
                st.write(f"💼 Designation: {ticket['designation']}")
                st.write(f"🏢 Department: {ticket['department']}")
                st.write(f"📧 Email: {ticket['email']}")
            
            with col2:
                st.markdown("**Travel Information:**")
                st.write(f"🌍 Type: {ticket['travel_type']}")
                st.write(f"🛫 From: {ticket['from_city']}, {ticket['from_country']}")
                st.write(f"🛬 To: {ticket['to_city']}, {ticket['to_country']}")
                st.write(f"📅 Start: {ticket['travel_start_date']}")
                st.write(f"📅 End: {ticket['travel_end_date']}")
                st.write(f"📝 Purpose: {ticket['purpose of booking']}")
        
        st.info("💡 **Tip:** Type your request like 'Can you plan trip for this?' or 'Show me flight options' or 'Book only flight' and click Send.")
    
    # Chat input (disabled if booking complete)
    if not st.session_state.booking_complete:
        if prompt := st.chat_input("💬 Type your request (e.g., 'Can you plan trip for this?')...", key=f"chat_input_{ticket['ticket_id']}"):
            # Add user message to chat history
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            
            with st.chat_message("user"):
                st.write(prompt)
            
            # Get AI response
            with st.spinner("🤖 Processing with AI assistant..."):
                response = call_chat_api(
                    message=prompt,
                    session_id=session_id,
                    indent_id=ticket["ticket_id"]  # Send indent_id to backend for context
                )
            
            # Mark as initialized
            st.session_state.chat_initialized = True
            
            # Update booking complete status from backend response
            if response.get("booking_complete", False):
                st.session_state.booking_complete = True
                refresh_travel_data()  # Refresh data from backend
                st.success("✓ Booking completed and ticket status updated!")
            
            # Add assistant response
            assistant_msg = {
                "role": "assistant",
                "content": response.get("response", "No response")
            }
            
            st.session_state.chat_history.append(assistant_msg)
            
            with st.chat_message("assistant"):
                st.write(assistant_msg["content"])
                
                # Show tools used if any
                tools_used = response.get("tools_used", [])
                if tools_used:
                    with st.expander("🔧 Tools Used"):
                        for tool in tools_used:
                            st.caption(f"• {tool}")
                
                # Show completion message
                if st.session_state.booking_complete:
                    st.success("✅ Booking completed! Flight and hotel have been booked. Ticket marked as completed.")
                    st.balloons()
    else:
        st.success("✅ Booking is complete. Flight and hotel have been booked successfully.")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Start New Conversation", use_container_width=True):
                st.session_state.chat_history = []
                st.session_state.chat_initialized = False
                st.session_state.booking_complete = False
                st.rerun()
        with col2:
            if st.button("📋 Back to Dashboard", use_container_width=True):
                st.session_state.booking_mode = None
                st.session_state.selected_ticket = None
                st.session_state.chat_history = []
                st.session_state.chat_initialized = False
                st.session_state.booking_complete = False
                st.rerun()


# ═══════════════════════════════════════════════════════════
# MAIN UI FUNCTION
# ═══════════════════════════════════════════════════════════

def hr_ui(token):
    """Main HR Dashboard UI"""
    st.set_page_config(
        page_title="HR Travel Dashboard", 
        page_icon="✈️", 
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # --- Start of the code to add ---
    token = st.session_state.get("auth", {}).get("token")
    if not token:
        st.error("Please login first.")
        return
    
    st.title("✈️ Corporate Travel Management Dashboard")
    st.caption("🤖 AI-powered booking assistance for employee travel requests")
    
    # Initialize session state
    if "booking_mode" not in st.session_state:
        st.session_state.booking_mode = None
    if "selected_ticket" not in st.session_state:
        st.session_state.selected_ticket = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "chat_initialized" not in st.session_state:
        st.session_state.chat_initialized = False
    if "booking_complete" not in st.session_state:
        st.session_state.booking_complete = False
    if "refresh_data" not in st.session_state:
        st.session_state.refresh_data = True
    
    # Sidebar
    with st.sidebar:
        st.title("⚙️ Settings")
        st.caption(f"API: {API_BASE_URL}")
        
        # Health check
        try:
            health = requests.get(f"{API_BASE_URL}/health", timeout=5)
            if health.status_code == 200:
                data = health.json()
                st.success("✓ API Connected")
                st.caption(f"Tools: {data.get('tools_available', 0)}")
                st.caption(f"Database: {'✓ Connected' if data.get('database_connected') else '✗ Disconnected'}")
            else:
                st.error("✗ API Error")
        except:
            st.error("✗ API Offline")
        
        render_chat_history_management()
    
    # Main content
    if st.session_state.booking_mode in ["active", "view"] and st.session_state.selected_ticket:
        render_booking_panel(st.session_state.selected_ticket)
    else:
        render_travel_requests_table(get_travel_data())


if __name__ == "__main__":
    hr_ui()