##################################################################################
# ระบบธนาคาร ATM เต็มรูปแบบ (INHERITANCE LAB)
# 
# STUDENT SKELETON CODE
# 
# คุณสมบัติ:
# 1. เพิ่มบัญชีเป็น 3 ประเภท (ออมทรัพย์, ฝากประจำ, กระแสรายวัน)
# 2. เพิ่มบัตรโดยมีบัตร ATM, Premium Card, Shopping Card
# 3. เพิ่มช่องทางให้บริการ ตู้ ATM, เคาน์เตอร์, เครื่องรูดบัตร (EDC)
# 4. เพิ่มประเภทธุรกรรม (D, W, TW, TD, I, P, F)
# 5. เพิ่มการคำนวณดอกเบี้ย, เครดิตคืน, ค่าธรรมเนียมรายปี, วงเงินรายวัน
# 6. บังคับใช้ Inheritance
#
##################################################################################

from abc import ABC, abstractmethod
from datetime import datetime, timedelta


# ============================================================================
# ABSTRACT BASE CLASSES 
# ============================================================================

class Account(ABC):
    """Base class สำหรับบัญชีทุกประเภท
    
    Attributes:
        __account_no: หมายเลขบัญชี
        __user: เจ้าของบัญชี (User object)
        __amount: ยอดเงินคงเหลือ
        __card: บัตร ATM/Debit ที่เชื่อมกับบัญชี
        __daily_withdrawn: ยอดเงินที่ถอนในวันนี้ (สำหรับ ATM/EDC)
        __transaction_list: ประวัติการทำธุรกรรมทั้งหมด
    """
    
    def __init__(self, account_no, user, amount):
        """TODO: Initialize account attributes"""
        pass
    
    # ========== Properties (5 คะแนน) ==========
    
    @property
    def amount(self):
        """TODO: Return current balance"""
        pass
    
    @property
    def card(self):
        """TODO: Return card associated with this account"""
        pass
    
    @property
    def account_no(self):
        """TODO: Return account number"""
        pass
    
    @property
    def user(self):
        """TODO: Return account owner"""
        pass
    
    # ========== Card Management ==========
    
    def add_card(self, card):
        """เพิ่มบัตรให้กับบัญชี
        
        Args:
            card: Card object (ATM_Card, DebitCard, PremiumCard, ShoppingCard)
        
        TODO: เก็บ card ไว้ใน __card attribute
        """
        pass
    
    # ========== Security & Validation (5 คะแนน) ==========
    
    def _validate_channel_session(self, channel):
        """ตรวจสอบ session ว่าบัตรที่อยู่ใน channel ตรงกับบัตรของบัญชีนี้หรือไม่
        
        Args:
            channel: ATM_machine หรือ EDC_machine object
        
        Raises:
            PermissionError: ถ้าบัตรไม่ตรงกัน หรือยังไม่ได้ insert card
        
        TODO:
        - ตรวจสอบว่า channel มี current_card หรือไม่
        - ตรวจสอบว่า current_card ตรงกับ self.__card หรือไม่
        - ถ้าไม่ตรง raise PermissionError
        """
        pass
    
    # ========== Transaction Recording ==========
    
    def _create_transaction(self, type, channel_type, channel_id, amount, balance, target=None):
        """บันทึก transaction ลง __transaction_list
        """
        self.__transaction_list.append(
            Transaction(type, channel_type, channel_id, amount, balance, target)
        )

    def print_transactions(self):
        """แสดงประวัติธุรกรรมทั้งหมด
        """
        print(f"\n--- History for {self.__account_no} ({type(self).__name__}) Balance: {self.__amount:.2f} ---")
        for t in self.__transaction_list: 
            print(t)

    def get_last_transaction(self):
        """ดึง transaction สุดท้าย (สำหรับ testing)
        
        Returns:
            Transaction object หรือ None ถ้าไม่มี
        """
        return self.__transaction_list[-1] if self.__transaction_list else None


    
    # ========== Transaction History ==========
    
    def get_transactions(self, count=None):
        """ดึง transactions ตามจำนวนที่กำหนด
        
        Args:
            count: จำนวน transactions (จากหลังสุด), None = ทั้งหมด
        
        Returns:
            list ของ Transaction objects
        """
        if count is None:
            return self.__transaction_list.copy()
        return self.__transaction_list[-count:] if count > 0 else []
    
    def get_transaction_count(self):
        """นับจำนวน transactions ทั้งหมด"""
        return len(self.__transaction_list)
    
    def _get_channel_id(self, channel):
        """ดึง channel ID จาก channel object
        
        TODO:
        - ถ้า channel มี atm_no → return atm_no
        - ถ้า channel มี edc_no → return edc_no
        - ถ้า channel มี counter_id → return counter_id
        - ถ้าไม่มี → return 'UNKNOWN'
        """
        pass

    # ========== Abstract Methods  ==========
    
    @abstractmethod
    def get_account_type(self):
        """ระบุประเภทบัญชี (แต่ละ subclass ต้อง implement)
        
        Returns:
            str: ชื่อประเภทบัญชี
        """
        pass
    
    @abstractmethod
    def calculate_interest(self):
        """คำนวณและเพิ่มดอกเบี้ย (แต่ละประเภทบัญชีมีอัตราต่างกัน)
        
        Returns:
            float: จำนวนดอกเบี้ยที่ได้รับ
        """
        pass
    
    @abstractmethod
    def _check_withdraw_limit(self, amount):
        """ตรวจสอบ limit การถอนตามประเภทบัญชี
        
        Args:
            amount: จำนวนเงินที่ต้องการถอน
        
        Raises:
            ValueError: ถ้าเกิน limit
        """
        pass
    
    def deposit(self, channel, amount):
        """ฝากเงิน - รองรับทุก channel (ATM, Counter, EDC)
        
        Args:
            channel: ช่องทางการทำธุรกรรม
            amount: จำนวนเงินที่ฝาก
        
        Raises:
            PermissionError: ถ้า session ไม่ถูกต้อง (ATM/EDC)
            ValueError: ถ้า amount <= 0
        
        TODO:
        1. Validate session (เฉพาะ ATM และ EDC)
        2. Validate amount > 0
        3. เพิ่มเงินเข้าบัญชี
        4. ถ้า channel มี receive_cash → เรียกใช้
        5. บันทึก transaction (type='D')
        6. แสดงข้อความสำเร็จ
        """
        pass
    
    def withdraw(self, channel, amount):
        """ถอนเงิน - มี validation หลายขั้นตอน
        
        Args:
            channel: ช่องทางการทำธุรกรรม
            amount: จำนวนเงินที่ต้องการถอน
        
        Raises:
            PermissionError: ถ้า session ไม่ถูกต้อง (ATM/EDC)
            ValueError: ถ้า amount <= 0
            ValueError: ถ้าเกิน withdraw limit
            ValueError: ถ้ายอดเงินไม่พอ
            ValueError: ถ้า balance < annual fee (ATM only)
            ValueError: ถ้าเกิน daily limit (ATM/EDC only)
            ValueError: ถ้า channel ไม่มีเงินสดพอ
        
        TODO:
        1. Validate session (ATM/EDC)
        2. Validate amount > 0
        3. เรียก _check_withdraw_limit(amount)
        4. คำนวณ fee (ปัจจุบัน fee = 0 สำหรับทุกบัตร)
        5. Check balance >= (amount + fee)
        6. Check balance - amount - fee >= annual_fee (เฉพาะ ATM)
        7. Check daily limit (ATM/EDC only)
        8. Check channel has cash (ถ้ามี has_sufficient_cash)
        9. หักเงินจากบัญชี
        10. Update __daily_withdrawn (ATM/EDC only)
        11. dispense_cash (ถ้ามี)
        12. บันทึก transaction (W และ F ถ้ามี fee)
        13. แสดงข้อความสำเร็จ
        """
        pass
    
    def transfer(self, channel, amount, target_account):
        """โอนเงินไปบัญชีอื่น
        
        Args:
            channel: ช่องทางการทำธุรกรรม
            amount: จำนวนเงินที่โอน
            target_account: บัญชีปลายทาง (Account object)
        
        Raises:
            PermissionError: ถ้า session ไม่ถูกต้อง (ATM/EDC)
            ValueError: ถ้า amount <= 0
            ValueError: ถ้ายอดเงินไม่พอ
            ValueError: ถ้าเกิน daily limit (ATM/EDC only)
        
        TODO:
        1. Validate session (ATM/EDC)
        2. Validate amount > 0
        3. Check balance >= amount
        4. Check daily limit (ATM/EDC only)
        5. หักเงินจากบัญชีต้นทาง
        6. Update __daily_withdrawn (ATM/EDC only)
        7. เรียก target_account.receive_transfer()
        8. บันทึก transaction (type='TW')
        9. แสดงข้อความสำเร็จ
        """
        pass
    
    def receive_transfer(self, amount, channel, source_acc_no):
        """รับเงินโอน
        
        Args:
            amount: จำนวนเงินที่รับ
            channel: ช่องทางที่โอนมา
            source_acc_no: หมายเลขบัญชีต้นทาง
        
        TODO:
        1. เพิ่มเงินเข้าบัญชี
        2. บันทึก transaction (type='TD')
        """
        pass


