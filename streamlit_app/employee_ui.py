import streamlit as st
import requests
import datetime  # <- use datetime.date.today()

FASTAPI_URL = "http://127.0.0.1:8000"


def employee_ui():
    st.set_page_config(page_title="Travel Desk – Employee", layout="wide")

    # ----------------- GLOBAL STYLES -----------------
    st.markdown(
        """
        <style>
        .main {
            background: linear-gradient(180deg, #f7f9fc 0%, #ffffff 45%, #f5f7fb 100%);
        }

        .header-card {
            background: linear-gradient(90deg, #2563eb, #0ea5e9);
            padding: 18px 24px;
            border-radius: 18px;
            color: white;
            box-shadow: 0 12px 30px rgba(15, 23, 42, 0.28);
            display: flex;
            justify-content: space-between;
            align-items: center;
            animation: fadeInDown 0.45s ease-out;
        }

        .header-title {
            font-size: 1.45rem;
            font-weight: 700;
            letter-spacing: 0.02em;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .header-subtitle {
            font-size: 0.9rem;
            opacity: 0.9;
        }

        .pill {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 6px 12px;
            border-radius: 999px;
            background: rgba(248, 250, 252, 0.18);
            font-size: 0.8rem;
            border: 1px solid rgba(226, 232, 240, 0.35);
        }

        .pill span.icon {
            font-size: 0.9rem;
        }

        .section-title {
            font-size: 1.05rem;
            font-weight: 600;
            margin-bottom: 0.25rem;
            display: flex;
            align-items: center;
            gap: 6px;
        }

        .section-caption {
            font-size: 0.85rem;
            color: #6b7280;
            margin-bottom: 0.75rem;
        }

        .stButton button {
            background: linear-gradient(90deg, #2563eb, #4f46e5);
            color: #ffffff;
            border-radius: 999px;
            padding: 0.5rem 1.1rem;
            border: none;
            font-weight: 600;
            font-size: 0.95rem;
            box-shadow: 0 10px 22px rgba(37, 99, 235, 0.45);
            transition: all 0.18s ease-out;
        }
        .stButton button:hover {
            transform: translateY(-1px);
            box-shadow: 0 14px 26px rgba(30, 64, 175, 0.55);
        }

        /* Ticket cards on right side */
        .request-card {
            padding: 14px 16px;
            border-radius: 16px;
            border: 1px solid #e5e7eb;
            background: #ffffff;
            margin-bottom: 10px;
            box-shadow: 0 8px 18px rgba(15, 23, 42, 0.08);
            transition: all 0.18s ease-out;
        }
        .request-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 12px 26px rgba(15, 23, 42, 0.12);
            border-color: #c4d1ff;
        }

        .badge-status {
            padding: 3px 10px;
            border-radius: 999px;
            font-size: 0.78rem;
            font-weight: 500;
        }
        .badge-pending {
            background: #fffbeb;
            color: #92400e;
            border: 1px solid #fed7aa;
        }
        .badge-approved {
            background: #ecfdf3;
            color: #166534;
            border: 1px solid #bbf7d0;
        }
        .badge-rejected {
            background: #fef2f2;
            color: #991b1b;
            border: 1px solid #fecaca;
        }

        .request-title {
            font-weight: 600;
            font-size: 0.98rem;
        }
        .request-meta {
            font-size: 0.8rem;
            color: #6b7280;
        }

        .stTextInput>div>div>input,
        .stTextArea textarea {
            border-radius: 10px;
        }

        @keyframes fadeInDown {
            from {opacity: 0; transform: translateY(-10px);}
            to   {opacity: 1; transform: translateY(0);}
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    token = st.session_state.get("token")
    if not token:
        st.error("Please login first.")
        return

    emp_name = st.session_state.get("name", "")
    emp_id = st.session_state.get("employee_id", "")

    # ----------------- HEADER -----------------
    st.markdown(
        f"""
        <div class="header-card">
            <div>
                <div class="header-title">
                    <span>📌</span> <span>Travel Desk – Employee Request</span>
                </div>
                <div class="header-subtitle">
                    Create new travel requests and track the status of all your previous tickets in one place.
                </div>
            </div>
            <div style="display:flex; gap:8px; align-items:center;">
                <div class="pill">
                    <span class="icon">👤</span> <span>{emp_name or "Employee"}</span>
                </div>
                <div class="pill">
                    <span class="icon">🆔</span> <span>{emp_id or "-"}</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Small vertical spacer ONLY (no white boxes)
    st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)

    # ----------------- LAYOUT: LEFT FORM / RIGHT TICKETS -----------------
    left_col, right_col = st.columns([2, 1])

    # ============================================================
    # LEFT SIDE – EMPLOYEE + TRAVEL FORM
    # ============================================================
    with left_col:
        # Employee details (minimal)
        st.markdown(
            """
            <div class="section-title">👨‍💼 Employee Details</div>
            <div class="section-caption">Read-only details from your profile.</div>
            """,
            unsafe_allow_html=True,
        )
        ec1, ec2 = st.columns(2)
        with ec1:
            st.text_input("Employee Name", emp_name, disabled=True)
        with ec2:
            st.text_input("Employee ID", emp_id, disabled=True)

        st.markdown("---")

        # Travel form
        st.markdown(
            """
            <div class="section-title">✈️ Travel Details</div>
            <div class="section-caption">
                Fill journey details as required for approvals and bookings.
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.form("travel_request_form", clear_on_submit=False):
            top1, top2 = st.columns(2)
            with top1:
                travel_type = st.selectbox(
                    "Travel Type",
                    ["domestic", "international"],
                    help="Domestic: within the same country. International: cross-border travel.",
                )
            with top2:
                pass

            d1, d2 = st.columns(2)
            with d1:
                travel_start_date = st.date_input(
                    "Travel Start Date (From Date)",
                    value=datetime.date.today(),
                )
            with d2:
                travel_end_date = st.date_input(
                    "Travel End Date (To Date)",
                    value=datetime.date.today(),
                )

            # -------- Country fields (no disabled / works for both types) --------
            cfrom, cto = st.columns(2)

            # Always render editable inputs so switching domestic/international works reliably
            with cfrom:
                from_country_input = st.text_input(
                    "From Country",
                    value="India",            # default for both
                    key="from_country_input",
                )

            with cto:
                # default to India for domestic, blank for international
                to_country_input = st.text_input(
                    "To Country",
                    value="India" if travel_type == "domestic" else "",
                    key="to_country_input",
                    placeholder="e.g., UAE / USA / UK",
                )

            # Business logic: what we actually send to backend
            if travel_type == "domestic":
                # For domestic we always force India, ignore whatever user typed
                from_country = "India"
                to_country = "India"
            else:
                # For international we use the user inputs
                from_country = (from_country_input or "").strip()
                to_country = (to_country_input or "").strip()


            city_from, city_to = st.columns(2)
            with city_from:
                from_city = st.text_input("From City", placeholder="e.g., Indore")
            with city_to:
                to_city = st.text_input("To City", placeholder="e.g., Pune / Dubai")

            purpose_of_booking = st.text_area(
                "Purpose of Booking",
                placeholder="Write a crisp purpose – client demo, training, onsite support, conference, etc.",
                height=110,
            )

            st.markdown(
                "<span style='font-size:0.8rem; color:#6b7280;'>This will be visible to your manager and HR for approval.</span>",
                unsafe_allow_html=True,
            )

            submitted = st.form_submit_button("Submit Travel Request")

        # ---------- HANDLE SUBMIT ----------
        if submitted:
            if not purpose_of_booking.strip():
                st.warning("Please enter the purpose of booking.")
                st.stop()

            if not from_city.strip() or not to_city.strip():
                st.warning("Please fill both From City and To City.")
                st.stop()

            if travel_end_date < travel_start_date:
                st.error("Travel end date cannot be before travel start date.")
                st.stop()

            if travel_type == "international" and not to_country.strip():
                st.warning("Please provide destination country for international travel.")
                st.stop()

            payload = {
                "purpose_of_booking": purpose_of_booking.strip(),
                "travel_type": travel_type,
                "travel_start_date": str(travel_start_date),
                "travel_end_date": str(travel_end_date),
                "from_city": from_city.strip(),
                "from_country": from_country.strip(),
                "to_city": to_city.strip(),
                "to_country": to_country.strip(),
            }

            headers = {"Authorization": f"Bearer {token}"}

            try:
                resp = requests.post(
                    f"{FASTAPI_URL}/employee/create-indent",
                    json=payload,
                    headers=headers,
                    timeout=30,
                )
            except Exception as e:
                st.error(f"Could not reach server: {e}")
                st.stop()

            if resp.status_code == 200:
                data = resp.json()
                indent_id = data.get("indent_id")
                st.success("✅ Travel request created successfully.")
                if indent_id:
                    st.info(f"Ticket / Indent ID: **{indent_id}**")
            else:
                try:
                    err = resp.json()
                except Exception:
                    err = {"detail": resp.text}
                st.error(f"Failed to create ticket: {err}")

    # ============================================================
    # RIGHT SIDE – MY TRAVEL REQUESTS
    # ============================================================
    with right_col:
        st.markdown(
            f"""
            <div class="section-title">🧾 My Travel Requests – {emp_name or "Employee"}</div>
            <div class="section-caption">
                Latest tickets raised by you. Status updates will reflect here as manager/HR take action.
            </div>
            """,
            unsafe_allow_html=True,
        )

        indents = []
        try:
            resp = requests.get(
                f"{FASTAPI_URL}/employee/my-indents",
                headers={"Authorization": f"Bearer {token}"},
                timeout=30,
            )
            if resp.status_code == 200:
                data = resp.json()
                # Support multiple possible response shapes
                if isinstance(data, list):
                    indents = data
                else:
                    indents = (
                        data.get("indents")
                        or data.get("items")      # original shape
                        or data.get("tickets")
                        or data.get("data")
                        or []
                    )
            else:
                st.warning(f"Unable to fetch travel requests (status {resp.status_code}).")
        except Exception as e:
            st.warning(f"Unable to fetch your previous requests: {e}")

        if not indents:
            st.info("You have not raised any travel requests yet.")
        else:
            for item in sorted(indents, key=lambda x: x.get("created_at", ""), reverse=True):
                status_raw = (item.get("status") or item.get("is_approved") or "pending").lower()
                if status_raw == "approved":
                    badge_class = "badge-status badge-approved"
                    status_label = "Approved"
                elif status_raw in ("rejected", "declined"):
                    badge_class = "badge-status badge-rejected"
                    status_label = "Rejected"
                else:
                    badge_class = "badge-status badge-pending"
                    status_label = "Pending"

                from_city_val = item.get("from_city", "-")
                to_city_val = item.get("to_city", "-")
                t_type = (item.get("travel_type") or "domestic").capitalize()
                start = item.get("travel_start_date") or item.get("start_date") or "-"
                end = item.get("travel_end_date") or item.get("end_date") or "-"
                indent_id = item.get("indent_id", "-")

                st.markdown(
                    f"""
                    <div class="request-card">
                        <div class="request-meta" style="display:flex; justify-content:space-between; align-items:center;">
                            <div>
                                <span style="font-size:0.8rem; color:#6b7280;">Ticket ID:</span>
                                <span style="font-weight:600; font-size:0.85rem;"> {indent_id}</span>
                            </div>
                            <div class="request-meta">
                                📅 {start} → {end}
                            </div>
                        </div>
                        <div style="margin-top:4px;">
                            <div class="request-title">✈️ {from_city_val} ➜ {to_city_val} • {t_type}</div>
                            <div style="margin-top:4px;">
                                <span style="font-size:0.82rem; color:#6b7280; margin-right:6px;">Status:</span>
                                <span class="{badge_class}">{status_label}</span>
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
