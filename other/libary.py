"""
Mini System: Library Management (OOP ครบทุกแบบในไฟล์เดียว)
ครอบคลุม:
- Class/Instance, __init__
- Instance attribute / Class attribute
- Instance method / Class method / Static method
- Encapsulation (public/protected/private) + @property
- Abstraction (ซ่อนรายละเอียดหลัง interface)
- Inheritance + Polymorphism
- Relationships: Association, Dependency, Aggregation, Composition, Self-association
"""

from __future__ import annotations
from datetime import date, timedelta
from typing import List, Optional


# ---------------------------
# 0) Utility (Static method example)
# ---------------------------
class DateUtil:
    """Utility class: ไม่แตะ state ของ object -> staticmethod เหมาะสุด"""

    @staticmethod
    def add_days(d: date, days: int) -> date:
        """Return a new date = d + days."""
        return d + timedelta(days=days)


# ---------------------------
# 1) Core domain classes
# ---------------------------
class Person:
    """
    Self-association:
    - Person มี friends เป็น List[Person] (สัมพันธ์กับคลาสตัวเอง)
    """

    def __init__(self, name: str):
        self.name = name
        self.friends: List["Person"] = []  # multiplicity: 0..*

    def add_friend(self, other: "Person") -> None:
        """Add a friend (self-association)."""
        if other is self:
            return
        if other not in self.friends:
            self.friends.append(other)

        # ตัวอย่าง binary association แบบสองทาง (optional):
        if self not in other.friends:
            other.friends.append(self)


class Member(Person):
    """
    Inheritance:
    - Member สืบทอดจาก Person
    Encapsulation:
    - จำกัด max borrow ด้วย class attribute
    """

    max_borrow = 10  # Class attribute: shared rule across all members

    def __init__(self, name: str, member_id: str):
        super().__init__(name)
        self.member_id = member_id


class Librarian(Person):
    """Inheritance: Librarian สืบทอดจาก Person"""

    def __init__(self, name: str, staff_id: str):
        super().__init__(name)
        self.staff_id = staff_id

    # Dependency example:
    def print_book_label(self, book: "Book") -> None:
        """
        Dependency:
        - Librarian ไม่เก็บ book ไว้เป็น attribute
        - แค่ "ใช้ชั่วคราว" เป็นพารามิเตอร์ของ method
        """
        print(f"[LABEL] {book.isbn} | {book.title} | {book.author}")


class Book:
    """
    Abstraction + Encapsulation:
    - expose interface ที่จำเป็น (title/author/isbn)
    - ซ่อนการ validate/normalize บางอย่างไว้ภายใน
    """

    def __init__(self, isbn: str, title: str, author: str):
        self.isbn = self._normalize_isbn(isbn)  # protected helper
        self.title = title
        self.author = author

    def _normalize_isbn(self, isbn: str) -> str:
        """Protected helper: ซ่อนรายละเอียดการทำงาน (abstraction)."""
        return isbn.replace("-", "").strip()


class BookItem:
    """
    Composition:
    - BookItem เป็น "ชิ้นส่วน" ของ Library inventory (ถูกสร้าง/ถูกทำลายโดย Library)
    Association:
    - BookItem อ้างถึง Book (has-a) เพื่อรู้ว่าเป็น copy ของหนังสือเล่มไหน
    """

    # Class attribute (นับจำนวน item ที่ถูกสร้าง)
    _serial_counter = 1

    def __init__(self, book: Book, rack: str):
        self.book = book                 # Association to Book (1)
        self.rack = rack
        self.item_no = BookItem._serial_counter  # unique id
        BookItem._serial_counter += 1

        self.is_available = True  # state

    def __repr__(self) -> str:
        return f"<BookItem #{self.item_no} {self.book.title} rack={self.rack} available={self.is_available}>"


# ---------------------------
# 2) Polymorphism via Policy (Strategy-like)
# ---------------------------
class LoanPolicy:
    """
    Polymorphism:
    - interface เดียวกัน: max_days()
    - แต่ implementation ต่างกันตาม policy
    """

    def max_days(self) -> int:
        raise NotImplementedError


class StandardPolicy(LoanPolicy):
    def max_days(self) -> int:
        return 15


class ShortPolicy(LoanPolicy):
    def max_days(self) -> int:
        return 7


class Loan:
    """
    Encapsulation:
    - _due_date: protected-ish
    - __returned: private (name mangling)
    Property:
    - returned: read-only property
    Abstraction:
    - ผู้ใช้เรียก .due_date ได้เลย ไม่ต้องรู้คำนวณยังไง
    """

    def __init__(self, member: Member, item: BookItem, policy: LoanPolicy):
        self.member = member      # Association to Member
        self.item = item          # Association to BookItem
        self.policy = policy      # Polymorphism target

        self.start_date = date.today()
        self._due_date = DateUtil.add_days(self.start_date, self.policy.max_days())
        self.__returned = False   # private

    @property
    def due_date(self) -> date:
        """Read-only property for due date (abstraction)."""
        return self._due_date

    @property
    def returned(self) -> bool:
        """Read-only property: ไม่ให้แก้จากข้างนอกโดยตรง"""
        return self.__returned

    def mark_returned(self) -> None:
        """Controlled state change (encapsulation)."""
        self.__returned = True

    def __repr__(self) -> str:
        return f"<Loan member={self.member.member_id} item={self.item.item_no} due={self.due_date} returned={self.returned}>"


