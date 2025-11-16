from src.db.travel_queries import approve_manager_ticket, approve_hr_ticket, book_flight, book_hotel

def manager_approve(indent_id, manager_id, comments=None):
    approve_manager_ticket(indent_id, manager_id, comments)
    return {"status": "MANAGER_APPROVED", "indent_id": indent_id}

def hr_approve_and_book(indent_id, hr_id, comments=None, do_booking=True):
    approve_hr_ticket(indent_id, hr_id, comments)
    result = {"status":"HR_APPROVED","indent_id":indent_id}
    if do_booking:
        flight = book_flight(indent_id)
        hotel = book_hotel(indent_id)
        result.update({"flight": flight, "hotel": hotel})
    return result
