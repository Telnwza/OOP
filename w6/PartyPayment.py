from __future__ import annotations
from pydantic import BaseModel
from typing import Optional, List
from fastapi import FastAPI, HTTPException, Query
from abc import ABC, abstractmethod
import uuid
from datetime import datetime, timezone

app = FastAPI()
http://127.0.0.1:8001/
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
    if not booking: return None
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
    self._coupon_code_list = []
    self._receipt_list = []

  def add_receipt(self, receipt):
    self._receipt_list.append(receipt)


  def add_coupon(self, code):
    self._coupon_code_list.append([code, "NotUsed"])

  def validate_coupon(self, code):
    for coupon in self._coupon_code_list:
      if coupon[0] == code and coupon[1] == "NotUsed":
        return True
    return False
  
  def mark_coupon_used(self, code):
    for index, coupon in enumerate(self._coupon_code_list):
      if coupon[0] == code and coupon[1] == "NotUsed":
        self._coupon_code_list[index][1] = "Used"
        return True
    return False

class Coupon(ABC):
  def __init__(self, id, code, minimum_price) -> None:
    self._id = id
    self._code = code
    self._minimum_price = minimum_price

  def is_applicable(self, base_price):
    if base_price < self._minimum_price:
      return False
    return True

  @abstractmethod
  def apply_Coupon(self, base_price:float):
    pass

  @property
  def code(self):
    return self._code

class PercentCoupon(Coupon):
  def __init__(self, id, code, minimum_price, percent) -> None:
    super().__init__(id, code, minimum_price)
    if percent < 0 or percent > 100:
      raise ValueError("Percent must be in range 0-100")
    self._percent = percent

  def apply_Coupon(self, base_price:float):
    if super().is_applicable(base_price):
      return base_price*self._percent/100
    return 0.0


class Booking:
  def __init__(self, id, member:Member, room_price:float) -> None:
    self._id = id
    self._member = member
    self._room_price = room_price
    self._status = "Pending"
    self._event_order = None

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
    @classmethod
    def pay(cls, total_price: float, strategy: PaymentStrategy):
        return strategy.pay(total_price)
    
    @classmethod
    def get_payment_strategy(cls, name: str):
      strategies = {
          "success": SuccessStrategy(),
          "fail": FailStrategy(),
      }
      if name not in strategies:
          raise HTTPException(status_code=400, detail="Unknown strategy")
      return strategies[name]
  
class PaymentStrategy(ABC):
    @abstractmethod
    def pay(self, amount: float):
        pass

class SuccessStrategy(PaymentStrategy):
    def pay(self, amount: float):
        if amount <= 0:
            return False, "Amount is less than 1"
        return True, f"REC-{uuid.uuid4().hex[:8]}"

class FailStrategy(PaymentStrategy):
    def pay(self, amount: float):
        return False, "Payment Declined"

class Log:
  def __init__(self) -> None:
    pass


########## APP ##########
@app.post("/partyroom-payment/pay/{booking_id}")
async def pay(booking_id: str, strategy: str, coupon_code: Optional[str] = Query(default=None)):
  booking = BookingManager.get_booking_from_id(booking_id)
  event_order = BookingManager.get_event_order_from_id(booking_id)
  member = BookingManager.get_member_from_id(booking_id)

  if not isinstance(member, Member):
    raise HTTPException(status_code=404, detail="Member Not Found")

  if not isinstance(booking, Booking) or not isinstance(event_order, EventOrder):
    raise HTTPException(status_code=404, detail="Booking or Order Not Found")
  
  if booking.status != "Pending":
    raise HTTPException(status_code=409, detail="Already Paid")
  
  base_total = booking.room_price + event_order.total_price
  final_total = base_total

  coupon = None
  applied_coupon = False
  
  if coupon_code:
    coupon = Restaurant.get_coupon_by_code(coupon_code)
    if not isinstance(coupon, Coupon):
      raise HTTPException(status_code=404, detail="Coupon Code Not Found")
    
    if member.validate_coupon(coupon_code) and coupon.is_applicable(base_total):
      discount_price = coupon.apply_Coupon(base_total)
      applied_coupon = True
      final_total = base_total - discount_price
      if final_total < 0:
        raise HTTPException(status_code=400, detail="total price can't be below 0")
    else:
      raise HTTPException(status_code=400, detail="Coupon Invalid")
    
  payment_strategy = PaymentGateway.get_payment_strategy(strategy)
  payment_success, payment_deail = payment_strategy.pay(final_total)
  if payment_success:
    if applied_coupon:
      if not member.mark_coupon_used(coupon_code):
        raise HTTPException(status_code=500, detail="Failed to mark coupon used")
    booking.status = "In Use"
    event_order.status = "Queued"

    print(f"Logging transaction for {booking_id}...")
    return {
            "booking_id" : booking_id,
            "status": "Complete",
            "toal_paid" : final_total,
            "coupon_code" : coupon.code if applied_coupon and coupon else None,
            "receipt_id": payment_deail,
            "message": "Payment successful and records updated"
    }
  else:
    raise HTTPException(status_code=400, detail=payment_deail)
    

######### Mock Data #########

# Clear existing data
Restaurant.coupon_list = []
Restaurant.member_list = []
BookingManager.booking_list = []

# Create sample members
member1 = Member(id="M001", name="Alice")
Restaurant.add_member(member1)

member2 = Member(id="M002", name="Bob")
Restaurant.add_member(member2)

# Create sample coupons
coupon1 = PercentCoupon(id="C001", code="SAVE10", minimum_price=100, percent=10)
Restaurant.add_coupon(coupon1)

coupon2 = PercentCoupon(id="C002", code="SAVE20", minimum_price=200, percent=20)
Restaurant.add_coupon(coupon2)

# Create sample bookings and orders
order1 = EventOrder(id="ORD-001", total_price=150.0)
booking1 = Booking(id="B001", member=member1, room_price=200.0)
booking1.add_event_order(order1)
member1.add_coupon("SAVE10")
BookingManager.add_booking(booking1)

order2 = EventOrder(id="ORD-002", total_price=300.0)
booking2 = Booking(id="B002", member=member2, room_price=250.0)
booking2.add_event_order(order2)
member2.add_coupon("SAVE20")
BookingManager.add_booking(booking2)

print(f"Mock Data Initialized: {len(Restaurant.member_list)} members, {len(Restaurant.coupon_list)} coupons, and {len(BookingManager.booking_list)} bookings created.")
