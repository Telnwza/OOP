from typing import List, Union, Optional

##################################################################################
# Instruction for Students:
# 1. จงเขียน Class Diagram เพื่อออกแบบ Class ต่างๆ ให้รองรับการทำงานของ Code ส่วนล่าง
# 2. จงเขียน Class Definition (Bank, User, Account, ATM_Card, ATM_machine, Transaction)
#    เพื่อให้สามารถรัน Function run_test() ได้โนดในเอกสาร Lab (เช่น เงินไม่พอ, PIN ผิด)
#    และทำการ Raise Exception เมื่อเกิดข้อผิดพลาด
#################################ดยไม่เกิด Error
# 3. ห้ามแก้ไข Code ในส่วนของ create_bank_system() และ run_test() โดยเด็ดขาด
# 4. ต้องมีการ Validate ข้อมูลตามเงื่อนไขที่กำห#################################################

# --- พื้นที่สำหรับเขียน Class ของนักศึกษา (เขียนต่อจากตรงนี้) ---

class Bank:
    yearly_fee = 150

    def __init__(self, name) -> None:
        self.__name = name
        self.__user_list = []
        self.__atm_machine_list : List[ATM_machine] = []
    
    def add_user(self, user: User):
        self.__user_list.append(user)

    def add_atm_machine(self, atm_machine: ATM_machine):
        self.__atm_machine_list.append(atm_machine)
    
    def get_atm_by_id(self, id: str):
        for atm in self.__atm_machine_list:
            if atm.get_id() == id:
                return atm
        raise ValueError
    
    def search_account_from_atm(self, id_card: str):
        for user in self.__user_list:
            account = user.find_account_form_atm(id_card)
            if account != None:
                return account
        raise ValueError
    
    def yearly_Fee(self):
        for user in self.__user_list:
            account_list = user.get_account()
            for account in account_list:
                account.yearlyFee(Bank.yearly_fee)

    def reset_daily_limit(self):
        for user in self.__user_list:
            account_list = user.get_account()
            for account in account_list:
                account.reset_daily_limit()
                
class User:
    def __init__(self, id: str, name: str) -> None:
        self.__id = id
        self.__name = name
        self.__account_list : List[Account] = []

    def add_account(self, account : Account):
        self.__account_list.append(account)
    
    def get_account(self):
        return self.__account_list
    
    def find_account_form_atm(self, id_card: str):
        for account in self.__account_list:
            if id_card == account.atm_card.get_id():
                return account
        return None

class Account:
    daily_limit = 40000

    def __init__(self, acc_no: str, user: User, amount : int) -> None:
        self.__account_id = acc_no
        self.__user = user
        self.__balance = amount
        self.__atm_card = None
        self.__transaction_list: List[Transaction] = []
        self.__daily_limit = Account.daily_limit
    
    def add_atm_card(self, atm_card : ATM_Card):
        if self.__atm_card != None: raise ValueError
        self.__atm_card = atm_card

    def deposit(self, atm: ATM_machine, amount: int):
        if atm.get_activate() == None: raise ValueError("No Card Detected")
        if atm.get_activate() != self.__account_id: raise ValueError("Wrong Account/ ATM")
        if amount <= 0 : raise ValueError("amount should not be negative")
        self.__balance += amount
        transaction = Transaction('D', atm, amount, self.__balance)
        self.__transaction_list.append(transaction)


    def withdraw(self, atm: ATM_machine, amount: int):
        if atm.get_activate() == None: raise ValueError("No Card Detected")
        if atm.get_activate() != self.__account_id: raise ValueError("Wrong Account/ ATM")
        if amount <= 0 : raise ValueError("amount should not be negative")
        if self.__balance - amount <= 0 : raise ValueError("account amount is not enough")
        if self.__daily_limit - amount <= 0 : raise ValueError("Exceded Daily limit")
        if not atm.enough(amount): raise ValueError("atm money is not enough")
        self.__balance -= amount
        self.__daily_limit -= amount
        transaction = Transaction('W', atm, amount, self.__balance)
        self.__transaction_list.append(transaction)


    def transfer(self, atm: ATM_machine, amount: int, to: Account):
        if atm.get_activate() == None: raise ValueError("No Card Detected")
        if atm.get_activate() != self.__account_id: raise ValueError("Wrong Account/ ATM")
        if amount <= 0 : raise ValueError("amount should not be negative")
        if self.__balance - amount <= 0 : raise ValueError("account amount is not enough")
        if self.__daily_limit - amount <= 0 : raise ValueError("Exceded Daily limit")
        if not atm.enough(amount): raise ValueError("atm money is not enough")
        self.__balance -= amount
        self.__daily_limit -= amount
        to.__balance += amount
        transactionW = Transaction('TW', atm, amount, self.__balance, to.__account_id)
        transactionD = Transaction('TD', atm, amount, self.__balance, self.__account_id)
        self.__transaction_list.append(transactionW)
        to.__transaction_list.append(transactionD)
    
    def yearlyFee(self, amount):
        if self.__balance - amount >= 0: self.__balance -= amount

    def print_transactions(self):
        for transaction in self.__transaction_list:
            transaction.print_transactions()
    
    def reset_daily_limit(self):
        self.__daily_limit = Account.daily_limit

    @property
    def atm_card(self):
        if self.__atm_card == None: raise ValueError
        return self.__atm_card
    
    @property
    def account_no(self):
        return self.__account_id
    
    @property
    def amount(self):
        return self.__balance
    

