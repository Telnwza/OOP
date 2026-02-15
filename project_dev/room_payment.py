from __future__ import annotations
from typing import Optional, List, Tuple
from fastapi import FastAPI, HTTPException, Query
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from fastmcp import FastMCP
import uuid
import random

mcp = FastMCP()

class OrderType(Enum):
    DELIVERY = "Delivery"
    EVENT = "Event"

class OrderStatus(Enum):
    PLACED = "Placed"
    PAID = "Paid"
    COOKING = "Cooking"
    READY_TO_PICKUP = "Ready"      
    COMPLETED = "Completed"
    CANCLED = "Cancled"  

class CouponStatus(Enum):
    USED = "Used"
    AVALIBLE = "Avalible"

class EventOrderStatus(Enum):
    PENDING = "Pending"
    QUEUED = "Queued"

class BookingStatus(Enum):
    PENDING = "Pending"
    IN_USE = "In Use"
    

class Coupon(ABC):
    def __init__(self, id, code, minimum_price) -> None:
        self._id = id
        self._code = code
        self._minimum_price = minimum_price

    @property
    def code(self):
        return self._code

    def is_applicable(self, base_price: float) -> bool:
        return base_price >= self._minimum_price

    @abstractmethod
    def apply_coupon(self, base_price: float) -> float:
        pass

class PercentCoupon(Coupon):
    def __init__(self, id, code, minimum_price, percent) -> None:
        super().__init__(id, code, minimum_price)
        if not (0 <= percent <= 100):
            raise ValueError("Percent must be in range 0-100")
        self._percent = percent

    def apply_coupon(self, base_price: float) -> float:
        if self.is_applicable(base_price):
            return base_price * (self._percent / 100)
        return 0.0

class Member:
    def __init__(self, id, name) -> None:
        self._id = id
        self._name = name
        self._coupon_list: List[List[str | CouponStatus]] = [] 

    def add_coupon(self, code: str):
        self._coupon_list.append([code, CouponStatus.AVALIBLE])

    def validate_coupon(self, code: str) -> bool:
        for item in self._coupon_list:
            if item[0] == code and item[1] == CouponStatus.AVALIBLE:
                return True
        return False
    
    def mark_coupon_used(self, code: str) -> bool:
        for item in self._coupon_list:
            if item[0] == code and item[1] == CouponStatus.AVALIBLE:
                item[1] = CouponStatus.USED
                return True
        return False
    
    @property
    def name(self): return self._name

class EventOrder:
    def __init__(self, id, total_price: float) -> None:
        self._id = id
        self._total_price = total_price
        self._status: EventOrderStatus = EventOrderStatus.PENDING
    
    @property
    def total_price(self):
        return self._total_price
    
    @property
    def status(self):
        return self._status
    
    @status.setter
    def status(self, status: EventOrderStatus):
        self._status = status

class Booking:
    def __init__(self, id, member: Member, room_price: float) -> None:
        self._id = id
        self._member = member
        self._room_price = room_price
        self._status: BookingStatus = BookingStatus.PENDING
        self._event_order: Optional[EventOrder] = None

    def calculate_payment_details(self, coupon: Optional[Coupon] = None) -> Tuple[float, float]:
        base_price = self.total_base_price
        discount = 0.0
        final_price = base_price

        if coupon:
          if not self.member.validate_coupon(coupon.code):
              raise ValueError("Member does not have this coupon or used")
          if not coupon.is_applicable(base_price):
              raise ValueError("Does Not Meet Minimum Price")
          
          discount = coupon.apply_coupon(base_price)
          final_price = base_price - discount

        if final_price < 0:
          raise ValueError("Negative Price")
        
        return (discount, final_price)
            
    def add_event_order(self, event_order: EventOrder):
        if self._event_order is not None:
            raise ValueError("Already Have Event Order")
        self._event_order = event_order

    @property
    def total_base_price(self) -> float:
        order_price = self._event_order.total_price if self._event_order else 0.0
        return self._room_price + order_price
    @property
    def room_price(self): return self._room_price
    @property
    def id(self): return self._id
    @property
    def member(self): return self._member
    @property
    def status(self) -> BookingStatus: return self._status
    @status.setter
    def status(self, val: BookingStatus): self._status = val
    @property
    def event_order(self): return self._event_order

class Restaurant:
    _coupon_list: List[Coupon] = []
    _member_list: List[Member] = []

    @classmethod
    def add_member(cls, member: Member):
        cls._member_list.append(member)

    @classmethod
    def add_coupon(cls, coupon: Coupon):
        cls._coupon_list.append(coupon)

    @classmethod
    def get_coupon_by_code(cls, code: str) -> Optional[Coupon]:
        for coupon in cls._coupon_list:
            if code == coupon.code:
                return coupon
        return None

class BookingManager:
    """Controller จัดการเกี่ยวกับการจ่ายเงิน"""
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
    def get_strategy(cls, name: str) -> PaymentStrategy:
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

class LogManager:
    _transaction_list: List[Transaction] = []

    @classmethod
    def add_log(cls, transaction: Transaction):
      cls._transaction_list.append(transaction)
      print(f"[SYSTEM LOG] {transaction.timestamp} | {transaction.id} | {transaction.status} | {transaction.amount} THB")

    @classmethod
    def get_logs_by_booking(cls, booking_id: str) -> List[Transaction]:
      found_logs = []
      for log in cls._transaction_list:
        if log.booking_id == booking_id:
          found_logs.append(log)
      return found_logs
    