class Card(ABC):
    """Base class สำหรับบัตรทุกประเภท
    
    Attributes:
        __card_no: หมายเลขบัตร
        __account_no: หมายเลขบัญชีที่เชื่อมกับบัตร
        __pin: รหัส PIN
    """
    
    def __init__(self, card_no, account_no, pin):
        """TODO: Initialize card attributes"""
        pass
    
    @property
    def card_no(self):
        """TODO: Return card number"""
        pass
    
    @property
    def account_no(self):
        """TODO: Return associated account number"""
        pass
    
    def validate_pin(self, pin_input):
        """ตรวจสอบ PIN
        
        Args:
            pin_input: PIN ที่ผู้ใช้ใส่
        
        Returns:
            bool: True ถ้า PIN ถูกต้อง
        
        TODO: เปรียบเทียบ pin_input กับ __pin
        """
        pass
    
    @abstractmethod
    def get_card_type(self):
        """ระบุประเภทบัตร (แต่ละ subclass ต้อง implement)
        
        Returns:
            str: ชื่อประเภทบัตร
        """
        pass


class Channel(ABC):
    """Base class สำหรับช่องทางการทำธุรกรรม"""
    
    @abstractmethod
    def authenticate(self, *args, **kwargs):
        """ยืนยันตัวตน (แต่ละ channel มีวิธีต่างกัน)"""
        pass


# ============================================================================
# ACCOUNT TYPES - Concrete Classes 
# ============================================================================

class SavingAccount(Account):
    """บัญชีออมทรัพย์
    
    Features:
    - ดอกเบี้ย 0.5% ต่อปี
    - ถอนไม่เกิน 40,000 บาท/ครั้ง (สำหรับทุกบัตร)
    """
    
    INTEREST_RATE = 0.005  # 0.5%
    WITHDRAW_LIMIT_PER_TRANSACTION = 40000
    
    def get_account_type(self):
        """TODO: Return "Saving Account" """
        pass
    
    def calculate_interest(self):
        """คำนวณและเพิ่มดอกเบี้ย 0.5%
        
        TODO:
        1. คำนวณ interest = amount * INTEREST_RATE
        2. เพิ่ม interest เข้า __amount
        3. บันทึก transaction (type='I', channel='SYSTEM', id='AUTO')
        4. แสดงข้อความและ return interest
        """
        pass
    
    def _check_withdraw_limit(self, amount):
        """ตรวจสอบ limit - ถอนไม่เกิน 40,000/ครั้ง
        
        TODO:
        - ถ้า amount > WITHDRAW_LIMIT_PER_TRANSACTION
        - raise ValueError พร้อมข้อความอธิบาย
        """
        pass


class FixedAccount(Account):
    """บัญชีฝากประจำ
    
    Features:
    - ดอกเบี้ย 2.5% ต่อปี
    - มีระยะเวลาฝาก (term_months)
    - ถอนก่อนกำหนดได้ดอกเบี้ย 50%
    """
    
    INTEREST_RATE = 0.025  # 2.5%
    EARLY_WITHDRAWAL_PENALTY = 0.5
    
    def __init__(self, account_no, user, amount, term_months=12):
        """TODO:
        1. เรียก super().__init__()
        2. เก็บ term_months
        3. เก็บ start_date = datetime.now()
        4. คำนวณ maturity_date = start_date + timedelta(days=term_months*30)
        """
        pass
    
    def get_account_type(self):
        """TODO: Return f"Fixed Account ({self.term_months} months)" """
        pass
    
    def calculate_interest(self, early_withdrawal=False):
        """คำนวณดอกเบี้ย 2.5% (หรือ 1.25% ถ้าถอนก่อนกำหนด)
        
        TODO:
        1. เริ่มจาก rate = INTEREST_RATE
        2. ถ้า early_withdrawal → rate *= EARLY_WITHDRAWAL_PENALTY
        3. คำนวณ interest = amount * rate * (term_months / 12)
        4. เพิ่ม interest เข้า __amount
        5. บันทึก transaction
        6. แสดงข้อความและ return interest
        """
        pass
    
    def _check_withdraw_limit(self, amount):
        """ฝากประจำสามารถถอนได้ แต่แสดง warning
        
        TODO:
        - ถ้า datetime.now() < maturity_date
        - แสดง warning message
        """
        pass


class CurrentAccount(Account):
    """บัญชีกระแสรายวัน
    
    Features:
    - ไม่มีดอกเบี้ย
    - ถอนไม่จำกัดจำนวน/ครั้ง
    - มี daily limit 40,000 เฉพาะ ATM/EDC
    """
    
    def get_account_type(self):
        """TODO: Return "Current Account" """
        pass
    
    def calculate_interest(self):
        """ไม่มีดอกเบี้ย
        
        TODO:
        - แสดงข้อความ "Current account: No interest"
        - return 0
        """
        pass
    
    def _check_withdraw_limit(self, amount):
        """ไม่มี limit ต่อครั้ง
        
        TODO: pass (ไม่ต้องทำอะไร)
        """
        pass


# ============================================================================
# CARD TYPES - Concrete Classes 
# ============================================================================

