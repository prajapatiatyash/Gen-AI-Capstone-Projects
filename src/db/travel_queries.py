# src/db/travel_queries.py
from src.db.connection import get_db_conn
import uuid, datetime

def get_user_by_employee_id(employee_id: str):
    with get_db_conn() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT employee_id, name, email, password_hash, grade, role, is_active, manager_id
            FROM users WHERE employee_id=%s
        """, (employee_id,))
        row = cur.fetchone()
        cur.close()
    if not row:
        return None
    return {
        "employee_id": row[0],
        "name": row[1],
        "email": row[2],
        "password_hash": row[3],
        "grade": row[4],
        "role": row[5],
        "is_active": row[6],
        "manager_id": row[7],
    }

def get_user_details(employee_id: str):
    u = get_user_by_employee_id(employee_id)
    if not u:
        return None
    return {k: u[k] for k in ("employee_id","name","email","grade","role","manager_id","is_active")}

def fetch_eligible_hotels(grade, city, limit=5):
    with get_db_conn() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT id, hotel_name, city, final_corporate_rate, grade_eligibility, is_active
            FROM tied_up_hotels
            WHERE city ILIKE %s AND is_active = TRUE
            ORDER BY final_corporate_rate ASC
            LIMIT %s
        """, (city, limit))
        rows = cur.fetchall()
        cur.close()
    hotels = []
    for r in rows:
        hotels.append({
            "id": r[0], "name": r[1], "city": r[2], "rate": float(r[3]), "grade_eligibility": r[4]
        })
    # filter by grade
    return [h for h in hotels if (h["grade_eligibility"] is None) or (grade in h["grade_eligibility"])]

def fetch_flights(source, destination, date=None):
    # Demo stub; replace with real API
    return [
        {"airline": "Indigo", "flight_no":"6E-502", "price":8200, "dep_time":"09:00"},
        {"airline": "Vistara", "flight_no":"UK-864", "price":9100, "dep_time":"13:00"}
    ]

def create_travel_indent(employee_id, intent, selected_flight, selected_hotel):
    indent_id = f"TIX{str(uuid.uuid4())[:8].upper()}"
    total_days = intent.get("total_days", 1)
    est_flight = selected_flight.get("price", 0)
    hotel_rate = selected_hotel.get("rate", 0)
    total_estimated = est_flight + hotel_rate * total_days
    with get_db_conn() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO travel_indents
            (indent_id, employee_id, purpose, source_city, destination_city, start_date, end_date, total_days,
             estimated_flight_cost, preferred_hotel_id, status, manager_approval_status, budget_approval_status, hr_approval_status, total_estimated_cost, created_at, updated_at)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,NOW(),NOW())
        """, (
            indent_id, employee_id, intent.get("purpose"), intent.get("source_city"), intent.get("destination_city"),
            intent.get("start_date"), intent.get("end_date"), total_days, est_flight, selected_hotel.get("id"),
            "SUBMITTED", "PENDING", "PENDING", "PENDING", total_estimated
        ))
        conn.commit()
        cur.close()
    # insert workflow manager step
    user = get_user_by_employee_id(employee_id)
    manager_id = user.get("manager_id")
    if manager_id:
        with get_db_conn() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO approval_workflow (indent_id, approver_id, approval_type, status, created_at)
                VALUES (%s,%s,%s,%s,NOW())
            """, (indent_id, manager_id, "MANAGER", "PENDING"))
            conn.commit()
            cur.close()
    return indent_id

def get_pending_manager_tickets(manager_id: str):
    with get_db_conn() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT ti.indent_id, ti.employee_id, u.name, ti.purpose, ti.status, ti.total_estimated_cost
            FROM travel_indents ti
            JOIN users u ON ti.employee_id = u.employee_id
            WHERE u.manager_id = %s AND ti.manager_approval_status = 'PENDING'
        """, (manager_id,))
        rows = cur.fetchall()
        cur.close()
    return [dict(zip(["indent_id","employee_id","employee_name","purpose","status","total_estimated_cost"], r)) for r in rows]

def get_indent_details(indent_id: str):
    with get_db_conn() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT indent_id, employee_id, purpose, source_city, destination_city, start_date, end_date, total_days, total_estimated_cost, status
            FROM travel_indents WHERE indent_id=%s
        """, (indent_id,))
        row = cur.fetchone()
        cur.close()
    if not row:
        return None
    return dict(zip(["indent_id","employee_id","purpose","source_city","destination_city","start_date","end_date","total_days","total_estimated_cost","status"], row))

def approve_manager_ticket(indent_id: str, manager_id: str, comments: str | None = None):
    with get_db_conn() as conn:
        cur = conn.cursor()
        cur.execute("""
            UPDATE travel_indents
            SET is_approval='approved', updated_at=NOW()
            WHERE indent_id=%s
        """, (indent_id,))
        cur.execute("""
            UPDATE approval_workflow
            SET status='APPROVED', comments=%s, approved_at=NOW()
            WHERE indent_id=%s AND approver_id=%s AND approval_type='MANAGER'
        """, (comments, indent_id, manager_id))
        # insert HR step
        cur.execute("SELECT employee_id FROM users WHERE role='hr' AND is_active=TRUE LIMIT 1")
        hr_row = cur.fetchone()
        if hr_row:
            hr_id = hr_row[0]
            cur.execute("""
                INSERT INTO approval_workflow (indent_id, approver_id, approval_type, status, created_at)
                VALUES (%s,%s,%s,%s,NOW())
            """, (indent_id, hr_id, "HR", "PENDING"))
        conn.commit()
        cur.close()

