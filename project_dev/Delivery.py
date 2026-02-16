from __future__ import annotations
from typing import Optional, List, Tuple
from fastapi import HTTPException
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from fastmcp import FastMCP
import uuid
import random

mcp = FastMCP()

class OrderStatus(Enum):
    PENDING_PAYMENT = "Pending Payment"
    PLACED = "Placed"
    CANCELLED = "Cancelled"

class DeliveryPlatformName(Enum):
    GRAB_FOOD = "GrabFood"
    LINEMAN = "LineMan"
    ROBINHOOD = "Robinhood"

class Coupon(ABC):
    def __init__(self, code, minimum_price) -> None:
        self._code = code
        self._minimum_price = minimum_price

    @property
    def code(self): return self._code

    def is_applicable(self, base_price: float) -> bool:
        return base_price >= self._minimum_price

    @abstractmethod
    def apply_coupon(self, base_price: float) -> float:
        pass

class PercentCoupon(Coupon):
    def __init__(self, code, minimum_price, percent) -> None:
        super().__init__(code, minimum_price)
        self._percent = percent

    def apply_coupon(self, base_price: float) -> float:
        if self.is_applicable(base_price):
            return base_price * (self._percent / 100)
        return 0.0

class PaymentStrategy(ABC):
    @classmethod
    def get_strategy(cls, name: str) -> PaymentStrategy:
        for strategy_cls in PaymentStrategy.__subclasses__():
            if strategy_cls.get_name().lower() == name.lower():
                return strategy_cls
        raise ValueError(f"Unknown Payment Strategy: {name}")
    
    @staticmethod
    @abstractmethod
    def get_name() -> str: pass
    
    @staticmethod
    @abstractmethod
    def pay(amount: float) -> Tuple[bool, str]: pass

class CreditCard(PaymentStrategy):
    @staticmethod
    def get_name() -> str: return "CreditCard"
    @staticmethod
    def pay(amount: float) -> Tuple[bool, str]:
        return True, f"REC-{uuid.uuid4().hex[:8].upper()}"

class QRCode(PaymentStrategy):
    @staticmethod
    def get_name() -> str: return "QRCode"
    @staticmethod
    def pay(amount: float) -> Tuple[bool, str]:
        return True, f"REC-{uuid.uuid4().hex[:8].upper()}"

class CashOnDelivery(PaymentStrategy):
    @staticmethod
    def get_name() -> str: return "Cash"
    @staticmethod
    def pay(amount: float) -> Tuple[bool, str]:
        return True, f"REC-{uuid.uuid4().hex[:8].upper()}"

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

    def confirm_payment(self, method: str, receipt: str, discount: float, final_price: float, coupon_code: str = None):
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


@mcp.tool
async def create_delivery_order(platform: str, food_items: List[str]):
    """
    สร้างออเดอร์ Delivery ใหม่ (Step 1)
    - platform: ชื่อแอพ (GrabFood, LineMan)
    - food_items: รายชื่ออาหาร เช่น ["Burger", "Coke"]
    Return: Order ID และราคารวมที่ต้องจ่าย
    """
    order_id = f"DEL-{uuid.uuid4().hex[:6].upper()}"
    new_order = DeliveryOrder(order_id, "CUST_AUTO", platform)

    added_items = []
    for item_name in food_items:
        food = Restaurant.get_menu_item(item_name)
        if food:
            new_order.add_food(food)
            added_items.append(f"{food.name} ({food.price})")
    
    if not added_items:
        return "Error: No valid food items found in menu."

    Restaurant.add_order(new_order)
    
    return {
        "message": "Order Created Successfully",
        "order_id": order_id,
        "platform": platform,
        "items": added_items,
        "total_price": new_order.total_base_price,
        "status": new_order.status.value,
        "next_step": "Please call 'pay_delivery_order' to confirm."
    }

@mcp.tool
async def pay_delivery_order(order_id: str, payment_method: str, coupon_code: str = None):
    """
    ชำระเงินค่าออเดอร์ Delivery (Step 2)
    - order_id: รหัสออเดอร์ที่ได้จาก step แรก
    - payment_method: ช่องทางจ่ายเงิน (CreditCard, QRCode, Cash)
    - coupon_code: รหัสส่วนลด (ถ้ามี) เช่น 'SAVE10'
    """

    order = Restaurant.get_order(order_id)
    if not order:
        return f"Error: Order {order_id} not found."
    
    if order.status == OrderStatus.PLACED:
        return f"Error: Order {order_id} is already paid."

    coupon = None
    if coupon_code:
        coupon = Restaurant.get_coupon(coupon_code)
        if not coupon:
            return "Error: Coupon code invalid."

    try:
        discount, final_price = order.calculate_payment_details(coupon)
    except ValueError as e:
        return f"Error processing payment: {str(e)}"

    try:
        strategy = PaymentStrategy.get_strategy(payment_method)
        success, receipt = strategy.pay(final_price)
    except ValueError as e:
        return f"Error: {str(e)}"

    if success:
        order.confirm_payment(strategy.get_name(), receipt, discount, final_price, coupon_code)
        
        return {
            "status": "Payment Success",
            "receipt_no": receipt,
            "order_id": order.id,
            "items_count": len(order.food_list),
            "base_price": order.total_base_price,
            "coupon_applied": coupon_code if discount > 0 else None,
            "discount": discount,
            "final_paid": final_price,
            "payment_method": strategy.get_name(),
            "order_status": order.status.value
        }
    else:
        return "Error: Payment Gateway declined the transaction."

# ==========================================
# MOCK DATA INIT
# ==========================================
# เพิ่มคูปองเข้าระบบ
Restaurant._coupons.append(PercentCoupon("SAVE10", 100.0, 10.0))
Restaurant._coupons.append(PercentCoupon("SAVE50", 500.0, 50.0))

if __name__ == "__main__":
    mcp.run()