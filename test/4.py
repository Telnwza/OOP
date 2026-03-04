from abc import ABC, abstractmethod

class Item(ABC):
  def __init__(self, name, price: float) -> None:
    self.__name = name
    self.__price: float = price

  @property
  def name(self): return self.__name

  @property
  def price(self): return self.__price

  @abstractmethod
  def prepare(self):
    pass

class Food(Item):
  def __init__(self, name, price: float) -> None:
    super().__init__(name, price)

  def prepare(self):
    print(f"กำลังปรุงอาหาร {self.name}")

class Drink(Item):
  def __init__(self, name, price: float) -> None:
    super().__init__(name, price)

  def prepare(self):
    print(f"กำลังชงเครื่องดื่ม {self.name}")

class Order:
  def __init__(self, id) -> None:
    self.__id = id
    self.__item: list[Item] = []

  @property
  def id(self): return self.__id

  def add_item(self, item: Item):
    print(f"เพิ่ม สินค้า {item.name} ใน Order")
    self.__item.append(item)

  def prepare_all(self):
    print(f"กำลังเตรียมอาหาร order: {self.id}")
    for item in self.__item:
      item.prepare()

  def calculate_total(self):
    item_total = 0.0
    for item in self.__item:
      item_total += item.price
    return item_total

class Table:
  def __init__(self, id) -> None:
    self.__id = id
    self.__order: list[Order] = []
  
  @property
  def id(self): return self.__id
  
  def add_order(self, order: Order):
    print(f"เพิ่ม order {order.id} ในโต๊ะ")
    self.__order.append(order)

  def prepare_all(self):
    for order in self.__order:
      order.prepare_all()

  def calculate_total(self) -> float:
    order_total = 0.0
    for order in self.__order:
      order_total += order.calculate_total()
    return order_total

class Restaurant:
  def __init__(self) -> None:
    self.__table: list[Table] = []

  def add_table(self, table:Table):
    self.__table.append(table)

  def prepare_all(self, table_id):
    for table in self.__table:
      if table.id == table_id:
        print(f"กำลังเตรียมอาหาร โต๊ะ {table_id}")
        table.prepare_all()
        return
    print(f"ไม่พบ โต๊ะ {table_id}")

  def calculate_total(self, table_id):
    total = 0.0
    for table in self.__table:
      if table.id == table_id:
        print(f"กำลังเตรียมอาหาร คิดบิล โต๊ะ {table_id}")
        return table.calculate_total()
    print(f"ไม่พบ โต๊ะ {table_id}")