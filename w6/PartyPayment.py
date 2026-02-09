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
    self._coupon_code_list = []

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
    self._total_price = None

  def add_event_order(self, event_order:EventOrder):
    if self._event_order != None :raise ValueError("Already Have Event Order")
    self._event_order = event_order

  @property
  def total_price(self):
    return self._total_price
  
  @total_price.setter
  def total_price(self, total_price):
    if total_price >= 0:
      self._total_price = total_price

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
  booking.total_price = base_total

  return {
    "booking_id" : booking_id,
    "room_price" : booking.room_price,
    "event_order_price" : event_order.total_price,
    "base_total_price" : base_total
  }

@app.post("/partyroom-payment/apply-coupon")
async def apply_coupon(booking_id:str, coupon_code:str):
  booking = BookingManager.get_booking_from_id(booking_id)
  member = booking.member
  coupon = Restaurant.get_coupon_by_code(coupon_code)
  
  if not isinstance(booking, Booking) or not isinstance(member, Member) or not isinstance(coupon, Coupon):
    raise HTTPException(status_code=404, detail="member or booking not found")
  
  base_total = booking.total_price

  if not base_total:
    raise  HTTPException(status_code=404, detail="didn't get base total yet")
  
  if member.validate_coupon(coupon_code):
    discount_price = coupon.apply_Coupon(base_total)
    total_price = base_total - discount_price
    booking.total_price = total_price
    booking.coupon = coupon
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

  booking = BookingManager.get_booking_from_id(booking_id)
  if not booking:
    raise HTTPException(status_code=404, detail="Booking not found")
  
  if not booking.total_price:
    raise  HTTPException(status_code=404, detail="didn't get base total yet")
  
  total = booking.total_price

  coupon = None
  if booking.coupon:
    coupon = booking.coupon.code

  if payment_success:
    booking.status = "In Use"

    if booking.event_order:
      booking.event_order.status = "Queued"

    member = booking.member

    if booking.coupon:
            member.mark_coupon_used(booking.coupon.code)
            
    print(f"Logging transaction for {booking_id}...")

    return {
            "status": "Complete",
            "toal paid" : total,
            "coupon used" : coupon,
            "receipt_id": "REC-999",
            "message": "Payment successful and records updated"
        }
  else:
        return {"status": "Failed", "message": "ShowErrorPaymentInvalid"}
  
######### Mock Data #########

# Clear existing data
Restaurant.coupon_list = []
Restaurant.member_list = []
BookingManager.booking_list = []

# 1. สร้าง Members
member1 = Member(id="M001", name="Tina Tate")
Restaurant.add_member(member1)
member2 = Member(id="M002", name="Danielle Moore")
Restaurant.add_member(member2)
member3 = Member(id="M003", name="Gabriel Newman")
Restaurant.add_member(member3)
member4 = Member(id="M004", name="Kelsey Orozco")
Restaurant.add_member(member4)
member5 = Member(id="M005", name="Michael Williams")
Restaurant.add_member(member5)
member6 = Member(id="M006", name="Jessica Williams")
Restaurant.add_member(member6)
member7 = Member(id="M007", name="David Cannon")
Restaurant.add_member(member7)
member8 = Member(id="M008", name="Melanie Macdonald")
Restaurant.add_member(member8)
member9 = Member(id="M009", name="Stacey Oconnor")
Restaurant.add_member(member9)
member10 = Member(id="M010", name="Christine Tran")
Restaurant.add_member(member10)
member11 = Member(id="M011", name="Andrew Ponce")
Restaurant.add_member(member11)
member12 = Member(id="M012", name="Christopher Kelley")
Restaurant.add_member(member12)
member13 = Member(id="M013", name="Joseph Williams")
Restaurant.add_member(member13)
member14 = Member(id="M014", name="Michael Williams")
Restaurant.add_member(member14)
member15 = Member(id="M015", name="Jessica Smith")
Restaurant.add_member(member15)
member16 = Member(id="M016", name="Krystal Williams")
Restaurant.add_member(member16)
member17 = Member(id="M017", name="Daniel Miller")
Restaurant.add_member(member17)
member18 = Member(id="M018", name="Michael Johnson")
Restaurant.add_member(member18)
member19 = Member(id="M019", name="Sara Farrell")
Restaurant.add_member(member19)
member20 = Member(id="M020", name="Michael Velez")
Restaurant.add_member(member20)

# 2. สร้าง Coupons
coupon1 = PercentCoupon(id="C001", code="SAVE43P1", minimum_price=500, percent=22)
Restaurant.add_coupon(coupon1)
coupon2 = PercentCoupon(id="C002", code="SAVE43P2", minimum_price=200, percent=36)
Restaurant.add_coupon(coupon2)
coupon3 = PercentCoupon(id="C003", code="SAVE35P3", minimum_price=100, percent=21)
Restaurant.add_coupon(coupon3)
coupon4 = PercentCoupon(id="C004", code="SAVE26P4", minimum_price=200, percent=14)
Restaurant.add_coupon(coupon4)
coupon5 = PercentCoupon(id="C005", code="SAVE47P5", minimum_price=100, percent=35)
Restaurant.add_coupon(coupon5)
coupon6 = PercentCoupon(id="C006", code="SAVE12P6", minimum_price=500, percent=28)
Restaurant.add_coupon(coupon6)
coupon7 = PercentCoupon(id="C007", code="SAVE30P7", minimum_price=100, percent=31)
Restaurant.add_coupon(coupon7)
coupon8 = PercentCoupon(id="C008", code="SAVE12P8", minimum_price=100, percent=23)
Restaurant.add_coupon(coupon8)
coupon9 = PercentCoupon(id="C009", code="SAVE38P9", minimum_price=500, percent=24)
Restaurant.add_coupon(coupon9)
coupon10 = PercentCoupon(id="C010", code="SAVE17P10", minimum_price=200, percent=24)
Restaurant.add_coupon(coupon10)