def get_pending_hr_tickets():
    with get_db_conn() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT indent_id, employee_id, purpose, start_date, end_date, total_estimated_cost
            FROM travel_indents
            WHERE manager_approval_status='APPROVED' AND hr_approval_status='PENDING'
        """)
        rows = cur.fetchall()
        cur.close()
    return [dict(zip(["indent_id","employee_id","purpose","start_date","end_date","total_estimated_cost"], r)) for r in rows]

def get_employee_by_indent(indent_id: str):
    with get_db_conn() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT u.employee_id, u.name, u.email, u.grade, u.department
            FROM users u JOIN travel_indents ti ON ti.employee_id = u.employee_id
            WHERE ti.indent_id=%s
        """, (indent_id,))
        row = cur.fetchone()
        cur.close()
    if not row:
        return None
    return dict(zip(["employee_id","name","email","grade","department"], row))

def approve_hr_ticket(indent_id: str, hr_id: str, comments: str | None = None):
    with get_db_conn() as conn:
        cur = conn.cursor()
        cur.execute("""
            UPDATE travel_indents
            SET hr_approval_status='APPROVED', status='HR_APPROVED', updated_at=NOW()
            WHERE indent_id=%s
        """, (indent_id,))
        cur.execute("""
            UPDATE approval_workflow
            SET status='APPROVED', comments=%s, approved_at=NOW()
            WHERE indent_id=%s AND approver_id=%s AND approval_type='HR'
        """, (comments, indent_id, hr_id))
        conn.commit()
        cur.close()

def book_flight(indent_id: str):
    # demo: mark as booked and return booking id
    booking = {"booking_id": f"FL{indent_id[-6:]}", "airline": "Indigo", "flight": "6E-502", "status":"CONFIRMED"}
    with get_db_conn() as conn:
        cur = conn.cursor()
        cur.execute("UPDATE travel_indents SET status='BOOKED' WHERE indent_id=%s", (indent_id,))
        conn.commit()
        cur.close()
    return booking

def book_hotel(indent_id: str):
    booking = {"booking_id": f"HT{indent_id[-6:]}", "hotel": "Tech Park Inn", "status":"CONFIRMED"}
    return booking

# ---------------------------------------------------------
# MANAGER QUERIES
# ---------------------------------------------------------

def fetch_manager_indents(manager_id):
    """Fetch all travel indents for employees reporting to this manager"""
    with get_db_conn() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT ti.*, 
                   u.name AS employee_name,
                   u.email,
                   u.grade,
                   u.department,
                   u.designation
            FROM travel_indents ti
            JOIN users u ON ti.employee_id = u.employee_id
            ORDER BY ti.created_at DESC
        """, (manager_id,))
        rows = cur.fetchall()
        cols = [c[0] for c in cur.description]
        return [dict(zip(cols, r)) for r in rows]


def fetch_manager_pending(manager_id):
    """Fetch only pending approval tickets"""
    with get_db_conn() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT ti.*, 
                   u.name AS employee_name,
                   u.email,
                   u.grade,
                   u.department,
                   u.designation
            FROM travel_indents ti
            JOIN users u ON ti.employee_id = u.employee_id
            WHERE ti.is_approved = 'pending'
            ORDER BY ti.created_at DESC
        """, (manager_id,))
        rows = cur.fetchall()
        cols = [c[0] for c in cur.description]
        return [dict(zip(cols, r)) for r in rows]


def fetch_manager_approved(manager_id):
    """Fetch approved tickets"""
    with get_db_conn() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT ti.*, 
                   u.name AS employee_name,
                   u.email,
                   u.grade,
                   u.department,
                   u.designation
            FROM travel_indents ti
            JOIN users u ON ti.employee_id = u.employee_id
            WHERE ti.is_approved = 'approved'
            ORDER BY ti.created_at DESC
        """, (manager_id,))
        rows = cur.fetchall()
        cols = [c[0] for c in cur.description]
        return [dict(zip(cols, r)) for r in rows]


def approve_indent_manager(indent_id):
    """Mark indent as manager approved"""
    with get_db_conn() as conn:
        cur = conn.cursor()
        cur.execute("""
            UPDATE travel_indents 
            SET is_approved = 'approved',
                updated_at = CURRENT_TIMESTAMP
            WHERE indent_id = %s
        """, (indent_id,))
        conn.commit()
        return True

def fetch_employee_profile(employee_id):
    with get_db_conn() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT employee_id, name, email, grade, department,
                   designation, manager_id, created_at, city, gender
            FROM users
            WHERE employee_id = %s
        """, (employee_id,))
        row = cur.fetchone()
        cols = [c[0] for c in cur.description]
        return dict(zip(cols, row))