class ATM_Card:
    def __init__(self, id: str, account_no: str, pin: str) -> None:
        self.__id = id
        self.__account_no = account_no
        self.__pin = pin

    def check_pin(self, pin):
        if pin == self.__pin: return True
        return False
    
    def get_account_no(self):
        return self.__account_no

    def get_id(self):
        return self.__id

class ATM_machine:
    def __init__(self, id: str, amount: int) -> None:
        self.__id = id
        self.__amount = amount
        self.__activate = None

    def enough(self, amount):
        if self.__amount - amount < 0: return False
        return True

    def insert_card(self, card: ATM_Card, pin: str):
        if not card.check_pin(pin): return False
        self.__activate = card.get_account_no()
        return True

    def get_id(self):
        return self.__id
    
    def get_activate(self):
        return self.__activate

class Transaction:
    def __init__(self, type, atm: ATM_machine, amount: int, bal_after: int, account = None) -> None:
        self.__type = type
        self.__atm = atm
        self.__amount = amount
        self.__bal_after = bal_after
        self.__to_account = account

    def print_transactions(self):
        print(f'Type : {self.__type} | at Atm(id) : {self.__atm.get_id()} | amount = {self.__amount} | bal_afer = {self.__bal_after} | form/to account(no) : {self.__to_account}')


##################################################################################
# Test Case & Setup : ห้ามแก้ไข Code ส่วนนี้
# ใช้สำหรับตรวจสอบว่า Class ที่ออกแบบมาถูกต้องตาม Requirement หรือไม่
##################################################################################

def create_bank_system() -> Bank:
    print("--- Setting up Bank System ---")
    
    # 1. กำหนดชื่อธนาคาร
    scb = Bank("SCB")
    
    # 2. สร้าง User, Account, ATM_Card
    # Data format: CitizenID: [Name, AccountNo, ATM Card No, Balance]
    user_data = {
       '1-1101-12345-12-0': ['Harry Potter', '1000000001', '12345', 20000],
       '1-1101-12345-13-0': ['Hermione Jean Granger', '1000000002', '12346', 1000]
    }
    
    for citizen_id, detail in user_data.items():
        name, account_no, atm_no, amount = detail
        
        user_instance = User(citizen_id, name)
        user_account = Account(account_no, user_instance, amount)
        atm_card = ATM_Card(atm_no, account_no, '1234')
        
        user_account.add_atm_card(atm_card)
        user_instance.add_account(user_account)
        scb.add_user(user_instance)

    # 3. สร้างตู้ ATM
    scb.add_atm_machine(ATM_machine('1001', 1000000))
    scb.add_atm_machine(ATM_machine('1002', 200000))

    return scb

