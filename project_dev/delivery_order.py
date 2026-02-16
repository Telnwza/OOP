from __future__ import annotations
from typing import Optional, List, Tuple
from fastapi import HTTPException
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from fastmcp import FastMCP
import uuid
import random

class OrderStatus(Enum):
    PENDING_PAYMENT = "Pending Payment"
    PLACED = "Placed"
    CANCELLED = "Cancelled"

class DeliveryPlatformName(Enum):
    GRAB_FOOD = "GrabFood"
    LINEMAN = "LineMan"

class Food:
    def __init__(self, name: str, price: float):
        self._name = name
        self._price = price
    
    @property
    def name(self): return self._name
    @property
    def price(self): return self._price

class DeliveryOrder:
    def __init__(self, id:str, customer_id:str, platform: str) -> None:
        self._id = id
        self._customer_id = customer_id
        self._platform = platform
        self._food_list: List[Food] = []
        self._status = OrderStatus.PENDING_PAYMENT
        
        # Payment Info
        self._total_base_price: float = 0.0
        self._discount: float = 0.0
        self._final_price: float = 0.0
        self._payment_method: Optional[str] = None
        self._receipt_id: Optional[str] = None
        self._coupon_code: Optional[str] = None

    def add_food(self, food: Food):
        self._food_list.append(food)
        self._total_base_price += food.price
        self._final_price = self._total_base_price

    def calculate_payment_details(self, coupon: Optional[Coupon] = None) -> Tuple[float, float]:
        """
        คำนวณราคาหลังหักส่วนลด (Pure Logic)
        คืนค่า: (discount_amount, final_price)
        """
        discount = 0.0
        final = self._total_base_price

        if coupon:
            if not coupon.is_applicable(self._total_base_price):
                raise ValueError(f"Coupon {coupon.code} minimum price not met")
            
            discount = coupon.apply_coupon(self._total_base_price)
            final = self._total_base_price - discount
        
        if final < 0: raise ValueError("Price cannot be negative")
        
        return discount, final

    def confirm_payment(self, method: str, receipt: str, discount: float, final_price: float, coupon_code: Optional[str] = None):
        """State Transition Method"""
        self._status = OrderStatus.PLACED
        self._payment_method = method
        self._receipt_id = receipt
        self._discount = discount
        self._final_price = final_price
        self._coupon_code = coupon_code

    @property
    def id(self): return self._id
    @property
    def status(self): return self._status
    @property
    def total_base_price(self): return self._total_base_price
    @property
    def final_price(self): return self._final_price
    @property
    def food_list(self): return self._food_list

class Restaurant:
    _orders: List[DeliveryOrder] = []
    _coupons: List[Coupon] = []
    _menu: List[Food] = [
        Food("Fried Chicken", 45.0),
        Food("Burger", 89.0),
        Food("French Fries", 39.0),
        Food("Coke", 25.0),
        Food("Combo Set A", 159.0)
    ]

    @classmethod
    def add_order(cls, order: DeliveryOrder):
        cls._orders.append(order)

    @classmethod
    def get_order(cls, order_id: str) -> Optional[DeliveryOrder]:
        for order in cls._orders:
            if order.id == order_id: return order
        return None

    @classmethod
    def get_coupon(cls, code: str) -> Optional[Coupon]:
        for coupon in cls._coupons:
            if coupon.code == code: return coupon
        return None
    
    @classmethod
    def get_menu_item(cls, name: str) -> Optional[Food]:
        for food in cls._menu:
            if food.name.lower() == name.lower(): return food
        return None

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

class LogManager:
    _transaction_list: List[Transaction] = []

    @classmethod
    def add_log(cls, transaction: Transaction):
      cls._transaction_list.append(transaction)
      print(f"[SYSTEM LOG] {transaction.timestamp} | {transaction.id} | {transaction.status} | {transaction.amount} THB")

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
    
  