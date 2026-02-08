class Dog:
    species = 'Mammal' # Class Variable
    def __init__(self, name):
        self.name = name # Instance Variable

d1 = Dog('Red')
d2 = Dog('Black')
Dog.species = 'Alien'
print(d1.species, d2.species)

def add_item(item, box=[]):
    box.append(item)
    return box

print(add_item('A'))
print(add_item('B'))

from abc import ABC, abstractmethod

# 1. Abstract Base Class
class Employee(ABC):
    def __init__(self, name, emp_id):
        self._name = name       # Protected use single underscore (_)
        self._id = emp_id       # Protected

    @abstractmethod             # บังคับให้ลูกต้องมี
    def calculate_salary(self):
        pass

    def show_details(self):
        print(f"ID: {self._id}, Name: {self._name}")

# 2. Subclasses
class FullTimeEmployee(Employee):
    def __init__(self, name, emp_id, salary):
        super().__init__(name, emp_id)  # ส่งค่าไปให้แม่
        self.salary = salary

    def calculate_salary(self):         # Override
        return self.salary

class PartTimeEmployee(Employee):
    def __init__(self, name, emp_id, hourly_rate, hours_worked):
        super().__init__(name, emp_id)
        self.hourly_rate = hourly_rate
        self.hours_worked = hours_worked

    def calculate_salary(self):         # Override
        return self.hourly_rate * self.hours_worked

# 3. Aggregation Class
class Company:
    def __init__(self, name):
        self.name = name
        self.employees = []    # List เก็บ Employee (Aggregation)

    def add_employee(self, emp):
        self.employees.append(emp)

    def pay_all_salaries(self):
        print(f"--- Payroll for {self.name} ---")
        for emp in self.employees:
            # Polymorphism: บรรทัดนี้ทำงานต่างกันตามชนิดพนักงาน
            print(f"{emp._name}: {emp.calculate_salary()} THB")

# Test (ในห้องสอบไม่ต้องเขียนส่วนนี้ก็ได้ ถ้าโจทย์ไม่ถาม)
c = Company("Te Tech")
c.add_employee(FullTimeEmployee("Te", "001", 50000))
c.add_employee(PartTimeEmployee("Bob", "002", 100, 40))
c.pay_all_salaries()