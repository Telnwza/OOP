from pydantic import BaseModel
from typing import Optional, List
from fastapi import FastAPI, HTTPException
from abc import ABC, abstractmethod

##เพิ่ม เก็บ total price ใน booking

app = FastAPI()

class Restaurant:
  coupon_list = []
  member_list = []

  @classmethod
  def add_member(cls, member:Member):
    cls.member_list.append(member)

  @classmethod
  def add_coupon(cls, coupon:Coupon):
    cls.coupon_list.append(coupon)

  @classmethod
  def get_coupon_by_code(cls, code):
    for coupon in cls.coupon_list:
      if code == coupon.code:
        return coupon
    return None
  
class BookingManager:
  booking_list = []

  @classmethod
  def get_member_from_id(cls, booking_id):
    for booking in cls.booking_list:
      if booking.id == booking_id:
        return booking.member
    return None
  
  @classmethod
  def get_event_order_from_id(cls, booking_id):
    booking = cls.get_booking_from_id(booking_id)
    return booking.event_order
  
  @classmethod
  def get_booking_from_id(cls, booking_id):
    for booking in cls.booking_list:
      if booking.id == booking_id:
        return booking
    return None

  @classmethod
  def add_booking(cls, booking):
    cls.booking_list.append(booking)

class Member:
  def __init__(self, id, name) -> None:
    self._id = id
    self._name = name
    self._coupon_list = []

  def add_coupon(self, code):
    coupon = Restaurant.get_coupon_by_code(code)
    self._coupon_list.append([code, "NotUsed"])

  def validate_coupon(self, code):
    for coupon in self._coupon_list:
      if coupon[0] == code and coupon[1] == "NotUsed":
        return True
    return False
  
  def mark_coupon_used(self, code):
    for index, coupon in enumerate(self._coupon_list):
      if coupon[0] == code and coupon[1] == "NotUsed":
        self._coupon_list[index][1] = "Used"
        return True
    return False

class Coupon(ABC):
  def __init__(self, id, code, minimum_price) -> None:
    self._id = id
    self._code = code
    self._minimum_price = minimum_price

  @abstractmethod
  def apply_Coupon(self, base_price:float):
    pass

  @property
  def code(self):
    return self._code

class PercentCoupon(Coupon):
  def __init__(self, id, code, minimum_price, percent) -> None:
    super().__init__(id, code, minimum_price)
    self._percent = percent

  def apply_Coupon(self, base_price:float):
    return base_price*self._percent/100


class Booking:
  def __init__(self, id, member:Member, room_price:float) -> None:
    self._id = id
    self._member = member
    self._room_price = room_price
    self._status = "Pending"
    self._event_order = None
    self._coupon = None

  def add_event_order(self, event_order:EventOrder):
    if self._event_order != None :raise ValueError("Already Have Event Order")
    self._event_order = event_order

  @property
  def status(self):
    return self._status
  
  @status.setter
  def status(self, status):
    self._status = status

  @property
  def coupon(self):
    return self._coupon
  
  @coupon.setter
  def coupon(self, coupon:Coupon):
    self._coupon = coupon

  @property
  def room_price(self):
    return self._room_price
  
  @property
  def member(self):
    return self._member
  
  @property
  def id(self):
    return self._id
  
  @property
  def event_order(self):
    return self._event_order

class EventOrder:
  def __init__(self, id, total_price:float) -> None:
    self._id = id
    self._total_price = total_price
    self._status = "Pending"
  
  @property
  def total_price(self):
    return self._total_price
  
  @property
  def status(self):
    return self._status
  
  @status.setter
  def status(self, status):
    self._status = status

class PaymentGateway:
  def __init__(self) -> None:
    pass

class Log:
  def __init__(self) -> None:
    pass


########## APP ##########

@app.get("/partyroom-payment/base-total/{booking_id}")
async def get_base_total(booking_id: str):
  booking = BookingManager.get_booking_from_id(booking_id)
  event_order = BookingManager.get_event_order_from_id(booking_id)

  if not booking or not event_order:
    raise HTTPException(status_code=404, detail="Booking or Order Not Found")
  
  base_total = booking.room_price + event_order.total_price

  return {
    "booking_id" : booking_id,
    "room_price" : booking.room_price,
    "event_order_price" : event_order.total_price,
    "base_total_price" : base_total
  }

@app.post("/partyroom-payment/apply-coupon")
async def apply_coupon(booking_id:str, coupon_code:str, base_total: float):
  booking = BookingManager.get_booking_from_id(booking_id)
  member = booking.member
  coupon = Restaurant.get_coupon_by_code(coupon_code)
  
  if not isinstance(booking, Booking) or not isinstance(member, Member) or not isinstance(coupon, Coupon):
    raise HTTPException(status_code=404, detail="member or booking not found")
  
  if member.validate_coupon(coupon_code):
    discount_price = coupon.apply_Coupon(base_total)
    total_price = base_total - discount_price
    return {
      "success" : True,
      "discount" : discount_price,
      "total_price" : total_price
    }
  else:
    return {
      "success" : False,
      "discount" : 0,
      "total_price" : base_total
    }

@app.post("/partyroom-payment/confirm-payment")
async def confirm_payment(booking_id:str, strategy):
  payment_success = True

  if payment_success:
    booking = BookingManager.get_booking_from_id(booking_id)
    if not booking:
      raise HTTPException(status_code=404, detail="Booking not found")
    
    booking.status = "In Use"

    if booking.event_order:
      booking.event_order.status = "Queued"

    member = booking.member

    if booking.coupon:
            member.mark_coupon_used(booking.coupon.code)
            
    print(f"Logging transaction for {booking_id}...")

    return {
            "status": "Complete",
            "receipt_id": "REC-999",
            "message": "Payment successful and records updated"
        }
  else:
        return {"status": "Failed", "message": "ShowErrorPaymentInvalid"}
  
######### Mock Data ########

# 1. สร้าง Member
member1 = Member(id="M001", name="Te ComputerEngineer")
Restaurant.add_member(member1)

# 2. สร้าง Coupon และแจกให้ Member
coupon10 = PercentCoupon(id="C001", code="DISCOUNT10", minimum_price=100, percent=10)
Restaurant.add_coupon(coupon10)
member1.add_coupon("DISCOUNT10") # Member คนนี้มีคูปองนี้

# 3. สร้าง Event Order
order1 = EventOrder(id="ORD-001", total_price=500.0)

# 4. สร้าง Booking
booking1 = Booking(id="B001", member=member1, room_price=1000.0)
booking1.add_event_order(order1)

# 5. นำเข้า BookingManager
BookingManager.add_booking(booking1)

print("Mock Data Initialized: Booking ID 'B001' created with Member 'Te' and Coupon 'DISCOUNT10'")
