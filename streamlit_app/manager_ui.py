import streamlit as st
import requests
import uuid

# =================================================================
# MANAGER DASHBOARD UI
# =================================================================


def manager_ui(token):
    if "current_tab" not in st.session_state:
        st.session_state.current_tab = "all"

    st.title("👨‍💼 Manager Dashboard")
    headers = {"Authorization": f"Bearer {token}"}

    tab1, tab2, tab3 = st.tabs(["📋 All Tickets", "🕒 Pending", "✅ Approved"])

    with tab1:
        st.session_state.current_tab = "all"
        st.subheader("📋 All Tickets Submitted")
        res = requests.get("http://localhost:8000/manager/indents", headers=headers)
        if res.status_code == 200:
            tickets = sorted(res.json(), key=lambda x: x["created_at"], reverse=True)
            for item in tickets:
                show_ticket(item, show_approve=True, show_reject=True, token=token)
        else:
            st.error("Failed to load tickets.")
            st.code(res.text)

    with tab2:
        st.session_state.current_tab = "pending"
        st.subheader("🕒 Tickets Pending Approval")
        res = requests.get("http://localhost:8000/manager/pending", headers=headers)
        if res.status_code == 200:
            pending = sorted(res.json(), key=lambda x: x["created_at"], reverse=True)
            for item in pending:
                show_ticket(item, show_approve=True, show_reject=True, token=token)
        else:
            st.error("Failed to load pending tickets.")

    with tab3:
        st.session_state.current_tab = "approved"
        st.subheader("✅ Approved Tickets")
        res = requests.get("http://localhost:8000/manager/approved", headers=headers)
        if res.status_code == 200:
            approved = sorted(res.json(), key=lambda x: x["created_at"], reverse=True)
            for item in approved:
                show_ticket(item, token=token)
        else:
            st.error("Failed to load approved tickets.")




# =================================================================
# SHOW TICKET (unique-button-safe)
# =================================================================
def show_ticket(item, show_approve=False, show_reject=False, token=None):
    current_tab = st.session_state.get("current_tab", "all")
    profile_key = f"profile_toggle_{current_tab}_{item['indent_id']}"

    with st.expander(f"🧾 {item['indent_id']} — {item['employee_name']}", expanded=False):
        st.markdown("### 👤 Employee Summary")
        st.write(f"**Name:** {item['employee_name']}")
        st.write(f"**Employee ID:** {item['employee_id']}")

        if profile_key not in st.session_state:
            st.session_state[profile_key] = False

        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("View Full Profile", key=f"btn_{profile_key}"):
                st.session_state[profile_key] = True
        with col2:
            if st.session_state[profile_key] and st.button("Close Profile", key=f"close_{profile_key}"):
                st.session_state[profile_key] = False

        if st.session_state[profile_key]:
            show_inline_profile(item["employee_id"], token)

        st.markdown("### ✈ Travel Details")
        st.write(f"**From:** {item['from_city']}")
        st.write(f"**To:** {item['to_city']}")
        st.write(f"**Start Date:** {item['travel_start_date']}")
        st.write(f"**End Date:** {item['travel_end_date']}")
        st.write(f"**Purpose:** {item['purpose_of_booking']}")

        st.markdown("### ✔ Approval Status")
        status = item["is_approved"]
        st.write("🟡 **Pending Approval**" if status == "pending" else "🟢 **Approved**" if status == "accepted" else f"Status: {status}")

        if show_approve and status == "pending":
            approve_key = f"approve_{current_tab}_{item['indent_id']}"
            if st.button("Approve Ticket ✔", key=approve_key):
                print(f"Approving ticket: {item['indent_id']}")
                res = requests.post(
                    f"http://localhost:8000/manager/approve/{item['indent_id']}",
                    headers={"Authorization": f"Bearer {token}"}
                )
                print(f"Approval response: {res.status_code}, {res.text}")
                if res.status_code == 200:
                    st.success("Ticket Approved!")
                    st.rerun()
                else:
                    st.error("Approval failed.")

            if show_reject and status == "pending":
                reject_key = f"reject_{current_tab}_{item['indent_id']}"
                if st.button("Reject Ticket", key=reject_key):
                    print(f"Rejecting ticket: {item['indent_id']}")
                    res = requests.post(
                        f"http://localhost:8000/manager/reject/{item['indent_id']}",
                        headers={"Authorization": f"Bearer {token}"}
                    )
                    print(f"Rejection response: {res.status_code}, {res.text}")
                    if res.status_code == 200:
                        st.success("Ticket Rejected!")
                        st.rerun()
                    else:
                        st.error("Rejection failed.")




# =================================================================
# EMPLOYEE FULL PROFILE (only appears when clicked)
# =================================================================


def show_inline_profile(emp_id, token):
    headers = {"Authorization": f"Bearer {token}"}
    res = requests.get(f"http://localhost:8000/manager/employee-profile/{emp_id}", headers=headers)

    if res.status_code != 200:
        st.error("Failed to load profile.")
        return

    profile = res.json()
    st.markdown(f"""
**Email:** {profile['email']}  
**Gender:** {profile.get('gender', 'N/A')}  
**Grade:** {profile['grade']}  
**Department:** {profile['department']}  
**Designation:** {profile['designation']}  
**Manager:** {profile['manager_id']}  
**Joining Date:** {profile['created_at']}  
**Home City:** {profile.get('city', 'N/A')}  
""")