# 3. สร้าง Bookings, Event Orders และแจก Coupon ให้ Member
order1 = EventOrder(id="ORD-001", total_price=968.96)
booking1 = Booking(id="B001", member=member19, room_price=1576.9)
booking1.add_event_order(order1)
member19.add_coupon("SAVE17P10")
BookingManager.add_booking(booking1)

order2 = EventOrder(id="ORD-002", total_price=983.8)
booking2 = Booking(id="B002", member=member1, room_price=1717.88)
booking2.add_event_order(order2)
member1.add_coupon("SAVE12P8")
BookingManager.add_booking(booking2)

order3 = EventOrder(id="ORD-003", total_price=487.89)
booking3 = Booking(id="B003", member=member5, room_price=804.8)
booking3.add_event_order(order3)
member5.add_coupon("SAVE43P2")
BookingManager.add_booking(booking3)

order4 = EventOrder(id="ORD-004", total_price=264.4)
booking4 = Booking(id="B004", member=member19, room_price=1588.18)
booking4.add_event_order(order4)
member19.add_coupon("SAVE38P9")
BookingManager.add_booking(booking4)

order5 = EventOrder(id="ORD-005", total_price=221.78)
booking5 = Booking(id="B005", member=member12, room_price=1687.6)
booking5.add_event_order(order5)
member12.add_coupon("SAVE43P1")
BookingManager.add_booking(booking5)

order6 = EventOrder(id="ORD-006", total_price=213.9)
booking6 = Booking(id="B006", member=member1, room_price=1387.97)
booking6.add_event_order(order6)
member1.add_coupon("SAVE47P5")
BookingManager.add_booking(booking6)

order7 = EventOrder(id="ORD-007", total_price=415.8)
booking7 = Booking(id="B007", member=member20, room_price=1557.49)
booking7.add_event_order(order7)
member20.add_coupon("SAVE43P2")
BookingManager.add_booking(booking7)

order8 = EventOrder(id="ORD-008", total_price=714.77)
booking8 = Booking(id="B008", member=member10, room_price=1063.95)
booking8.add_event_order(order8)
member10.add_coupon("SAVE30P7")
BookingManager.add_booking(booking8)

order9 = EventOrder(id="ORD-009", total_price=233.1)
booking9 = Booking(id="B009", member=member2, room_price=1289.43)
booking9.add_event_order(order9)
member2.add_coupon("SAVE38P9")
BookingManager.add_booking(booking9)

order10 = EventOrder(id="ORD-010", total_price=575.64)
booking10 = Booking(id="B010", member=member18, room_price=1756.12)
booking10.add_event_order(order10)
member18.add_coupon("SAVE35P3")
BookingManager.add_booking(booking10)

order11 = EventOrder(id="ORD-011", total_price=644.02)
booking11 = Booking(id="B011", member=member1, room_price=1626.36)
booking11.add_event_order(order11)
member1.add_coupon("SAVE30P7")
BookingManager.add_booking(booking11)

order12 = EventOrder(id="ORD-012", total_price=462.63)
booking12 = Booking(id="B012", member=member2, room_price=1686.04)
booking12.add_event_order(order12)
member2.add_coupon("SAVE17P10")
BookingManager.add_booking(booking12)

order13 = EventOrder(id="ORD-013", total_price=417.48)
booking13 = Booking(id="B013", member=member9, room_price=1836.72)
booking13.add_event_order(order13)
member9.add_coupon("SAVE47P5")
BookingManager.add_booking(booking13)

order14 = EventOrder(id="ORD-014", total_price=800.75)
booking14 = Booking(id="B014", member=member15, room_price=1143.91)
booking14.add_event_order(order14)
member15.add_coupon("SAVE12P8")
BookingManager.add_booking(booking14)

order15 = EventOrder(id="ORD-015", total_price=873.34)
booking15 = Booking(id="B015", member=member8, room_price=1434.98)
booking15.add_event_order(order15)
member8.add_coupon("SAVE26P4")
BookingManager.add_booking(booking15)

order16 = EventOrder(id="ORD-016", total_price=630.93)
booking16 = Booking(id="B016", member=member19, room_price=629.98)
booking16.add_event_order(order16)
member19.add_coupon("SAVE12P6")
BookingManager.add_booking(booking16)

order17 = EventOrder(id="ORD-017", total_price=480.12)
booking17 = Booking(id="B017", member=member8, room_price=1913.41)
booking17.add_event_order(order17)
member8.add_coupon("SAVE47P5")
BookingManager.add_booking(booking17)

order18 = EventOrder(id="ORD-018", total_price=339.1)
booking18 = Booking(id="B018", member=member10, room_price=574.63)
booking18.add_event_order(order18)
member10.add_coupon("SAVE43P2")
BookingManager.add_booking(booking18)

order19 = EventOrder(id="ORD-019", total_price=947.81)
booking19 = Booking(id="B019", member=member13, room_price=1240.26)
booking19.add_event_order(order19)
member13.add_coupon("SAVE12P6")
BookingManager.add_booking(booking19)

order20 = EventOrder(id="ORD-020", total_price=446.01)
booking20 = Booking(id="B020", member=member17, room_price=1868.51)
booking20.add_event_order(order20)
member17.add_coupon("SAVE43P1")
BookingManager.add_booking(booking20)

print(f"Mock Data Initialized: {len(Restaurant.member_list)} members, {len(Restaurant.coupon_list)} coupons, and {len(BookingManager.booking_list)} bookings created.")

