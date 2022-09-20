import database as db
import datetime
import authengine

database = db.Database("data/database.json")


class Error(Exception):
    def __init__(self, message, code=400):
        self.message = message
        self.code = code


class BookingSchema:
    booking_id: str
    created: int = datetime.datetime.timestamp(datetime.datetime.now())
    name: str
    start: int
    end: int
    location: str
    description: str


def get_bookings(auth_username: str, auth_token: str, username: str, booking_id: str | None = None) -> \
        BookingSchema | list[BookingSchema] | Error:
    """
        Gets a booking by its id, or all if no id is provided.
        Users can get the bookings of themselves, and anyone of a lower level.
    """
    to_fetch = username or auth_username
    if authengine.is_user_logged_in(auth_username, auth_token):
        if authengine.get_privilege_level(auth_username) > authengine.get_privilege_level(to_fetch) or \
                auth_username == to_fetch:
            bookings = database.get(to_fetch)
            if not bookings:
                return Error("No bookings found.", 404)
            if booking_id and booking_id in bookings:
                return bookings[booking_id]
            return bookings
        return Error("You do not have permission to view this user's bookings.", 403)
    return Error("You are not logged in.", 401)


def add_booking(auth_username: str, auth_token: str, username: str, booking: BookingSchema) -> int | Error:
    """
        Adds a booking to the database.
        Users can add bookings to themselves, and anyone of a lower level.
    """
    if authengine.is_user_logged_in(auth_username, auth_token):
        if authengine.get_privilege_level(auth_username) > authengine.get_privilege_level(username) or \
                auth_username == username:
            current_data = database.get(username)
            if not current_data:
                database.post(username, [booking])
                return 200
            for each_booking in current_data:
                if each_booking == booking or each_booking.booking_id == booking.booking_id:
                    return Error("Booking already exists.", 409)
            current_data.append = booking
            database.post(username, current_data)
            return 200
        return Error("You do not have permission to add a booking to this user.", 403)
    return Error("You are not logged in.", 401)


def delete_booking(auth_username: str, auth_token: str, username: str, booking_id: str) -> int | Error:
    """
        Deletes a booking from the database.
        Users can delete bookings from themselves, and anyone of a lower level.
    """
    if authengine.is_user_logged_in(auth_username, auth_token):
        if authengine.get_privilege_level(auth_username) > authengine.get_privilege_level(username) or \
                auth_username == username:
            current_data = database.get(username)
            if not current_data:
                return Error("No bookings found.", 404)
            for each_booking in current_data:
                if each_booking.booking_id == booking_id:
                    current_data.remove(each_booking)
                    database.post(username, current_data)
                    return 200
            return Error("Booking not found.", 404)
        return Error("You do not have permission to delete a booking from this user.", 403)
    return Error("You are not logged in.", 401)


def edit_booking(auth_username: str, auth_token: str, username: str, booking_id: str, booking: BookingSchema) -> int | Error:
    """
        Edits a booking in the database.
        Users can edit bookings in themselves, and anyone of a lower level.
    """
    if authengine.is_user_logged_in(auth_username, auth_token):
        if authengine.get_privilege_level(auth_username) > authengine.get_privilege_level(username) or \
                auth_username == username:
            current_data = database.get(username)
            if not current_data:
                return Error("No bookings found.", 404)
            for each_booking in current_data:
                if each_booking.booking_id == booking_id:
                    current_data.remove(each_booking)
                    current_data.append(booking)
                    database.post(username, current_data)
                    return 200
            return Error("Booking not found.", 404)
        return Error("You do not have permission to edit a booking from this user.", 403)
    return Error("You are not logged in.", 401)