class ATM_Card(Card):
    """บัตร ATM ธรรมดา
    
    Features:
    - ใช้กับ ATM เท่านั้น (ไม่ใช้กับ EDC)
    - ค่าธรรมเนียมรายปี 100 บาท
    - ไม่มี cashback
    """
    
    ANNUAL_FEE = 100
    
    def get_card_type(self):
        """TODO: Return "ATM Card" """
        pass
    
    def charge_annual_fee(self, account):
        """หักค่าธรรมเนียมรายปี
        
        Args:
            account: Account object ที่จะหักเงิน
        
        Raises:
            ValueError: ถ้ายอดเงินไม่พอ
        
        TODO:
        1. Check account._Account__amount >= ANNUAL_FEE
        2. หักเงิน ANNUAL_FEE
        3. บันทึก transaction (type='F', channel='SYSTEM', id='ANNUAL_FEE')
        4. แสดงข้อความ
        """
        pass




# ============================================================================
# CHANNEL TYPES - Concrete Classes 
# ============================================================================

class ATM_machine(Channel):
    """ตู้ ATM
    
    Features:
    - ใช้ได้กับบัตรทุกประเภท
    - ต้องใส่บัตรและ PIN
    - ถอนสูงสุด 40,000/ครั้ง
    - มี daily limit ตามประเภทบัตร
    """
    
    def __init__(self, atm_no, money):
        """TODO:
        - เก็บ atm_no
        - เก็บ __money
        - สร้าง current_card = None
        """
        pass
    
    @property
    def money(self):
        """TODO: Return ATM cash balance"""
        pass
    
    def authenticate(self, card, pin):
        """ยืนยันตัวตนด้วยบัตรและ PIN
        
        TODO: เรียก insert_card(card, pin) และ return ผลลัพธ์
        """
        pass
    
    def insert_card(self, card, pin):
        """ใส่บัตรและตรวจสอบ PIN
        
        TODO:
        - เรียก card.validate_pin(pin)
        - ถ้าถูกต้อง → เก็บ current_card = card, return True
        - ถ้าไม่ถูก → return False
        """
        pass
    
    def eject_card(self):
        """TODO: ตั้ง current_card = None"""
        pass
    
    def has_sufficient_cash(self, amount):
        """TODO: return __money >= amount"""
        pass
    
    def dispense_cash(self, amount):
        """TODO: __money -= amount"""
        pass
    
    def receive_cash(self, amount):
        """TODO: __money += amount"""
        pass



# ============================================================================
# SUPPORTING CLASSES
# ============================================================================

class Bank:
    """ระบบธนาคาร - จัดการ Users, ATMs, EDCs, Counters"""
    
    ATM_FEE = 0  # ถอน ATM ฟรีทุกบัตร
    WITHDRAW_LIMIT = 40000  # วงเงินถอนมาตรฐาน
    
    def __init__(self, name):
        """TODO:
        - เก็บ name
        - สร้าง __user_list = []
        - สร้าง __atm_list = []
        - สร้าง __edc_list = []
        - สร้าง __counter_list = []
        """
        pass
    
    def add_user(self, user):
        """TODO: ตรวจสอบ type และเพิ่มเข้า __user_list"""
        pass
    
    def add_atm_machine(self, atm):
        """TODO: ตรวจสอบ type และเพิ่มเข้า __atm_list"""
        pass
    
    def add_edc_machine(self, edc):
        """TODO: ตรวจสอบ type และเพิ่มเข้า __edc_list"""
        pass
    
    def add_counter(self, counter):
        """TODO: ตรวจสอบ type และเพิ่มเข้า __counter_list"""
        pass
    
    def get_atm_by_id(self, atm_id):
        """TODO: หา ATM จาก atm_no และ return (หรือ None)"""
        pass
    
    def get_edc_by_id(self, edc_id):
        """TODO: หา EDC จาก edc_no และ return (หรือ None)"""
        pass
    
    def get_counter_by_id(self, counter_id):
        """TODO: หา Counter จาก counter_id และ return (หรือ None)"""
        pass
    
    def search_account_from_card(self, card_no):
        """ค้นหา account จากหมายเลขบัตร
        
        TODO:
        - วน loop users ทั้งหมด
        - เรียก user.search_account_from_card(card_no)
        - ถ้าเจอ return account
        - ถ้าไม่เจอ return None
        """
        pass


class User:
    """ผู้ใช้บริการธนาคาร"""
    
    def __init__(self, citizen_id, name):
        """TODO:
        - เก็บ citizen_id
        - เก็บ name
        - สร้าง __account_list = []
        """
        pass
    
    def add_account(self, account):
        """TODO: เพิ่ม account เข้า __account_list"""
        pass
    
    def search_account_from_card(self, card_no):
        """TODO:
        - วน loop accounts
        - ถ้า account มี card และ card.card_no == card_no
        - return account
        - ถ้าไม่เจอ return None
        """
        pass
    
    def get_all_accounts(self):
        """TODO: return __account_list"""
        pass


class Transaction:
    """รายการทำธุรกรรม
    
    Transaction Types:
        D  = Deposit (ฝากเงิน)
        W  = Withdraw (ถอนเงิน)
        TW = Transfer Withdraw (โอนออก)
        TD = Transfer Deposit (รับโอน)
        I  = Interest/Cashback (ดอกเบี้ย/เครดิตคืน)
        P  = Payment (ชำระเงินผ่าน EDC)
        F  = Fee (ค่าธรรมเนียม)
    """
    
    def __init__(self, type, channel_type, channel_id, amount, balance, target=None):
        """TODO:
        - เก็บ type, channel_type, channel_id
        - เก็บ amount, balance, target
        - เก็บ timestamp = datetime.now()
        """
        pass
    
    def __str__(self):
        """TODO:
        Format: "TYPE-CHANNEL_TYPE:CHANNEL_ID-AMOUNT-BALANCE[-TARGET]"
        Example: "D-ATM_machine:ATM-1001-5000.00-25000.00"
        Example: "TW-Counter:COUNTER-01-2000.00-23000.00-1000000003"
        """
        pass


#################################################################################
# TEST SETUP & EXECUTION
##################################################################################

def create_enhanced_bank_system():
    """สร้างระบบธนาคารพร้อม User, Account, Card และ Channel"""
    
    print("="*70)
    print("Setting up Enhanced Bank System with Inheritance")
    print("="*70 + "\n")
    
    bank = Bank("KMITL Bank")
    
    # ========== USER 1: Harry Potter (3 accounts) ==========
    harry = User('1-1101-12345-12-0', 'Harry Potter')
    
    # 1. Saving Account with Premium Card (Debit Card)
    harry_saving = SavingAccount('1000000001', harry, 20000)
    harry_premium_card = PremiumCard('12345', '1000000001', '1234')
    harry_saving.add_card(harry_premium_card)
    harry.add_account(harry_saving)
    
    # 2. Fixed Account (12 months) - no card
    harry_fixed = FixedAccount('1000000002', harry, 100000, term_months=12)
    harry.add_account(harry_fixed)
    
    # 3. Current Account - NO CARD (รับเงินจาก EDC/Transfer)
    harry_current = CurrentAccount('1000000003', harry, 50000)
    harry.add_account(harry_current)
    
    bank.add_user(harry)
    print(f"✓ Added user: {harry.name}")
    print(f"  - Saving Account: {harry_saving.account_no} = {harry_saving.amount:,.2f} THB (Premium Card)")
    print(f"  - Fixed Account: {harry_fixed.account_no} = {harry_fixed.amount:,.2f} THB")
    print(f"  - Current Account: {harry_current.account_no} = {harry_current.amount:,.2f} THB\n")
    
    # ========== USER 2: Hermione (Saving Account + Shopping Card) ==========
    hermione = User('1-1101-12345-13-0', 'Hermione Granger')
    hermione_saving = SavingAccount('2000000001', hermione, 30000)
    hermione_shopping_card = ShoppingCard('22345', '2000000001', '5678')
    hermione_saving.add_card(hermione_shopping_card)
    hermione.add_account(hermione_saving)
    bank.add_user(hermione)
    print(f"✓ Added user: {hermione.name}")
    print(f"  - Saving Account: {hermione_saving.account_no} = {hermione_saving.amount:,.2f} THB (Shopping Card)\n")
    
    # ========== MERCHANT: Shop ABC (Current Account for EDC) ==========
    merchant = User('1-9999-99999-99-0', 'Shop ABC')
    merchant_account = CurrentAccount('9000000001', merchant, 100000)
    merchant.add_account(merchant_account)
    bank.add_user(merchant)
    print(f"✓ Added merchant: {merchant.name}")
    print(f"  - Merchant Account: {merchant_account.account_no} = {merchant_account.amount:,.2f} THB\n")
    
    # ========== CHANNELS ==========
    bank.add_atm_machine(ATM_machine('ATM-1001', 1000000))
    bank.add_counter(Counter('COUNTER-01'))
    bank.add_edc_machine(EDC_machine('EDC-001', merchant_account))
    print("✓ Added channels: ATM-1001, COUNTER-01, EDC-001\n")
    
    return bank, harry, hermione, merchant


