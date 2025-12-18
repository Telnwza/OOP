class Staff:
  def __init__(self, id, name):
    self.__id = id
    self.__name = name

class Room:
  def __init__(self, id, name, cap):
    self.__id = id
    self.__name = name
    self.__cap = cap
    self.__staff = None

  def assign_staff(self, staff):
    if not isinstance(staff, Staff): return 'Error'
    self.__staff = staff
    return 'Done'

class User:
  def __init__(self, id, name):
    self.__id = id
    self.__name = name
    self.__booking_list = []

  def book(self, room, date, timeslot): #09:00-11:00 #2-11-2020
    if not isinstance(room, Room) or not isinstance(date, str) or not isinstance(timeslot, str): return 'Error'
    if len(date.split('-')) != 3 or len(timeslot.split('-')) != 2 : return 'Error'
    try : 
       for x in date.split('-'): int(x)
       for x in timeslot.split('-'):
          for y in x.split(':'): int(y)
    except:
       return 'Error'
    for booking in self.__booking_list:
      if room == booking.get_room() and date == booking.get_date() and timeslot == booking.get_time_slot() and booking.get_status() == 'Booked':
        return 'Already Booked'
    self.__booking_list.append(Booking(room, date, timeslot))
    return 'Done'

  def cancel(self, room, date, timeslot):
    if not isinstance(room, Room) or not isinstance(date, str) or not isinstance(timeslot, str): return 'Error'
    for index, booking in enumerate(self.__booking_list):
      if room == booking.get_room() and date == booking.get_date() and timeslot == booking.get_time_slot() and booking.get_status() == 'Booked':
        self.__booking_list[index].set_status('Cancelled')
        return 'Done'
    return 'Not Found'
  
  def get_total_hours(self):
      total_hours = 0.0
      for booking in self.__booking_list:
        if booking.get_status() != 'Booked' : continue
        time_interval = booking.get_time_slot()
        time = time_interval.split('-')
        time_enter = time[0].split(':')
        time_exit = time[1].split(':')
        time_enter_hours = int(time_enter[0])+int(time_enter[1])/60
        time_exit_hours = int(time_exit[0])+int(time_exit[1])/60
        total_hours += time_exit_hours - time_enter_hours
      return total_hours
  
  def get_active_bookings(self):
    room_list = []
    for booking in self.__booking_list:
      if booking.get_status() == 'Booked':
        room_list.append(booking.get_room())
    return room_list


class Booking:
  def __init__(self, room, date, time_slot):
    self.__room = room
    self.__date = date
    self.__time_slot = time_slot
    self.__status = 'Booked'

  def set_status(self, status):
    self.__status = status

  def get_room(self):
    return self.__room
  
  def get_date(self):
    return self.__date
  
  def get_time_slot(self):
    return self.__time_slot
  
  def get_status(self):
    return self.__status

# =========================
# Test Suite: Meeting Room Booking System
# Spec-based tests (print Expected vs Actual)
# =========================
# Assumption:
# You have implemented these classes in the same file or imported:
#   Staff, Room, User, Booking
# And methods:
#   Room.assign_staff(staff)
#   User.book(room, date, timeslot)
#   User.cancel(room, date, timeslot)
#   User.get_active_bookings()
#   User.get_total_hours()
#
# Return strings exactly:
#   "Done", "Error", "Already Booked", "Not Found"
#
# Note: This test suite tries to be tolerant for get_active_bookings() returning:
#   - list of Booking
#   - list of Room
# It will inspect items to summarize.

def _extract_booking_signature(item):
    """
    Normalize an active-booking item into a readable signature.
    Supports:
      - Booking-like objects with get_room/get_date/get_timeslot or room/date/timeslot attributes
      - Room-like objects (then signature only includes room id/name if available)
    """
    # Booking-like: try getters
    for room_getter, date_getter, slot_getter in [
        ("get_room", "get_date", "get_timeslot"),
        ("room", "date", "timeslot"),
    ]:
        try:
            # getters
            if callable(getattr(item, room_getter, None)) and callable(getattr(item, date_getter, None)) and callable(getattr(item, slot_getter, None)):
                room = getattr(item, room_getter)()
                date = getattr(item, date_getter)()
                slot = getattr(item, slot_getter)()
                return ("BOOKING", _room_label(room), str(date), str(slot))
            # attributes
            if hasattr(item, room_getter) and hasattr(item, date_getter) and hasattr(item, slot_getter):
                room = getattr(item, room_getter)
                date = getattr(item, date_getter)
                slot = getattr(item, slot_getter)
                return ("BOOKING", _room_label(room), str(date), str(slot))
        except Exception:
            pass

    # Room-like
    return ("ROOM", _room_label(item), None, None)

def _room_label(room):
    """Try to make a stable label for Room objects."""
    if room is None:
        return "None"
    # try getters
    for gid, gname in [("get_id", "get_name"), ("get_id", "get_room_name"), ("id", "room_name"), ("id", "name")]:
        try:
            rid = getattr(room, gid)() if callable(getattr(room, gid, None)) else getattr(room, gid, None)
            rname = getattr(room, gname)() if callable(getattr(room, gname, None)) else getattr(room, gname, None)
            if rid is not None and rname is not None:
                return f"{rid}:{rname}"
            if rid is not None:
                return f"{rid}"
            if rname is not None:
                return f"{rname}"
        except Exception:
            continue
    # fallback
    return room.__class__.__name__

