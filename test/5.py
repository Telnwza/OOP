class MenuItem:
    def __init__(self, name: str, price: float):
        self.__name = name
        self.__price = price

    @property
    def name(self) -> str:
        return self.__name

    @property
    def price(self) -> float:
        return self.__price

class Order:
    def __init__(self, order_id: int):
        self.__order_id = order_id
        self.__status = "Created"
        self.__items = []

    @property
    def order_id(self) -> int:
        return self.__order_id

    def add_item(self, item: MenuItem) -> None:
        self.__items.append(item)

    def calculate_total(self) -> float:
        return sum(item.price for item in self.__items)

    def update_status(self, new_status: str) -> None:
        self.__status = new_status
        
    def get_status(self) -> str:
        return self.__status

# Controller Class
class Restaurant:
    def __init__(self, name: str):
        self.__name = name
        self.__menu_catalog = []  # เก็บรายการอาหารที่มีขาย
        self.__orders = []        # เก็บออเดอร์ทั้งหมดในระบบ
        self.__next_order_id = 1

    def add_menu_item(self, item: MenuItem) -> None:
        self.__menu_catalog.append(item)

    def create_new_order(self) -> int:
        """สร้างออเดอร์ใหม่และคืนค่า order_id กลับไปให้ UI"""
        new_order = Order(self.__next_order_id)
        self.__orders.append(new_order)
        self.__next_order_id += 1
        return new_order.order_id

    def add_item_to_order(self, order_id: int, item_name: str) -> bool:
        """รับคำสั่งจาก UI เพื่อเพิ่มอาหารลงออเดอร์โดยอ้างอิงจาก ID"""
        # 1. ค้นหาเมนูจาก Catalog
        selected_item = next((item for item in self.__menu_catalog if item.name == item_name), None)
        if not selected_item:
            return False
            
        # 2. ค้นหาออเดอร์
        target_order = next((order for order in self.__orders if order.order_id == order_id), None)
        if not target_order:
            return False
            
        # 3. เพิ่มลงออเดอร์
        target_order.add_item(selected_item)
        return True

    def checkout_order(self, order_id: int, payment_method: str) -> bool:
        """จัดการการชำระเงินและอัปเดตสถานะ"""
        target_order = next((order for order in self.__orders if order.order_id == order_id), None)
        if not target_order:
            return False

        total = target_order.calculate_total()
        
        # จำลองระบบการชำระเงิน (ในระบบจริงจะเป็นการเรียก Payment Class)
        payment_success = True # สมมติว่าชำระเงินผ่านเสมอ
        
        if payment_success:
            target_order.update_status("Pending")
            return True
        return False

# ==========================================
# Driver Code สำหรับทดสอบ (จำลองการทำงานของหน้าจอ Kiosk)
# ==========================================
if __name__ == "__main__":
    # System Initialization
    my_restaurant = Restaurant("FastFood Station")
    my_restaurant.add_menu_item(MenuItem("Cheeseburger", 89.0))
    my_restaurant.add_menu_item(MenuItem("French Fries", 45.0))

    # จำลองการทำงานฝั่งลูกค้า (UI สื่อสารผ่าน Restaurant เท่านั้น)
    current_order_id = my_restaurant.create_new_order()
    
    my_restaurant.add_item_to_order(current_order_id, "Cheeseburger")
    my_restaurant.add_item_to_order(current_order_id, "French Fries")
    
    is_paid = my_restaurant.checkout_order(current_order_id, "Credit Card")
    
    if is_paid:
        print(f"ชำระเงินสำเร็จ ออเดอร์หมายเลข {current_order_id} ถูกส่งไปยังห้องครัวแล้ว")