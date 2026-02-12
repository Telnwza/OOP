from enum import Enum, auto
from datetime import datetime

class DeliveryOrderStatus(Enum):
  PLACED = "PLACED"
  COOKING = "COOKING"
  READY = "READY"
  IN_TRANSIT = "IN_TRANSIT"
  DELIVERED = "DELIVERED"

class DeliveryPlatformName(Enum):
  GRAB_FOOD = "GRAB_FOOD"
  LINEMAN = "LINEMAN"

class Food:
  def __init__(self) -> None:
    pass

class DeliveryOrder:
  def __init__(self, id:str, type:str, customer_id:str) -> None:
    self._id = id
    self._type = type
    self._customer_id = customer_id
    self._food_list:list[Food] = []
    self._total_price = total_price
    self._time = time
    self._status = status
    pass

def generate_delivery_order() -> DeliveryOrder:
  return DeliveryOrder()