# ---------------------------
# 3) Aggregation + Composition owner: Library
# ---------------------------
class Library:
    """
    Aggregation:
    - Library "รวบรวม/จัดการ" Member และ Librarian (คนอยู่ได้เอง)
      เก็บเป็น list (multiplicity 0..*)
    Composition:
    - BookItem ถูกสร้างและถูกจัดการโดย Library (inventory)
      โดยทั่วไปถือเป็นส่วนประกอบภายในระบบคลังของห้องสมุด

    Association:
    - Library มีความสัมพันธ์กับหลายคลาสผ่าน attribute list
    Class method:
    - from_defaults() เป็น alternate constructor
    """

    def __init__(self, name: str):
        self.name = name

        # Aggregation: people live independently
        self.members: List[Member] = []
        self.librarians: List[Librarian] = []

        # Composition: inventory items created/owned by library
        self.inventory: List[BookItem] = []

        # Active loans (association to Loan)
        self.loans: List[Loan] = []

    @classmethod
    def from_defaults(cls) -> "Library":
        """Class method: alternate constructor."""
        return cls("Default Library")

    # ---------- Aggregation management ----------
    def add_member(self, member: Member) -> None:
        self.members.append(member)

    def add_librarian(self, librarian: Librarian) -> None:
        self.librarians.append(librarian)

    # ---------- Composition management ----------
    def add_new_copy(self, book: Book, rack: str, copies: int = 1) -> None:
        """
        Composition:
        - Library สร้าง BookItem ภายใน (เป็นส่วนประกอบของ inventory)
        Multiplicity:
        - copies ทำให้เกิด 1..* items ได้
        """
        for _ in range(max(1, copies)):
            self.inventory.append(BookItem(book, rack))

    # ---------- Query helpers ----------
    def __find_available_items_by_isbn(self, isbn: str) -> List[BookItem]:
        """Return all available copies for given isbn."""
        norm = isbn.replace("-", "").strip()
        return [it for it in self.inventory if it.book.isbn == norm and it.is_available]

    def __count_loans_for_member(self, member: Member) -> int:
        """Count active (not returned) loans for a member."""
        return sum(1 for loan in self.loans if loan.member is member and not loan.returned)

    # ---------- Business actions ----------
    def borrow(self, member: Member, isbn: str, policy: LoanPolicy) -> Optional[Loan]:
        """
        Association:
        - borrow() สร้าง Loan ที่ผูก member + item + policy
        Encapsulation:
        - ตรวจเงื่อนไขต่าง ๆ ภายใน method
        Polymorphism:
        - policy.max_days() ต่างกันได้ แต่ interface เดียวกัน
        """
        if self.__count_loans_for_member(member) >= Member.max_borrow:
            return None  # เกินสิทธิ์

        items = self.__find_available_items_by_isbn(isbn)
        if not items:
            return None  # ไม่มีเล่มว่าง

        item = items[0]
        item.is_available = False

        loan = Loan(member, item, policy)
        self.loans.append(loan)
        return loan

    def return_book(self, loan: Loan) -> bool:
        """Return a borrowed book."""
        if loan.returned:
            return False
        loan.item.is_available = True
        loan.mark_returned()
        return True


# ---------------------------
# 4) Demo usage (optional)
# ---------------------------
if __name__ == "__main__":
    # Create library (class method)
    lib = Library.from_defaults()

    # Create people (instances)
    alice = Member("Alice", "M001")
    bob = Member("Bob", "M002")
    staff = Librarian("Mr. Smith", "S100")

    # Self-association demo
    alice.add_friend(bob)

    # Aggregation: add people into library
    lib.add_member(alice)
    lib.add_member(bob)
    lib.add_librarian(staff)

    # Create book objects
    book1 = Book("978-123", "Python Programming", "Someone")
    book2 = Book("978-999", "Networks 101", "Another")

    # Composition: library creates copies (BookItem)
    lib.add_new_copy(book1, rack="A1", copies=2)
    lib.add_new_copy(book2, rack="B2", copies=1)

    # Dependency: librarian prints label using book as parameter
    staff.print_book_label(book1)

    # Polymorphism: different policies
    standard = StandardPolicy()
    short = ShortPolicy()

    # Borrow with standard policy
    loan1 = lib.borrow(alice, "978-123", standard)
    print("loan1:", loan1)

    # Borrow with short policy (same interface, different due date)
    loan2 = lib.borrow(bob, "978-999", short)
    print("loan2:", loan2)

    # Return
    if loan1:
        lib.return_book(loan1)
        print("after return loan1:", loan1)

    # Show self-association result
    print("Alice friends:", [p.name for p in alice.friends])