class Transaction:
    def __init__(self, booking_id: str, amount: float, strategy: str, status: str, payment_id: str,coupon_code: Optional[str] = None):
      self._id = f"TXN-{uuid.uuid4().hex[:12].upper()}"
      self._booking_id = booking_id
      self._amount = amount
      self._strategy = strategy
      self._status = status
      self._payment_id = payment_id
      self._coupon_code = coupon_code
      self._timestamp = datetime.now()

    def mark_success(self): self._status = "SUCCESS"
    def mark_failed(self): self._status = "FAILED"

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
    def coupon_code(self): return self._coupon_code
    @property
    def booking_id(self): return self._booking_id

class Receipt:
  def __init__(self, transaction: Transaction, booking: Booking):
    self._transaction = transaction
    self._booking = booking

  def generate(self):
    return {
      "receipt_no": self._transaction.id,
      "date": self._transaction.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
      "merchant": "Knight Chicken Fast Food Co.",
      "customer": self._booking.member.name,
      "items": [
          {"name": "Room Charge", "price": self._booking.room_price},
          {"name": "Food Orders", "price": self._booking.event_order.total_price if self._booking.event_order else 0}
      ],
      "total_base_price" : self._booking.room_price + self._booking.event_order.total_price if self._booking.event_order else 0,
      "discount_coupon": self._transaction.coupon_code,
      "discounted": (self._booking.room_price + self._booking.event_order.total_price if self._booking.event_order else 0) - self._transaction.amount,
      "total_paid": self._transaction.amount,
      "payment_method": self._transaction.strategy,
      "status": "PAID"
    }

# API Endpoints 

@mcp.tool
async def get_base_price(booking_id: str):
    """
    ตรวจสอบจำนวนเงินทั้งหมดที่ต้องจ่าย แบบที่ยังไม่ใส่ส่วนลด โดยรับ booking_id เป็น parameter มี Format เป็น Bxxx
    และจำคืนค่า room_price และ order_price และ total_base_price
    """
    booking = BookingManager.get_booking_from_id(booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking Not Found")
    
    return {
        "booking_id": booking.id,
        "room_price": booking.room_price,
        "order_price": booking.event_order.total_price if booking.event_order else 0,
        "total_base_price": booking.total_base_price
    }

@mcp.tool
async def pay(booking_id: str, strategy: str, coupon_code: Optional[str] = Query(default=None)):
    """
    จ่ายเงิน โดยรับ booking_id เป็น parameter มี Format เป็น Bxxx ช่องทางการจ่ายเงิน มี QRCode , Cash(เงินสด) และ CreditCard
    และจะใช้คูปองหรือไม่ก็ได้ ถ้าใช้คูปอง จะรับคูปองมาเป็น Code
    """
    booking = BookingManager.get_booking_from_id(booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking Not Found")
    
    if booking.status != BookingStatus.PENDING:
        raise HTTPException(status_code=409, detail="Booking already paid")
    
    coupon = None
    if coupon_code:
        coupon = Restaurant.get_coupon_by_code(coupon_code)
        if not coupon:
                raise HTTPException(status_code=400, detail="Coupon Not Found")

    try:
      discount, final_total = booking.calculate_payment_details(coupon)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    payment_strategy = PaymentStrategy.get_strategy(strategy)
    success, receipt_or_msg = payment_strategy.pay(final_total)

    transaction = Transaction(booking_id,final_total,strategy.lower(), "PENDING", receipt_or_msg, coupon_code if discount > 0 else None)

    if success:
        booking.status = BookingStatus.IN_USE
        if booking.event_order:
            booking.event_order.status = EventOrderStatus.QUEUED
        
        member = booking.member
        if coupon_code and discount > 0:
          if not member.mark_coupon_used(coupon_code):
              raise HTTPException(status_code=500, detail="can't mark coupon as used") 

        transaction.mark_success()
        LogManager.add_log(transaction)

        receipt = Receipt(transaction, booking)
        return receipt.generate()
    
    else:
        transaction.mark_failed()
        LogManager.add_log(transaction)

        raise HTTPException(status_code=402, detail=f"Payment Failed: {receipt_or_msg}")

# ==========================================
# Mock Data
# ==========================================
# Clear lists
Restaurant._member_list.clear()
Restaurant._coupon_list.clear()
BookingManager._booking_list.clear()

# Create Member & Coupon
alice = Member("M001", "Alice")
bob = Member("M002", "Bob")
Restaurant.add_member(alice)
Restaurant.add_member(bob)

c1 = PercentCoupon("C001", "SAVE10", 100, 10.0)
c2 = PercentCoupon("C002", "SAVE20", 500, 20.0)
Restaurant.add_coupon(c1)
Restaurant.add_coupon(c2)

alice.add_coupon("SAVE10")
bob.add_coupon("SAVE10")
bob.add_coupon("SAVE20")


# Create Bookings
# Booking 1: Alice with a room and an event order, eligible for SAVE10
order1 = EventOrder("ORD-001", 150.0)
b1 = Booking("B001", alice, 200.0)
b1.add_event_order(order1)
BookingManager.add_booking(b1)

# Booking 2: Bob with a room and a large event order, eligible for SAVE20
order2 = EventOrder("ORD-002", 600.0)
b2 = Booking("B002", bob, 400.0)
b2.add_event_order(order2)
BookingManager.add_booking(b2)

# Booking 3: Alice with just a room booking
b3 = Booking("B003", alice, 150.0)
BookingManager.add_booking(b3)

# Booking 4: Bob with a small order, not meeting minimum for any coupon
order3 = EventOrder("ORD-003", 50.0)
b4 = Booking("B004", bob, 40.0)
b4.add_event_order(order3)
BookingManager.add_booking(b4)

print("Mock Data Initialized. Ready to test.")

if __name__ == "__main__":
    mcp.run()