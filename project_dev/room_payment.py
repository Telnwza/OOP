from __future__ import annotations
from typing import Optional, List, Tuple, Dict, Any
from fastapi import FastAPI, HTTPException, Query
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from enum import Enum
from fastmcp import FastMCP
import uuid
import random

app = FastAPI()
mcp = FastMCP("PartyRoomPayment System")

# --- Enums ---
class Status(Enum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"

class OrderType(Enum):
    GENERAL = "General"
    DELIVERY = "Delivery"
    EVENT = "Event"

class DeliveryPlatformName(Enum):
    GRAB_FOOD = "GrabFood"
    LINEMAN = "LineMan"

class OrderStatus(Enum):
    PENDING = "Pending"
    PLACED = "Placed"
    PAID = "Paid"
    COOKING = "Cooking"
    READY_TO_PICKUP = "Ready"      
    COMPLETED = "Completed"
    CANCELED = "Canceled"

class EventOrderStatus(Enum):
    PENDING = "Pending"
    QUEUED = "Queued"

class BookingStatus(Enum):
    PENDING = "Pending"
    IN_USE = "In Use"
    PAID = "Paid"

class RoomStatus(Enum):
    AVAILABLE = "Available"
    RESERVED = "Reserved"
    IN_USE = "In-Use"
    CLEANING = "Cleaning"

class RoomType(Enum):
    VIP = "VIP"
    STANDARD = "Standard"
    HALL = "Hall"

class MemberTier(Enum):
    BRONZE = "Bronze"
    SILVER = "Silver"
    GOLD = "Gold"

class CouponStatus(Enum):
    AVAILABLE = "Available"
    NOT_AVAILABLE = "Not Available"

class StaffRole(Enum):
    PartyStaff = "Party Staff"

# --- Utilities ---
class SimulationClock:
    _current_time = datetime.now()

    @classmethod
    def set_time(cls, new_time: datetime):
        cls._current_time = new_time

    @classmethod
    def get_time(cls):
        return cls._current_time

# --- Core Classes ---
class Coupon(ABC):
    def __init__(self, id, code, minimum_price) -> None:
        self._id = id
        self._code = code
        self._minimum_price = minimum_price
        self._status: CouponStatus = CouponStatus.AVAILABLE

    @property
    def minimum_price(self):
        return self._minimum_price

    @property
    def status(self):
        return self._status

    @property
    def code(self):
        return self._code

    def is_applicable(self, base_price: float) -> bool:
        return base_price >= self._minimum_price

    @abstractmethod
    def apply_coupon(self, base_price: float) -> float:
        pass

    def mark_as_used(self):
        self._status = CouponStatus.NOT_AVAILABLE

class PercentCoupon(Coupon):
    def __init__(self, id, code, minimum_price, percent) -> None:
        super().__init__(id, code, minimum_price)
        if not (0 <= percent <= 100):
            raise ValueError("Percent must be in range 0-100")
        self._percent = percent

    def apply_coupon(self, base_price: float) -> float:
        if self.is_applicable(base_price):
            return base_price * (self._percent / 100)
        raise ValueError(f"Does Not Meet Minimum Price (Min: {self._minimum_price})")
        return 0.0

class Transaction:
    def __init__(self, target_id: str, amount: float, strategy: str, status: str, payment_id: str, coupon: Optional[Coupon] = None, order_type: OrderType = OrderType.GENERAL, staff_id: str = "SYSTEM"):
      self._id = f"TXN-{uuid.uuid4().hex[:12].upper()}"
      self._target_id = target_id
      self._amount = amount
      self._strategy = strategy
      self._status = status
      self._payment_id = payment_id
      self._coupon = coupon
      self._timestamp = SimulationClock.get_time()
      self._order_type = order_type
      self._staff_id = staff_id

    def mark_success(self): self._status = Status.SUCCESS
    def mark_failed(self): self._status = Status.FAILED

    @property
    def id(self): return self._id
    @property
    def timestamp(self): return self._timestamp
    @property
    def status(self): return self._status
    @property
    def amount(self): return self._amount
    @property
    def strategy(self): return self._strategy
    @property
    def coupon(self): return self._coupon
    @property
    def target_id(self): return self._target_id
    @property
    def order_type(self): return self._order_type
    @property
    def staff_id(self): return self._staff_id

class User:
    def __init__(self, id: str, name: str, phone: str = ""):
        self._id = id
        self._name = name
        self._phone = phone

    @property
    def id(self):
        return self._id
    
    @property
    def name(self):
        return self._name

class Staff(User):
    def __init__(self, id: str, name: str, role: StaffRole):
        super().__init__(id, name)
        self.role = role

class PartyStaff(Staff):
    def __init__(self, id: str, name: str):
        super().__init__(id, name, role=StaffRole.PartyStaff)

class Customer(User):
    def __init__(self, id: str, name: str):
        super().__init__(id, name)

class Receipt:
  def __init__(self, transaction: Transaction, source_object):
    self._transaction = transaction
    self._source = source_object

  def generate(self):
    bill_info = self._source.get_bill_info()
    discounted_amount = bill_info["total_base_price"] - self._transaction.amount
    coupon_code = self._transaction.coupon.code if self._transaction.coupon else "None"

    return {
      "receipt_no": self._transaction.id,
      "date": self._transaction.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
      "merchant": "Knight Chicken Fast Food Co.",
      "order_type": self._transaction.order_type.value,
      "customer": bill_info["customer_name"],
      "items": bill_info["items"],
      "total_base_price": bill_info["total_base_price"],
      "discount_coupon": coupon_code,
      "deposit_deducted": bill_info["deposit_deducted"],
      "discount_amount": discounted_amount,
      "final_amount_due": self._transaction.amount,
      "payment_method": self._transaction.strategy,
      "status": "PAID"
    }

class Member(Customer):
    def __init__(self, id: str, name: str, tier: MemberTier):
        super().__init__(id, name)
        self._coupon_list: List[Coupon] = [] 
        self._receipt_list: List[Receipt] = []
        self._tier = tier

    def add_receipt(self, receipt: Receipt):
        self._receipt_list.append(receipt)

    def add_coupon(self, coupon: Coupon):
        self._coupon_list.append(coupon)

    def get_coupon_by_code(self, code: str):
        for coupon in self._coupon_list:
            if coupon.code == code:
                return coupon
        return None
    
    @property
    def tier(self):
        return self._tier

class Food:
    def __init__(self, name: str, price: float):
        self._name = name
        self._price = price
    
    @property
    def name(self): return self._name
    @property
    def price(self): return self._price

    def __str__(self):
        return f"Name : {self.name}, Price : {self.price}"

class EventOrder:
    def __init__(self, id) -> None:
        self._id = id
        self._total_price = 0.0
        self._status: EventOrderStatus = EventOrderStatus.PENDING
        self._food_list: List[Food] = []

    def add_food(self, food: Food):
        self._food_list.append(food)
        self._total_price += food.price

    @property
    def food_list(self): return self._food_list
    @property
    def id(self): return self._id
    @property
    def total_price(self): return self._total_price
    @property
    def status(self): return self._status
    @status.setter
    def status(self, status: EventOrderStatus): self._status = status

class Room:
    def __init__(self, room_id: str, room_type: RoomType):
        self._room_id = room_id
        self._room_type = room_type
        self._status: RoomStatus = RoomStatus.AVAILABLE
        if room_type == RoomType.HALL:
            self._capacity = 100
            self._price_per_hour = 5000.0
        elif room_type == RoomType.VIP:
            self._capacity = 20
            self._price_per_hour = 2000.0
        elif room_type == RoomType.STANDARD:
            self._capacity = 10
            self._price_per_hour = 500.0
        else:
            raise ValueError("Unknown room type")
    
    def mark_room_in_use(self):
        self._status = RoomStatus.IN_USE
    
    @property
    def capacity(self): return self._capacity
    @property
    def price_per_hour(self): return self._price_per_hour
    @property
    def id(self): return self._room_id
    @property
    def type(self): return self._room_type
    
class Booking:
    def __init__(self, booking_id, member: Member, room: Room, start_time: datetime, hours: int) -> None:
        self._booking_id = booking_id
        self._member = member
        self._room = room
        self._start_time = start_time
        self._end_time = start_time + timedelta(hours=hours)
        self._hours = hours
        self._status: BookingStatus = BookingStatus.PENDING
        self._event_order: Optional[EventOrder] = None
        self._deposit_status = "Unpaid"
        self._room_price = self.room.price_per_hour * self.hours
        self._required_deposit = self._room_price  * 0.5
        self._total_price = 0.0
        self._coupon_used: Optional[Coupon] =  None

    def calculate_payment_details(self, coupon: Optional[Coupon] = None):
        member = self.member
        room = self.room
        hours = self.hours
        start_time = self._start_time
        end_time = self._end_time
        room_price = self._room_price
        deposit_price = self._required_deposit
        discount = 0.0

        if not self.event_order:
            raise ValueError("No Order Yet")
        
        food_list = self.event_order.food_list
        food_list_serialized = [{"name": f.name, "price": f.price} for f in food_list]
        order_price = self.event_order.total_price

        base_price = order_price + room_price - deposit_price
        
        if coupon:
            if coupon.status == CouponStatus.NOT_AVAILABLE:
                raise ValueError("Coupon is Not Available")
            discount = coupon.apply_coupon(base_price)
            self._coupon_used = coupon
        else:
            self._coupon_used = None

        final_price = base_price - discount
        
        if final_price < 0:
            final_price = 0.0
        
        self._total_price = final_price
        
        return {
            "Member" : {
                "Name" : member.name,
                "Tier" : member.tier.value
            },
            "Booking Id" : self.id,
            "Item": {
                "Room" : {
                    "Id" : room.id,
                    "Capacity" : room.capacity,
                    "Price Per Hours" : room.price_per_hour,
                    "Start Time" : start_time.strftime("%H:%M"),
                    "End Time" : end_time.strftime("%H:%M"),
                    "Total Hours" : hours,
                    "Deposit" : deposit_price,
                    "Total Room Price" : room_price - deposit_price
                },
                "Order" : {
                    "Food" : food_list_serialized,
                    "Total Order Price" : order_price
                }
            },
            "Total Price Before Discount" : base_price,
            "Coupon Code" : coupon.code if coupon else "None",
            "Discounted" : discount,
            "Total Price" : final_price
        }
            
    def add_event_order(self, event_order: EventOrder):
        if self._event_order is not None:
            raise ValueError("Already Have Event Order")
        self._event_order = event_order
    
    def get_bill_info(self):
        items = [
            {"name": f"Room Charge ({self.room.id})", "Total Hours": self.hours, "price": self.room_price}
        ]
        if self.event_order:
             food_list = self.event_order.food_list
             food_list_serialized = [{"name": f.name, "price": f.price} for f in food_list]
             items.append({"name": "Event Food", 
                           "Food": food_list_serialized
                           })

        return {
            "customer_name": self._member.name,
            "items": items,
            "total_base_price": self.room_price + (self._event_order.total_price if self._event_order else 0),
            "deposit_deducted": self._required_deposit
        }

    @property
    def coupon_used(self): return self._coupon_used
    @property
    def total_price(self): return self._total_price
    @property
    def hours(self): return self._hours
    @property
    def room(self): return self._room
    @property
    def room_price(self): return self._room_price
    @property
    def id(self): return self._booking_id
    @property
    def member(self): return self._member
    @property
    def status(self) -> BookingStatus: return self._status
    @status.setter
    def status(self, val: BookingStatus): self._status = val
    @property
    def event_order(self): return self._event_order

class Restaurant:
    transaction_list: List[Transaction] = []
    coupon_list: List[Coupon] = []
    members: List[Member] = []
    rooms: List[Room] = []
    staff_list: List[PartyStaff] = []

    @classmethod
    def get_staff_by_id(cls, staff_id: str):
        for staff in cls.staff_list:
            if staff.id == staff_id:
                return staff
        return None
    
    @classmethod
    def add_log(cls, transaction: Transaction):
      cls.transaction_list.append(transaction)
      print(f"[SYSTEM LOG] {transaction.timestamp} | {transaction.id} | {transaction.status} | {transaction.amount} THB | Staff: {transaction.staff_id}")

    @classmethod
    def add_member(cls, member: Member):
        cls.members.append(member)

    @classmethod
    def add_coupon(cls, coupon: Coupon):
        cls.coupon_list.append(coupon)

    @classmethod
    def get_coupon_by_code(cls, code: str) -> Optional[Coupon]:
        for coupon in cls.coupon_list:
            if code == coupon.code:
                return coupon
        return None

class BookingManager:
    _booking_list: List[Booking] = []

    @classmethod
    def add_booking(cls, booking: Booking):
        cls._booking_list.append(booking)

    @classmethod
    def get_booking_from_id(cls, booking_id: str) -> Optional[Booking]:
      for booking in cls._booking_list:
        if booking.id == booking_id:
          return booking
      return None
    
class PaymentStrategy(ABC):
    @classmethod
    def get_strategy(cls, name: str):
      for strategy_cls in PaymentStrategy.__subclasses__():
        try:
          if strategy_cls.get_name().lower() == name.lower():
            return strategy_cls
        except NotImplementedError:
          continue
      raise HTTPException(status_code=400, detail=f"Unknown Strategy: {name}")
    
    @staticmethod
    @abstractmethod
    def get_name() -> str:
      pass
    @staticmethod
    @abstractmethod
    def pay(amount: float) -> Tuple[bool, str]:
      pass

class QRCode(PaymentStrategy):
    @staticmethod
    def get_name() -> str: return "QRCode"
    @staticmethod
    def pay(amount: float) -> Tuple[bool, str]:
      success = random.random() < 0.90
      if success : return True, f"REC-{uuid.uuid4().hex[:8].upper()}"
      return False, "Payment Declined"

class CreditCard(PaymentStrategy):
    @staticmethod
    def get_name() -> str: return "CreditCard"
    @staticmethod
    def pay(amount: float) -> Tuple[bool, str]:
      success = random.random() < 0.80
      if success : return True, f"REC-{uuid.uuid4().hex[:8].upper()}"
      return False, "Payment Declined"

class Cash(PaymentStrategy):
    @staticmethod
    def get_name() -> str: return "Cash"
    @staticmethod
    def pay(amount: float) -> Tuple[bool, str]:
      success = random.random() < 0.99
      if success : return True, f"REC-{uuid.uuid4().hex[:8].upper()}"
      return False, "Payment Declined"

# --- Tools / Endpoints ---

@mcp.tool
@app.get("/partyroom-payment/get_booking_info/{booking_id}")
async def get_booking_info(booking_id: str, staff_id: str):
    """
    แสดงข้อมูลรายละเอียดของ booking ทั้งหมด
    รับ booking_id รูปแบบ Bxxx และ staff_id รูปแบบ STxxx
    ดึงข้อมูลรายละเอียดทั้งหมดของ booking ไปแสดง เพื่อถามก่อนยืนยันว่าจะ confirm จ่ายเงินไหม หรือจะใช้คูปองใหม
    """
    booking = BookingManager.get_booking_from_id(booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking Not Found")
    
    if booking.status != BookingStatus.PENDING:
        raise HTTPException(status_code=409, detail="Booking already paid or processed")
    
    staff = Restaurant.get_staff_by_id(staff_id=staff_id)
    if not staff or staff.role != StaffRole.PartyStaff:
        raise HTTPException(status_code=400, detail="Staff Not found or Not Party Staff")
    
    return booking.calculate_payment_details()

@mcp.tool
@app.post("/partyroom-payment/apply_coupon/{booking_id}")
async def apply_coupon(booking_id: str, staff_id: str, coupon_code: str):
    """
    ใช้คูปอง กับ booking
    รับ booking_id รูปแบบ Bxxx และ staff_id รูปแบบ STxxx และ coupon_code
    ดึงข้อมูลรายละเอียดทั้งหมดของ booking หลังใช้คูปแงแล้ว ไปแสดง เพื่อถามก่อนยืนยันว่าจะ confirm จ่ายเงินไหม
    """
    booking = BookingManager.get_booking_from_id(booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking Not Found")
    
    if booking.status != BookingStatus.PENDING:
        raise HTTPException(status_code=409, detail="Booking already paid")
    
    staff = Restaurant.get_staff_by_id(staff_id=staff_id)
    if not staff or staff.role != StaffRole.PartyStaff:
        raise HTTPException(status_code=400, detail="Staff Not found or Not Party Staff")
    
    coupon = booking.member.get_coupon_by_code(coupon_code)
    if not coupon:
        raise HTTPException(status_code=404, detail="Coupon Not Found in Member Wallet")

    try:
        return booking.calculate_payment_details(coupon)
    except ValueError as e:
         raise HTTPException(status_code=400, detail=str(e))

@mcp.tool
@app.post("/partyroom-payment/confrim_pay/{booking_id}")
async def pay_booking(booking_id: str, staff_id: str, strategy: str):
    """
    ยืนยันการชำระเงิน ของ booking โดยควรจะ ดูรายละเอียดก่อนชำระเงิน
    รับ booking_id รูปแบบ Bxxx และ staff_id รูปแบบ STxxx และ 
    strategy ช่องทางการชำระเงิน มี creditcard , cash , qrcode
    """
    booking = BookingManager.get_booking_from_id(booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking Not Found")
    
    if booking.status != BookingStatus.PENDING:
        raise HTTPException(status_code=409, detail="Booking already paid")
    
    staff = Restaurant.get_staff_by_id(staff_id=staff_id)
    if not staff or staff.role != StaffRole.PartyStaff:
        raise HTTPException(status_code=400, detail="Staff Not found or Not Party Staff")
    
    if booking.total_price == 0.0 and booking.room_price > 0:
        booking.calculate_payment_details()

    total_price = booking.total_price
    
    try:
        payment_strategy = PaymentStrategy.get_strategy(strategy)
    except HTTPException as e:
        raise e

    success, receipt_or_msg = payment_strategy.pay(total_price)

    transaction = Transaction(
        target_id=booking_id,
        amount=total_price,
        strategy=strategy.lower(),
        status="PENDING",
        payment_id=receipt_or_msg,
        coupon=booking.coupon_used,
        order_type=OrderType.EVENT,
        staff_id=staff_id
    )

    if success:
        booking.status = BookingStatus.PAID
        if booking.event_order:
            booking.event_order.status = EventOrderStatus.QUEUED
        booking.room.mark_room_in_use()
        
        member = booking.member
        if booking.coupon_used:
          booking.coupon_used.mark_as_used()

        transaction.mark_success()
        Restaurant.add_log(transaction)

        receipt = Receipt(transaction, booking)
        member.add_receipt(receipt)
        return receipt.generate()
    
    else:
        transaction.mark_failed()
        Restaurant.add_log(transaction)
        raise HTTPException(status_code=402, detail=f"Payment Failed: {receipt_or_msg}")

# --- MOCK DATA GENERATION ---

print("Initializing Mock Data...")

# 1. Setup Staff
staff1 = PartyStaff("ST001", "Alice Manager")
staff2 = PartyStaff("ST002", "Bob Service")
Restaurant.staff_list.extend([staff1, staff2])

# 2. Setup Foods
f1 = Food("Chicken Bucket Large", 599.0)
f2 = Food("Spicy Wings Set", 299.0)
f3 = Food("French Fries Tower", 159.0)
f4 = Food("Coke Pitcher", 90.0)
f5 = Food("Luxury Party Platter", 1200.0)

# 3. Setup Rooms
r1 = Room("R001", RoomType.VIP)      # 2000/hr
r2 = Room("R002", RoomType.STANDARD) # 500/hr
r3 = Room("R003", RoomType.HALL)     # 5000/hr
Restaurant.rooms.extend([r1, r2, r3])

# 4. Setup Coupons
# Coupon 1: 10% off, min spend 1000
c1 = PercentCoupon("CP001", "DISCOUNT10", 1000.0, 10.0) 
# Coupon 2: 50% off, min spend 5000
c2 = PercentCoupon("CP002", "BIGPARTY50", 5000.0, 50.0)
Restaurant.add_coupon(c1)
Restaurant.add_coupon(c2)

# 5. Setup Members
m1 = Member("M001", "John Doe", MemberTier.GOLD)
m1.add_coupon(c1) # John has 10% coupon

m2 = Member("M002", "Jane Smith", MemberTier.SILVER)
m2.add_coupon(c2) # Jane has 50% coupon

Restaurant.add_member(m1)
Restaurant.add_member(m2)

# 6. Setup Event Orders & Bookings

# --- Booking 1: John Doe (Standard Room, Small Order) ---
order1 = EventOrder("ORD-101")
order1.add_food(f1) # 599
order1.add_food(f4) # 90
# Total Food: 689

# Room: Standard (500) * 3 hours = 1500
# Total Base: 2189
booking1 = Booking("B001", m1, r2, datetime.now().replace(hour=18, minute=0), 3)
booking1.add_event_order(order1)
BookingManager.add_booking(booking1)

# --- Booking 2: Jane Smith (VIP Room, Big Order) ---
order2 = EventOrder("ORD-102")
order2.add_food(f5) # 1200
order2.add_food(f5) # 1200
order2.add_food(f1) # 599
order2.add_food(f4) # 90
# Total Food: 3089

# Room: VIP (2000) * 4 hours = 8000
# Total Base: 11089
booking2 = Booking("B002", m2, r1, datetime.now().replace(hour=19, minute=0), 4)
booking2.add_event_order(order2)
BookingManager.add_booking(booking2)

print("Mock Data Generated Successfully!")
print("-------------------------------------------------")
print("Available Test Scenarios:")
print("1. [ST001] Get Info for B001 (John): /partyroom-payment/get_booking_info/B001?staff_id=ST001")
print("   -> Try applying coupon 'DISCOUNT10': /partyroom-payment/apply_coupon/B001?staff_id=ST001&coupon_code=DISCOUNT10")
print("   -> Confirm Pay (QRCode): /partyroom-payment/confrim_pay/B001?staff_id=ST001&strategy=QRCode")
print("\n2. [ST001] Get Info for B002 (Jane): /partyroom-payment/get_booking_info/B002?staff_id=ST001")
print("   -> Try applying coupon 'BIGPARTY50': /partyroom-payment/apply_coupon/B002?staff_id=ST001&coupon_code=BIGPARTY50")
print("-------------------------------------------------")

if __name__ == "__main__":
    mcp.run()