def run_test():
    scb = create_bank_system()
    
    atm_machine1 = scb.get_atm_by_id('1001')
    atm_machine2 = scb.get_atm_by_id('1002')
    
    harry_account = scb.search_account_from_atm('12345')
    hermione_account = scb.search_account_from_atm('12346')
    
    # ตรวจสอบว่าหา Account เจอหรือไม่
    if not harry_account or not hermione_account:
        print("Error: Could not find accounts. Check your search_account_from_atm method.")
        return

    harry_card = harry_account.atm_card
    hermiony_card = hermione_account.atm_card
    
    print("\n--- Test Case #1 : Insert Card (Harry) ---")
    print(f"Harry's Account No : {harry_account.account_no}")

    if atm_machine2.insert_card(hermiony_card, "1234"):
        print("Success: ATM accepted valid card and PIN")
    else:
        print("Error: ATM rejected valid card")

    print("\n--- Test Case #2 : Deposit 1000 to Hermione ---")
    print(f"Before: {hermione_account.amount}")

    try:
        hermione_account.deposit(atm_machine2, 1000)
        print(f"After: {hermione_account.amount}")
    except Exception as e:
        print(f"Error: {e}")

    print("\n--- Test Case #3 : Deposit -1 (Expect Error) ---")
    try:
        hermione_account.deposit(atm_machine2, -1)
        print("Error: Failed to catch negative deposit")
    except ValueError as e: # คาดหวัง ValueError หรือ Exception ที่เหมาะสม
        print(f"Pass: System correctly raised error -> {e}")
    except Exception as e:
        print(f"Pass: System raised error -> {e}")

    print("\n--- Test Case #4 : Withdraw 500 from Hermione ---")
    print(f"Before: {hermione_account.amount}")

    try:
        hermione_account.withdraw(None, 500)
        print(f"After: {hermione_account.amount}")
    except Exception as e:
        print(f"Error: {e}")

    print("\n--- Test Case #5 : Withdraw Excess Balance (Expect Error) ---")
    try:
        hermione_account.withdraw(atm_machine2, 30000)
        print("Error: Failed to catch overdraft")
    except Exception as e:
        print(f"Pass: System correctly raised error -> {e}")

    print("\n--- Test Case #6 : Transfer 10000 from Harry to Hermione ---")
    print(f"Harry Before: {harry_account.amount}")
    print(f"Hermione Before: {hermione_account.amount}")

    try:
        harry_account.transfer(atm_machine2, 10000, hermione_account)
        print(f"Harry After: {harry_account.amount}")
        print(f"Hermione After: {hermione_account.amount}")
    except Exception as e:
        print(f"Error: {e}")

    print("\n--- Test Case #7 : Transaction History ---")

    print("Harry Transactions:")
    harry_account.print_transactions()
    print("Hermione Transactions:")
    hermione_account.print_transactions()

    print("\n--- Test Case #8 : Wrong PIN (Expect Error) ---")
    if not atm_machine1.insert_card(harry_card, "1234"):
        print("Pass: ATM correctly rejected wrong PIN")
    else:
        print("Error: ATM accepted wrong PIN")
        
    print("\n--- Test Case #9 : Exceed Daily Limit (Expect Error) ---")
    # Harry ถอนไปแล้ว 0, โอน 10000 (นับรวม) = ใช้ไป 10000
    # Limit = 40000. ลองถอนอีก 35000 (รวมเป็น 45000) ต้อง Error
    try:
        print("Attempting to withdraw 35,000 (Total daily: 45,000)...")
        harry_account.withdraw(atm_machine1, 35000)
        print("Error: Daily limit exceeded but not caught")
    except Exception as e:
        print(f"Pass: System correctly raised error -> {e}")

    print("\n--- Test Case #10 : ATM Insufficient Cash (Expect Error) ---")
 
    poor_atm = ATM_machine('9999', 100) 
    scb.add_atm_machine(poor_atm)
    try:
        print("Attempting to withdraw 500 from ATM with 100 THB...")
        harry_account.withdraw(poor_atm, 500)
        print("Error: ATM insufficient cash but not caught")
    except Exception as e:
        print(f"Pass: System correctly raised error -> {e}")

if __name__ == "__main__":
    run_test()