def run_optimized_validation_tests():
    """ทดสอบครบทุกเงื่อนไข validation - 33 tests"""
    
    bank, harry, hermione, merchant = create_enhanced_bank_system()
    
    # Get accounts
    harry_saving = harry.get_all_accounts()[0]
    harry_fixed = harry.get_all_accounts()[1]
    harry_current = harry.get_all_accounts()[2]
    hermione_saving = hermione.get_all_accounts()[0]
    merchant_account = merchant.get_all_accounts()[0]
    
    # Get channels
    atm = bank.get_atm_by_id('ATM-1001')
    counter = bank.get_counter_by_id('COUNTER-01')
    edc = bank.get_edc_by_id('EDC-001')
    
    # ========== GROUP 1: AMOUNT & SESSION VALIDATIONS ==========
    print("\n" + "="*70)
    print("[GROUP 1] Amount & Session Validations (6 tests)")
    print("="*70)
    
    # Test 1: Session validation (covers all operations)
    print("\n[Test 1] Session - No Card (covers Deposit/Withdraw/Transfer)")
    try:
        harry_saving.withdraw(atm, 1000)
    except PermissionError as e:
        print(f"✓ Expected Error: {e}")
    
    # Test 2: Zero amount (covers account operations)
    print("\n[Test 2] Amount - Zero (covers Deposit/Withdraw/Transfer)")
    atm.insert_card(harry_saving.card, '1234')
    try:
        harry_saving.deposit(atm, 0)
    except ValueError as e:
        print(f"✓ Expected Error: {e}")
    atm.eject_card()
    
    # Test 3: Zero amount for Pay (separate because different method)
    print("\n[Test 3] Amount - Zero for EDC Pay")
    edc.swipe_card(hermione_saving.card, '5678')
    try:
        edc.pay(hermione_saving, 0)
    except ValueError as e:
        print(f"✓ Expected Error: {e}")
    edc.eject_card()
    
    # Test 4: Negative amount (covers all operations)
    print("\n[Test 4] Amount - Negative (covers Deposit/Withdraw/Transfer)")
    atm.insert_card(harry_saving.card, '1234')
    try:
        harry_saving.deposit(atm, -500)
    except ValueError as e:
        print(f"✓ Expected Error: {e}")
    atm.eject_card()
    
    # Test 5: PIN validation - Wrong PIN
    print("\n[Test 5] PIN - Wrong PIN (covers ATM & EDC)")
    result = atm.insert_card(harry_saving.card, '9999')
    print(f"✓ Card accepted: {result} (Expected: False)")
    
    # Test 6: PIN validation - Correct PIN
    print("\n[Test 6] PIN - Correct PIN")
    result = atm.insert_card(harry_saving.card, '1234')
    print(f"✓ Card accepted: {result} (Expected: True)")
    
    # ========== GROUP 2: ACCOUNT OPERATIONS ==========
    print("\n" + "="*70)
    print("[GROUP 2] Account Operations (11 tests)")
    print("="*70)
    
    # Test 7: Deposit success (ATM)
    print("\n[Test 7] Deposit - Success via ATM")
    harry_saving.deposit(atm, 5000)
    
    # Test 8: Deposit success (Counter)
    print("\n[Test 8] Deposit - Success via Counter")
    atm.eject_card()
    counter.verify_identity(harry_saving, '1-1101-12345-12-0')
    harry_saving.deposit(counter, 10000)
    counter.clear_session() # ลบ authenticated Account
    
    # Test 9: Withdraw - Saving Account limit 40,000/ครั้ง (test กับ Shopping Card)
    print("\n[Test 9] Withdraw - Saving Account Limit (40,000/transaction)")
    atm.insert_card(hermione_saving.card, '5678')
    try:
        hermione_saving.withdraw(atm, 45000)
    except ValueError as e:
        print(f"✓ Expected Error: {e}")
        print(f"  ✓ Shopping Card uses Saving Account default limit (40,000)")
    atm.eject_card()
    
    # Test 10: Withdraw - Premium Card ถอนได้ 40,000/ครั้ง (เหมือนบัตรอื่น)
    print("\n[Test 10] Withdraw - Premium Card (40,000/transaction limit)")
    atm.insert_card(harry_saving.card, '1234')
    harry_saving.deposit(atm, 100000)
    
    # ถอน 40,000 (ถอนได้)
    harry_saving.withdraw(atm, 40000)
    print(f"  ✓ Withdrew 40,000 THB (Premium Card follows 40,000/transaction limit)")
    print(f"  ✓ Daily withdrawn: 40,000 / 100,000")
    
    # ถอน 50,000 (ต้อง error)
    try:
        harry_saving.withdraw(atm, 50000)
        raise AssertionError("❌ Should not allow withdrawal > 40,000!")
    except ValueError as e:
        print(f"  ✓ Cannot withdraw 50,000: {e}")
        print(f"  ✓ Premium Card also limited to 40,000/transaction")
    
    # Test 11: Withdraw - Must keep balance > annual fee
    print("\n[Test 11] Withdraw - Must Keep Balance > Annual Fee (ATM only)")
    try:
        # พยายามถอนจนเหลือน้อยกว่า 500
        harry_saving.withdraw(atm, harry_saving.amount - 400)
    except ValueError as e:
        print(f"✓ Expected Error: {e}")
        print(f"  ✓ ATM enforces minimum balance = annual fee")
    atm.eject_card()
    
    # Test 12: Withdraw - Shopping Card Success (within limit)
    print("\n[Test 12] Withdraw - Shopping Card Success (within 40,000 limit)")
    atm.insert_card(hermione_saving.card, '5678')
    hermione_saving.withdraw(atm, 20000)
    print(f"  ✓ Withdrew 20,000 THB (Shopping Card limit = 40,000)")
    atm.eject_card()
    
    # Test 13: Withdraw - Insufficient balance
    print("\n[Test 13] Withdraw - Insufficient Balance")
    atm.insert_card(hermione_saving.card, '5678')
    try:
        hermione_saving.withdraw(atm, 100000)
    except ValueError as e:
        print(f"✓ Expected Error: {e}")
    atm.eject_card()
    
    # Test 14: Withdraw - ATM insufficient cash
    print("\n[Test 14] Withdraw - ATM Insufficient Cash")
    small_atm = ATM_machine('ATM-SMALL', 500)
    small_atm.insert_card(harry_saving.card, '1234')
    try:
        harry_saving.withdraw(small_atm, 1000)
    except ValueError as e:
        print(f"✓ Expected Error: {e}")
    small_atm.eject_card()
    
    # Test 15: Daily limit - Premium Card (100,000/day)
    print("\n[Test 15] Daily Limit - Premium Card (100,000/day)")
    atm.insert_card(harry_saving.card, '1234')
    
    print(f"  Daily withdrawn so far: 40,000 THB (from Test 10)")
    print(f"  Remaining daily limit: 60,000 THB")
    
    harry_saving.deposit(atm, 100000)
    print(f"  Current balance: {harry_saving.amount:.2f} THB")
    
    # ถอน 40,000 (total = 40,000 + 40,000 = 80,000)
    harry_saving.withdraw(atm, 40000)
    print("  ✓ Withdrew 40,000 (daily used: 80,000)")
    
    # ถอน 20,000 (total = 80,000 + 20,000 = 100,000)
    harry_saving.withdraw(atm, 20000)
    print("  ✓ Withdrew 20,000 (daily used: 100,000)")
    print(f"  ✓ Premium Card daily limit: 100,000 (used: 100,000, remaining: 0)")
    
    # พยายามถอนอีก (ต้อง error)
    try:
        harry_saving.withdraw(atm, 10000)
        raise AssertionError("❌ Should not allow withdrawal exceeding daily limit!")
    except ValueError as e:
        print(f"  ✓ Cannot withdraw more: {e}")
    
    # Test 16: Transfer - Insufficient balance
    print("\n[Test 16] Transfer - Insufficient Balance")
    try:
        harry_saving.transfer(atm, 200000, hermione_saving)
    except ValueError as e:
        print(f"✓ Expected Error: {e}")
    
    # Test 17: Transfer - Same user via Counter (bypass daily limit)
    print("\n[Test 17] Transfer - Success (Same User via Counter)")
    atm.eject_card()
    counter.verify_identity(harry_saving, '1-1101-12345-12-0')
    harry_saving.deposit(counter, 10000)
    harry_saving.transfer(counter, 2000, harry_current)
    print("  ✓ Transfer via Counter bypasses daily limit")
    counter.clear_session()
    
    # ========== GROUP 3: ACCOUNT TYPE SPECIFIC ==========
    print("\n" + "="*70)
    print("[GROUP 3] Account Type Specific (5 tests)")
    print("="*70)
    
    # Test 18: Saving - Interest
    print("\n[Test 18] Saving Account - Interest (0.5%)")
    
    # เก็บค่าก่อนคำนวณ
    balance_before = harry_saving.amount
    txn_count_before = harry_saving.get_transaction_count()
    
    # คำนวณดอกเบี้ย
    interest = harry_saving.calculate_interest()
    
    # คำนวณค่าที่คาดหวัง
    expected_interest = balance_before * SavingAccount.INTEREST_RATE
    balance_after = harry_saving.amount
    
    # ตรวจสอบค่าดอกเบี้ย
    assert abs(interest - expected_interest) < 0.01, \
        f"Interest mismatch: got {interest:.2f}, expected {expected_interest:.2f}"
    print(f"  ✓ Interest calculated: {interest:.2f} THB")
    print(f"  ✓ Expected (0.5%): {expected_interest:.2f} THB")
    
    # ตรวจสอบยอดเงิน
    assert abs(balance_after - (balance_before + interest)) < 0.01, \
        f"Balance not updated correctly: {balance_after:.2f} vs {balance_before + interest:.2f}"
    print(f"  ✓ Balance: {balance_before:.2f} → {balance_after:.2f} THB")
    
    # ตรวจสอบ transaction
    last_txn = harry_saving.get_last_transaction()
    assert last_txn is not None, "No transaction recorded"
    assert last_txn.type == 'I', f"Wrong transaction type: {last_txn.type}, expected 'I'"
    assert abs(last_txn.amount - interest) < 0.01, \
        f"Transaction amount mismatch: {last_txn.amount:.2f} vs {interest:.2f}"
    assert last_txn.channel_type == 'SYSTEM', \
        f"Wrong channel type: {last_txn.channel_type}, expected 'SYSTEM'"
    assert last_txn.channel_id == 'AUTO', \
        f"Wrong channel ID: {last_txn.channel_id}, expected 'AUTO'"
    print(f"  ✓ Transaction recorded: {last_txn}")
    
    # ตรวจสอบจำนวน transactions
    assert harry_saving.get_transaction_count() == txn_count_before + 1, \
        f"Transaction count mismatch: {harry_saving.get_transaction_count()} vs {txn_count_before + 1}"
    print(f"  ✓ Transaction count increased: {txn_count_before} → {harry_saving.get_transaction_count()}")
    
    # Test 19: Fixed - Interest
    print("\n[Test 19] Fixed Account - Interest (2.5%)")
    
    # เก็บค่าก่อนคำนวณ
    balance_before = harry_fixed.amount
    txn_count_before = harry_fixed.get_transaction_count()
    
    # คำนวณดอกเบี้ย
    interest = harry_fixed.calculate_interest()
    
    # คำนวณค่าที่คาดหวัง
    term_ratio = harry_fixed.term_months / 12
    expected_interest = balance_before * FixedAccount.INTEREST_RATE * term_ratio
    balance_after = harry_fixed.amount
    
    # ตรวจสอบค่าดอกเบี้ย
    assert abs(interest - expected_interest) < 0.01, \
        f"Interest mismatch: got {interest:.2f}, expected {expected_interest:.2f}"
    print(f"  ✓ Interest calculated: {interest:.2f} THB")
    print(f"  ✓ Expected (2.5% × {term_ratio}): {expected_interest:.2f} THB")
    
    # ตรวจสอบยอดเงิน
    assert abs(balance_after - (balance_before + interest)) < 0.01, \
        "Balance not updated correctly"
    print(f"  ✓ Balance: {balance_before:.2f} → {balance_after:.2f} THB")
    
    # ตรวจสอบ transaction
    last_txn = harry_fixed.get_last_transaction()
    assert last_txn is not None, "No transaction recorded"
    assert last_txn.type == 'I', f"Wrong transaction type: {last_txn.type}"
    assert abs(last_txn.amount - interest) < 0.01, "Transaction amount mismatch"
    assert last_txn.channel_type == 'SYSTEM', "Wrong channel type"
    assert last_txn.channel_id == 'AUTO', "Wrong channel ID"
    print(f"  ✓ Transaction recorded: {last_txn}")
    
    # ตรวจสอบจำนวน transactions
    assert harry_fixed.get_transaction_count() == txn_count_before + 1, \
        "Transaction count not increased"
    print(f"  ✓ Transaction count increased: {txn_count_before} → {harry_fixed.get_transaction_count()}")
    
    # Test 20: Fixed - Early withdrawal warning
    print("\n[Test 20] Fixed Account - Early Withdrawal Warning")
    
    # ตรวจสอบว่ายังไม่ครบกำหนด
    from datetime import datetime
    assert datetime.now() < harry_fixed.maturity_date, \
        "Test invalid: account already matured"
    print(f"  ✓ Not matured yet (maturity: {harry_fixed.maturity_date.date()})")
    
    balance_before = harry_fixed.amount
    txn_count_before = harry_fixed.get_transaction_count()
    
    counter.verify_identity(harry_fixed, '1-1101-12345-12-0')
    harry_fixed.withdraw(counter, 1000)
    
    # ตรวจสอบยอดเงิน
    balance_after = harry_fixed.amount
    assert abs(balance_after - (balance_before - 1000)) < 0.01, \
        f"Balance incorrect: {balance_after:.2f} vs {balance_before - 1000:.2f}"
    print(f"  ✓ Withdrawal allowed (with penalty warning)")
    print(f"  ✓ Balance: {balance_before:.2f} → {balance_after:.2f} THB")
    
    # ตรวจสอบ transaction
    last_txn = harry_fixed.get_last_transaction()
    assert last_txn is not None, "No transaction recorded"
    assert last_txn.type == 'W', f"Wrong transaction type: {last_txn.type}"
    assert abs(last_txn.amount - 1000) < 0.01, \
        f"Transaction amount wrong: {last_txn.amount:.2f}"
    print(f"  ✓ Transaction recorded: {last_txn}")
    
    # ตรวจสอบจำนวน transactions
    assert harry_fixed.get_transaction_count() == txn_count_before + 1, \
        "Transaction not added"
    print(f"  ✓ Transaction count increased: {txn_count_before} → {harry_fixed.get_transaction_count()}")
    
    counter.clear_session()
    
    # Test 21: Current - No interest
    print("\n[Test 21] Current Account - No Interest")
    
    balance_before = harry_current.amount
    txn_count_before = harry_current.get_transaction_count()
    
    # คำนวณดอกเบี้ย
    interest = harry_current.calculate_interest()
    
    # ตรวจสอบว่าไม่มีดอกเบี้ย
    assert interest == 0, \
        f"Current account should have no interest, got {interest:.2f}"
    print(f"  ✓ Interest: {interest:.2f} THB (as expected)")
    
    # ตรวจสอบว่ายอดเงินไม่เปลี่ยน
    assert abs(harry_current.amount - balance_before) < 0.01, \
        f"Balance should not change: {harry_current.amount:.2f} vs {balance_before:.2f}"
    print(f"  ✓ Balance unchanged: {balance_before:.2f} THB")
    
    # ตรวจสอบว่าไม่มี transaction ใหม่
    current_txn_count = harry_current.get_transaction_count()
    assert current_txn_count == txn_count_before, \
        f"Should not record transaction: {current_txn_count} vs {txn_count_before}"
    print(f"  ✓ No transaction recorded (count: {current_txn_count})")
    
    # Test 22: Current - Large withdrawal (no limit per transaction)
    print("\n[Test 22] Current Account - Large Withdrawal (No Per-Transaction Limit)")
    
    balance_before = harry_current.amount
    txn_count_before = harry_current.get_transaction_count()
    
    counter.verify_identity(harry_current, '1-1101-12345-12-0')
    harry_current.withdraw(counter, 20000)
    
    # ตรวจสอบยอดเงิน
    balance_after = harry_current.amount
    assert abs(balance_after - (balance_before - 20000)) < 0.01, \
        "Balance not updated correctly"
    print(f"  ✓ Withdrew 20,000 THB (no per-transaction limit)")
    print(f"  ✓ Balance: {balance_before:.2f} → {balance_after:.2f} THB")
    
    # ตรวจสอบ transaction
    last_txn = harry_current.get_last_transaction()
    assert last_txn is not None, "No transaction recorded"
    assert last_txn.type == 'W', f"Wrong transaction type: {last_txn.type}"
    assert abs(last_txn.amount - 20000) < 0.01, "Transaction amount mismatch"
    print(f"  ✓ Transaction recorded: {last_txn}")
    
    # ตรวจสอบจำนวน transactions
    assert harry_current.get_transaction_count() == txn_count_before + 1, \
        "Transaction not added"
    print(f"  ✓ Transaction count increased: {txn_count_before} → {harry_current.get_transaction_count()}")
    
    counter.clear_session()
    
    # ========== GROUP 4: CARD & FEES ==========
    print("\n" + "="*70)
    print("[GROUP 4] Card & Fees (5 tests)")
    print("="*70)
    
    # Test 23: Annual fee - Insufficient
    print("\n[Test 23] Debit Card - Annual Fee Insufficient Balance")
    poor_user = User('1-2222-22222-22-2', 'Poor User')
    poor_account = SavingAccount('3000000001', poor_user, 100)
    poor_card = ShoppingCard('33333', '3000000001', '1111')
    poor_account.add_card(poor_card)
    try:
        poor_card.charge_annual_fee(poor_account)
    except ValueError as e:
        print(f"✓ Expected Error: {e}")
    
    # Test 24: Annual fee - ATM Card (100 THB)
    print("\n[Test 24] ATM Card - Annual Fee Success (100 THB)")
    atm_user = User('1-3333-33333-33-3', 'ATM User')
    atm_account = SavingAccount('4000000001', atm_user, 5000)
    atm_card = ATM_Card('44444', '4000000001', '9999')
    atm_account.add_card(atm_card)
    atm_card.charge_annual_fee(atm_account)
    print(f"  ✓ ATM Card annual fee = 100 THB")
    
    # Test 25: Annual fee - Premium Card (500 THB)
    print("\n[Test 25] Premium Card - Annual Fee Success (500 THB)")
    harry_saving.card.charge_annual_fee(harry_saving)
    
    # Test 26: Premium Card - Cashback 2%
    print("\n[Test 26] Premium Card - Cashback 2% (no minimum)")
    atm.insert_card(harry_saving.card, '1234')
    harry_saving.deposit(atm, 50000)
    atm.eject_card()
    edc.swipe_card(harry_saving.card, '1234')
    edc.pay(harry_saving, 5000)
    print(f"  Total Cashback (Premium): {harry_saving.card.cashback:.2f} THB")
    edc.eject_card()
    
    # Test 27: Shopping Card - Cashback 1%
    print("\n[Test 27] Shopping Card - Cashback 1% (>= 1000)")
    edc.swipe_card(hermione_saving.card, '5678')
    edc.pay(hermione_saving, 3000)
    print(f"  Total Cashback (Shopping): {hermione_saving.card.cashback:.2f} THB")
    edc.eject_card()
    
    # ========== GROUP 5: CHANNEL VALIDATIONS ==========
    print("\n" + "="*70)
    print("[GROUP 5] Channel Validations (3 tests)")
    print("="*70)
    
    # Test 28: Counter - Wrong Citizen ID
    print("\n[Test 28] Counter - Wrong Citizen ID")
    try:
        counter.verify_identity(harry_saving, '0-0000-00000-00-0')
    except PermissionError as e:
        print(f"✓ Expected Error: {e}")
    
    # Test 29: EDC - Pay without swipe
    print("\n[Test 29] EDC - Pay Without Swipe")
    try:
        edc.pay(hermione_saving, 1000)
    except PermissionError as e:
        print(f"✓ Expected Error: {e}")
    
    # Test 30: EDC - Pay insufficient balance
    print("\n[Test 30] EDC - Pay Insufficient Balance")
    edc.swipe_card(hermione_saving.card, '5678')
    try:
        edc.pay(hermione_saving, 100000)
    except ValueError as e:
        print(f"✓ Expected Error: {e}")
    edc.eject_card()
    
    # ========== GROUP 6: SYSTEM VALIDATIONS ==========
    print("\n" + "="*70)
    print("[GROUP 6] System Validations (3 tests)")
    print("="*70)
    
    # Test 31: Bank type validations (combined)
    print("\n[Test 31] Bank - Type Validations (User/ATM/EDC/Counter)")
    errors = []
    try:
        bank.add_user("not user")
    except TypeError:
        errors.append("User")
    try:
        bank.add_atm_machine("not atm")
    except TypeError:
        errors.append("ATM")
    try:
        bank.add_edc_machine("not edc")
    except TypeError:
        errors.append("EDC")
    try:
        bank.add_counter("not counter")
    except TypeError:
        errors.append("Counter")
    print(f"✓ All type checks passed: {', '.join(errors)}")
    
    # Test 32: Search - Non-existent card
    print("\n[Test 32] Search - Non-existent Card")
    result = bank.search_account_from_card('99999')
    print(f"✓ Search result: {result} (Expected: None)")
    
    # Test 33: EDC Constructor - Wrong merchant type
    print("\n[Test 33] EDC Constructor - Wrong Merchant Account Type")
    try:
        wrong_edc = EDC_machine('EDC-999', harry_saving)
    except TypeError as e:
        print(f"✓ Expected Error: {e}")
    
    print("\n" + "="*70)
    print("✅ PART 1 COMPLETED - 33 Validation Tests Passed!")
    print("="*70)
    
    return bank, harry, hermione, merchant


