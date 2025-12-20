class Wallet:
  def __init__(self, bal):
    if bal < 0 : return 'Error'
    self.__bal = bal
    return 'Done'
  
  def deposit(self, amount):
    if not amount.isnumeric() or float(amount) < 0: return 'Error'
    self.__bal += float(amount)
    return 'Done'
  
  def withdraw(self, amount):
    if not amount.isnumeric() or float(amount) < 0 or self.__bal - float(amount) < 0: return 'Error'
    self.__bal -= float(amount)
    return 'Done'
  
  def get_balance(self):
    return self.__bal
  