def _print_case(title):
    print("\n" + "-" * 60)
    print(title)
    print("-" * 60)

def _show_active(user, label="Active bookings"):
    try:
        active = user.get_active_bookings()
    except Exception as e:
        print(f"{label}: CRASHED ({e})")
        return None

    if not isinstance(active, list):
        print(f"{label}: FAIL (Expected list, got {type(active).__name__})")
        return active

    sigs = [_extract_booking_signature(x) for x in active]
    print(f"{label} count = {len(active)}")
    for i, s in enumerate(sigs, 1):
        kind, room_lbl, date, slot = s
        if kind == "BOOKING":
            print(f"  {i}. {room_lbl} | {date} | {slot}")
        else:
            print(f"  {i}. {room_lbl} (Room-only item)")
    return sigs

def _expect(actual, expected, name):
    ok = (actual == expected)
    print(f"{name}: {actual} (Expected: {expected}) {'PASS' if ok else 'FAIL'}")
    return ok

# =========================
# Run Tests
# =========================
print("=======================================")
print("Testing Meeting Room Booking System")
print("=======================================")

# --- Setup Data ---
staff1 = Staff("S001", "Ms. Admin")
room1 = Room("R101", "Alpha", 8)
room2 = Room("R102", "Beta", 12)

user1 = User("U001", "Te")
user2 = User("U002", "Another User")

_print_case("[Setup] Assign Staff to Rooms")
try:
    r = room1.assign_staff(staff1)
    # allow either None or "Done" (depending on your design)
    if r is None:
        print("Assign staff to room1: PASS (returned None)")
    else:
        print(f"Assign staff to room1: returned '{r}'")
except Exception as e:
    print(f"Assign staff to room1: CRASHED ({e})")

try:
    r = room2.assign_staff(staff1)
    if r is None:
        print("Assign staff to room2: PASS (returned None)")
    else:
        print(f"Assign staff to room2: returned '{r}'")
except Exception as e:
    print(f"Assign staff to room2: CRASHED ({e})")

_print_case("[1] Booking Logic")
res = user1.book(room1, "2025-12-20", "09:00-11:00")
_expect(res, "Done", "1.1 Book R101 09:00-11:00")

res = user1.book(room1, "2025-12-20", "09:00-11:00")
_expect(res, "Already Booked", "1.2 Book same slot again")

res = user1.book(room1, "2025-12-20", "11:00-12:00")
_expect(res, "Done", "1.3 Book different slot same day")

res = user1.book(room2, "2025-12-20", "09:00-11:00")
_expect(res, "Done", "1.4 Book different room same slot")

_show_active(user1, "User1 active bookings (after bookings)")

_print_case("[2] Cancel Logic")
res = user1.cancel(room1, "2025-12-20", "11:00-12:00")
_expect(res, "Done", "2.1 Cancel existing booking")

res = user1.cancel(room1, "2025-12-20", "11:00-12:00")
_expect(res, "Not Found", "2.2 Cancel again (should not exist)")

res = user1.cancel(room1, "2025-12-21", "09:00-11:00")
_expect(res, "Not Found", "2.3 Cancel non-existent date")

_show_active(user1, "User1 active bookings (after cancels)")

_print_case("[3] Robustness: Invalid Types (must not crash)")
try:
    res = user1.book("R101", "2025-12-20", "13:00-14:00")
    _expect(res, "Error", "3.1 Book with room as string")
except Exception as e:
    print(f"3.1 Book with room as string: CRASHED ({e})")

try:
    res = user1.cancel(123, "2025-12-20", "09:00-11:00")
    _expect(res, "Error", "3.2 Cancel with room as int")
except Exception as e:
    print(f"3.2 Cancel with room as int: CRASHED ({e})")

_print_case("[4] Independence Between Users")
res = user2.book(room1, "2025-12-20", "09:00-11:00")
# NOTE: This spec checks duplicate per-user (not global conflicts).
# So user2 can book same room/time independently.
_expect(res, "Done", "4.1 User2 book same room/time (per-user duplicate rule)")

_show_active(user2, "User2 active bookings")

_print_case("[5] Total Hours Calculation (active only)")
# For user1 currently active (based on above):
# user1 booked:
#   room1 09:00-11:00  -> 2h (active)
#   room1 11:00-12:00  -> cancelled
#   room2 09:00-11:00  -> 2h (active)
# Expected total = 4.0 (if you compute hours as float)
try:
    total = user1.get_total_hours()
    print(f"User1 total hours: {total} (Expected: 4 or 4.0)")
except Exception as e:
    print(f"User1 total hours: CRASHED ({e})")

# For user2:
#   room1 09:00-11:00 -> 2h
try:
    total = user2.get_total_hours()
    print(f"User2 total hours: {total} (Expected: 2 or 2.0)")
except Exception as e:
    print(f"User2 total hours: CRASHED ({e})")

print("\n=======================================")
print("Test suite finished.")
print("=======================================")