def run_inheritance_tests():
    """Test cases ที่ ENFORCE inheritance และ polymorphism - 12 tests"""
    
    print("\n\n" + "="*70)
    print("PART 2: INHERITANCE & POLYMORPHISM ENFORCEMENT - 12 Tests")
    print("="*70)
    print("\n⚠️  Creating fresh bank system for Part 2 tests...")
    
    # ========== สร้างระบบใหม่ทั้งหมด ==========
    bank = Bank("KMITL Bank")
    
    # USER 1: Harry Potter
    harry = User('1-1101-12345-12-0', 'Harry Potter')
    harry_saving = SavingAccount('1000000001', harry, 20000)
    harry_premium_card = PremiumCard('12345', '1000000001', '1234')
    harry_saving.add_card(harry_premium_card)
    harry.add_account(harry_saving)
    
    harry_fixed = FixedAccount('1000000002', harry, 100000, term_months=12)
    harry.add_account(harry_fixed)
    
    harry_current = CurrentAccount('1000000003', harry, 50000)
    harry.add_account(harry_current)
    
    bank.add_user(harry)
    
    # USER 2: Hermione
    hermione = User('1-1101-12345-13-0', 'Hermione Granger')
    hermione_saving = SavingAccount('2000000001', hermione, 30000)
    hermione_shopping_card = ShoppingCard('22345', '2000000001', '5678')
    hermione_saving.add_card(hermione_shopping_card)
    hermione.add_account(hermione_saving)
    bank.add_user(hermione)
    
    # MERCHANT
    merchant = User('1-9999-99999-99-0', 'Shop ABC')
    merchant_account = CurrentAccount('9000000001', merchant, 100000)
    merchant.add_account(merchant_account)
    bank.add_user(merchant)
    
    # CHANNELS
    bank.add_atm_machine(ATM_machine('ATM-1001', 1000000))
    bank.add_counter(Counter('COUNTER-01'))
    bank.add_edc_machine(EDC_machine('EDC-001', merchant_account))
    
    # Get references
    harry_saving = harry.get_all_accounts()[0]
    harry_fixed = harry.get_all_accounts()[1]
    harry_current = harry.get_all_accounts()[2]
    hermione_saving = hermione.get_all_accounts()[0]
    
    atm = bank.get_atm_by_id('ATM-1001')
    counter = bank.get_counter_by_id('COUNTER-01')
    edc = bank.get_edc_by_id('EDC-001')
    
    print("✓ Fresh bank system created (no daily limits from Part 1)\n")
    
    # ========== INHERITANCE CHECKS ==========
    
    # Test 1: All accounts must inherit from Account
    print("\n[Test 1] Verify Inheritance - All accounts are Account instances")
    accounts = [harry_saving, harry_fixed, harry_current, hermione_saving]
    for i, acc in enumerate(accounts, 1):
        if isinstance(acc, Account):
            print(f"  ✓ Account {i}: {type(acc).__name__} inherits from Account")
        else:
            raise AssertionError(f"❌ {type(acc).__name__} does NOT inherit from Account!")
    
    # Test 2: All cards must inherit from Card
    print("\n[Test 2] Verify Inheritance - All cards are Card instances")
    cards = [harry_saving.card, hermione_saving.card]
    for i, card in enumerate(cards, 1):
        if isinstance(card, Card):
            print(f"  ✓ Card {i}: {type(card).__name__} inherits from Card")
        else:
            raise AssertionError(f"❌ {type(card).__name__} does NOT inherit from Card!")
    
    # Test 3: All channels must inherit from Channel
    print("\n[Test 3] Verify Inheritance - All channels are Channel instances")
    channels = [atm, counter, edc]
    for i, ch in enumerate(channels, 1):
        if isinstance(ch, Channel):
            print(f"  ✓ Channel {i}: {type(ch).__name__} inherits from Channel")
        else:
            raise AssertionError(f"❌ {type(ch).__name__} does NOT inherit from Channel!")
    
    # Test 4: Cannot instantiate abstract base class Account
    print("\n[Test 4] Abstract Base Class - Cannot instantiate Account directly")
    try:
        dummy_user = User('0-0000-00000-00-0', 'Dummy')
        abstract_account = Account('999', dummy_user, 1000)
        raise AssertionError("❌ Should NOT be able to instantiate Account!")
    except TypeError as e:
        print(f"  ✓ Expected Error: Can't instantiate abstract class")
    
    # Test 5: Cannot instantiate Card ABC
    print("\n[Test 5] Abstract Base Class - Cannot instantiate Card directly")
    try:
        abstract_card = Card('999', '999', '9999')
        raise AssertionError("❌ Should NOT be able to instantiate Card!")
    except TypeError as e:
        print(f"  ✓ Expected Error: Can't instantiate abstract class")
    
    # Test 6: Polymorphic calculate_interest()
    print("\n[Test 6] Polymorphism - calculate_interest() behaves differently")
    test_accounts = [
        (harry_saving, "Saving", 0.005),
        (harry_fixed, "Fixed", 0.025),
        (harry_current, "Current", 0.0)
    ]
    
    for acc, name, expected_rate in test_accounts:
        initial = acc.amount
        interest = acc.calculate_interest()
        
        if name == "Current":
            if interest == 0:
                print(f"  ✓ {name}: No interest (Rate: {expected_rate*100}%)")
            else:
                raise AssertionError(f"❌ {name}: Should have no interest!")
        else:
            if interest > 0:
                print(f"  ✓ {name}: Interest = {interest:.2f} (Rate: {expected_rate*100}%)")
            else:
                raise AssertionError(f"❌ {name}: Should have interest!")
    
    # Test 7: Polymorphic _check_withdraw_limit()
    print("\n[Test 7] Polymorphism - All cards limited to 40,000/transaction")
    
    # Premium Card: limit 40,000 (ไม่มี override แล้ว)
    atm.insert_card(harry_saving.card, '1234')
    try:
        harry_saving.withdraw(atm, 50000)
        raise AssertionError("❌ Premium Card should reject > 40,000!")
    except ValueError:
        print("  ✓ Premium Card: Limit 40,000 enforced (no override)")
    atm.eject_card()
    
    # Shopping Card: limit 40,000 (Saving default)
    atm.insert_card(hermione_saving.card, '5678')
    try:
        hermione_saving.withdraw(atm, 45000)
        raise AssertionError("❌ Shopping Card should reject > 40,000!")
    except ValueError:
        print("  ✓ Shopping Card: Limit 40,000 enforced (Saving default)")
    atm.eject_card()
    
    # Test 8: Polymorphic get_account_type()
    print("\n[Test 8] Polymorphism - get_account_type() returns different values")
    expected_types = {
        'SavingAccount': 'Saving Account',
        'FixedAccount': 'Fixed Account (12 months)',
        'CurrentAccount': 'Current Account'
    }
    
    for acc in [harry_saving, harry_fixed, harry_current]:
        class_name = type(acc).__name__
        account_type = acc.get_account_type()
        expected = expected_types.get(class_name, '')
        
        if account_type == expected:
            print(f"  ✓ {class_name}: '{account_type}'")
        else:
            raise AssertionError(f"❌ {class_name}: Wrong type '{account_type}'!")
    
    # Test 9: Polymorphic card types
    print("\n[Test 9] Polymorphism - Different card types")
    card_types = [
        (harry_saving.card, "Premium Card"),
        (hermione_saving.card, "Shopping Card")
    ]
    
    for card, expected_name in card_types:
        card_type = card.get_card_type()
        if expected_name in card_type:
            print(f"  ✓ {type(card).__name__}: {card_type}")
        else:
            raise AssertionError(f"❌ Wrong card type!")
    
    # Test 10: Card features comparison
    print("\n[Test 10] Card Features - Premium vs Shopping vs ATM")
    print(f"  ATM Card:")
    print(f"    - Annual Fee: 100 THB")
    print(f"    - Per-Transaction Limit: 40,000 (default)")
    print(f"  Shopping Card:")
    print(f"    - Annual Fee: 300 THB")
    print(f"    - Daily Limit: {hermione_saving.card.DAILY_LIMIT:,}")
    print(f"    - Per-Transaction Limit: 40,000")
    print(f"    - Cashback Rate: {hermione_saving.card.CASHBACK_RATE*100}%")
    print(f"  Premium Card:")
    print(f"    - Annual Fee: 500 THB")
    print(f"    - Daily Limit: {harry_saving.card.DAILY_LIMIT:,} (สิทธิพิเศษ)")
    print(f"    - Per-Transaction Limit: 40,000 (เหมือนบัตรอื่น)")
    print(f"    - Cashback Rate: {harry_saving.card.CASHBACK_RATE*100}%")
    print(f"  ✓ Premium Card ข้อได้เปรียบคือ Daily Limit สูงกว่า (100,000 vs 40,000)")
    
    # Test 11: Polymorphic list processing
    print("\n[Test 11] Polymorphism - Process mixed types in single list")
    all_accounts = [harry_saving, harry_fixed, harry_current, hermione_saving]
    
    print("  ✓ Processed mixed account types polymorphically:")
    for acc in all_accounts:
        print(f"    - {type(acc).__name__}: {acc.get_account_type()} = {acc.amount:.2f}")
    

