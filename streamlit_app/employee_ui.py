import streamlit as st
import requests
from datetime import date

FASTAPI_URL = "http://127.0.0.1:8000"


def employee_ui(token: str) -> None:
    """
    Employee dashboard:
    - Create new travel request
    - See list of own tickets (/employee/my-indents)
    """
    # ----------------- BASIC CONTEXT -----------------
    # Read whatever login stored
    auth = st.session_state.get("auth", {})
    emp_id = auth.get("employee_id", "")
    emp_name = auth.get("name", "") or "Employee"

    headers = {"Authorization": f"Bearer {token}"}

    # ----------------- LIGHT GLOBAL STYLES -----------------
    st.markdown(
        """
        <style>
        .header-card {
            background: linear-gradient(90deg, #2563eb, #0ea5e9);
            padding: 16px 22px;
            border-radius: 18px;
            color: white;
            box-shadow: 0 10px 26px rgba(15, 23, 42, 0.25);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .header-title {
            font-size: 1.35rem;
            font-weight: 700;
            letter-spacing: 0.01em;
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
            background: rgba(248, 250, 252, 0.16);
            font-size: 0.8rem;
            border: 1px solid rgba(226, 232, 240, 0.35);
        }
        .section-title {
            font-size: 1.02rem;
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
        .request-card {
            padding: 12px 14px;
            border-radius: 14px;
            border: 1px solid #e5e7eb;
            background: #ffffff;
            margin-bottom: 10px;
            box-shadow: 0 6px 16px rgba(15, 23, 42, 0.08);
            transition: all 0.15s ease-out;
        }
        .request-card:hover {
            transform: translateY(-1px);
            box-shadow: 0 10px 20px rgba(15, 23, 42, 0.12);
            border-color: #c7d2fe;
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
        .stButton button {
            background: linear-gradient(90deg, #2563eb, #4f46e5);
            color: #ffffff;
            border-radius: 999px;
            padding: 0.5rem 1.1rem;
            border: none;
            font-weight: 600;
            font-size: 0.95rem;
            box-shadow: 0 10px 22px rgba(37, 99, 235, 0.4);
            transition: all 0.15s ease-out;
        }
        .stButton button:hover {
            transform: translateY(-1px);
            box-shadow: 0 14px 26px rgba(30, 64, 175, 0.5);
        }
        .stTextInput>div>div>input,
        .stTextArea textarea {
            border-radius: 10px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # ----------------- HEADER -----------------
    st.markdown(
        f"""
        <div class="header-card">
            <div>
                <div class="header-title">
                    <span>📌</span> <span>Travel Desk – Employee</span>
                </div>
                <div class="header-subtitle">
                    Raise new travel requests and track their status in one place.
                </div>
            </div>
            <div style="display:flex; gap:8px; align-items:center;">
                <div class="pill">
                    <span>👤</span> <span>{emp_name}</span>
                </div>
                <div class="pill">
                    <span>🆔</span> <span>{emp_id or "-"} </span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # small spacer
    st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)

    # ----------------- LAYOUT: FORM (LEFT) + TICKETS (RIGHT) -----------------
    left_col, right_col = st.columns([2, 1])

    # =============================================================
    # LEFT – TRAVEL REQUEST FORM
    # =============================================================
    with left_col:
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
            # travel type
            travel_type = st.selectbox(
                "Travel Type",
                ["domestic", "international"],
                key="travel_type_select",
                help="Domestic: within the same country. International: cross‑border travel.",
            )

            # dates
            d1, d2 = st.columns(2)
            with d1:
                travel_start_date = st.date_input(
                    "Travel Start Date (From Date)",
                    value=date.today(),
                    key="travel_start_date",
                )
            with d2:
                travel_end_date = st.date_input(
                    "Travel End Date (To Date)",
                    value=date.today(),
                    key="travel_end_date",
                )

            # countries — IMPORTANT: different keys for domestic vs international
            cfrom, cto = st.columns(2)
            if travel_type == "domestic":
                with cfrom:
                    st.text_input(
                        "From Country",
                        value="India",
                        disabled=True,
                        key="from_country_dom",
                    )
                with cto:
                    st.text_input(
                        "To Country",
                        value="India",
                        disabled=True,
                        key="to_country_dom",
                    )
                from_country = "India"
                to_country = "India"
            else:
                with cfrom:
                    from_country = st.text_input(
                        "From Country",
                        value=st.session_state.get("from_country_int", "India"),
                        key="from_country_int",
                    )
                with cto:
                    to_country = st.text_input(
                        "To Country",
                        value=st.session_state.get("to_country_int", ""),
                        key="to_country_int",
                    )

            # cities
            city_from, city_to = st.columns(2)
            with city_from:
                from_city = st.text_input("From City", placeholder="e.g., Indore", key="from_city")
            with city_to:
                to_city = st.text_input(
                    "To City",
                    placeholder="e.g., Pune / Dubai",
                    key="to_city",
                )

            # purpose
            purpose_of_booking = st.text_area(
                "Purpose of Booking",
                placeholder=(
                    "Write a crisp purpose – client demo, training, onsite support, conference, etc. "
                    "This will be visible to manager and HR."
                ),
                height=120,
                key="purpose_of_booking",
            )

            submitted = st.form_submit_button("Submit Travel Request")

        # ---------- SUBMIT HANDLER ----------
        if submitted:
            # validations
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

                # Best‑effort refresh so ticket list updates (handles both new & old Streamlit)
                if hasattr(st, "rerun"):
                    st.rerun()
                elif hasattr(st, "experimental_rerun"):
                    st.experimental_rerun()
            else:
                try:
                    err = resp.json()
                except Exception:
                    err = {"detail": resp.text}
                st.error(f"Failed to create ticket: {err}")


    # =============================================================
    # RIGHT – MY TRAVEL REQUESTS
    # =============================================================
    with right_col:
        st.markdown(
            f"""
            <div class="section-title">🧾 My Travel Requests – {emp_name}</div>
            <div class="section-caption">
                Latest tickets raised by you. Status updates will reflect here as manager / HR take action.
            </div>
            """,
            unsafe_allow_html=True,
        )

        indents = []
        try:
            resp = requests.get(
                f"{FASTAPI_URL}/employee/my-indents",
                headers=headers,
                timeout=30,
            )
            if resp.status_code == 200:
                data = resp.json()
                # Support both list and wrapped formats
                if isinstance(data, list):
                    indents = data
                else:
                    indents = (
                        data.get("indents")
                        or data.get("items")
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
            return

        # Show newest first based on created_at when available
        def _sort_key(item: dict):
            return item.get("created_at") or item.get("travel_start_date") or ""

        for item in sorted(indents, key=_sort_key, reverse=True):
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

            from_city = item.get("from_city", "-")
            to_city = item.get("to_city", "-")
            t_type = (item.get("travel_type") or "domestic").capitalize()
            start = item.get("travel_start_date") or item.get("start_date") or "-"
            end = item.get("travel_end_date") or item.get("end_date") or "-"
            indent_id = item.get("indent_id", "-")

            st.markdown(
                f"""
                <div class="request-card">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <div>
                            <span style="font-size:0.8rem; color:#6b7280;">Ticket ID:</span>
                            <span style="font-weight:600; font-size:0.85rem;"> {indent_id}</span>
                        </div>
                        <div style="font-size:0.8rem; color:#6b7280;">
                            📅 {start} → {end}
                        </div>
                    </div>
                    <div style="margin-top:4px;">
                        <div style="font-weight:600; font-size:0.96rem;">
                            ✈️ {from_city} ➜ {to_city} • {t_type}
                        </div>
                        <div style="margin-top:4px;">
                            <span style="font-size:0.82rem; color:#6b7280; margin-right:6px;">Status:</span>
                            <span class="{badge_class}">{status_label}</span>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