def print_final_summary(bank, harry, hermione, merchant):
    """แสดงสรุปสุดท้าย"""
    
    harry_saving = harry.get_all_accounts()[0]
    harry_fixed = harry.get_all_accounts()[1]
    harry_current = harry.get_all_accounts()[2]
    hermione_saving = hermione.get_all_accounts()[0]
    merchant_account = merchant.get_all_accounts()[0]
    atm = bank.get_atm_by_id('ATM-1001')
    
    print("\n\n" + "="*70)
    print("FINAL SUMMARY")
    print("="*70)
    
    print("\nTRANSACTION HISTORY:")
    print("-"*70)
    harry_saving.print_transactions()
    harry_fixed.print_transactions()
    harry_current.print_transactions()
    hermione_saving.print_transactions()
    merchant_account.print_transactions()
    
    print("\n" + "="*70)
    print("FINAL BALANCES")
    print("="*70)
    print(f"Harry Saving:      {harry_saving.amount:>12,.2f} THB (Premium Card)")
    print(f"Harry Fixed:       {harry_fixed.amount:>12,.2f} THB")
    print(f"Harry Current:     {harry_current.amount:>12,.2f} THB")
    print(f"Hermione Saving:   {hermione_saving.amount:>12,.2f} THB (Shopping Card)")
    print(f"Merchant:          {merchant_account.amount:>12,.2f} THB")
    print(f"ATM Cash:          {atm.money:>12,.2f} THB")
    
    print("\n" + "="*70)
    print("CARD INFORMATION")
    print("="*70)
    print(f"Harry Premium Card:")
    print(f"  - Type: {harry_saving.card.get_card_type()}")
    print(f"  - Annual Fee: {harry_saving.card.ANNUAL_FEE} THB")
    print(f"  - Daily Limit: {harry_saving.card.DAILY_LIMIT:,} THB (สิทธิพิเศษ)")
    print(f"  - Per-Transaction Limit: 40,000 THB (เหมือนบัตรอื่น)")
    print(f"  - Total Cashback: {harry_saving.card.cashback:.2f} THB")
    print(f"\nHermione Shopping Card:")
    print(f"  - Type: {hermione_saving.card.get_card_type()}")
    print(f"  - Annual Fee: {hermione_saving.card.ANNUAL_FEE} THB")
    print(f"  - Daily Limit: {hermione_saving.card.DAILY_LIMIT:,} THB")
    print(f"  - Per-Transaction Limit: {hermione_saving.card.WITHDRAW_LIMIT_PER_TRANSACTION:,} THB")
    print(f"  - Total Cashback: {hermione_saving.card.cashback:.2f} THB")
    
    print("\n" + "="*70)
    print("REQUIREMENTS COMPLIANCE")
    print("="*70)
    print("✅ Saving Account: Withdraw limit 40,000/transaction (ทุกบัตร)")
    print("✅ Premium Card: Per-transaction limit 40,000 (เหมือนบัตรอื่น)")
    print("✅ Premium Card: Daily limit 100,000 (สิทธิพิเศษ)")
    print("✅ Shopping Card: Daily limit 40,000")
    print("✅ ATM Card: Annual fee 100 THB")
    print("✅ ATM withdraw: Must keep balance > annual fee")
    print("✅ Current Account: Daily limit 40,000 (ATM/EDC only)")


if __name__ == "__main__":
    # Part 1: Run validation tests
    bank, harry, hermione, merchant = run_optimized_validation_tests()
    
    # Part 2: Run inheritance/polymorphism tests
    run_inheritance_tests()
    
    # Print final summary
    print_final_summary(bank, harry, hermione, merchant)