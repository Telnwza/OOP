from abc import ABC, abstractmethod

class Charger(ABC):
  def __init__(self, id, power_kw:float) -> None:
    self.__id: str = id
    self.__power_kw: float = power_kw
    self.__is_avalible: bool = True

  def mark_not_avalible(self): self.__is_avalible = False
  def mark_avalible(self): self.__is_avalible = True

  @property
  def is_avalible(self): return self.__is_avalible
  
  @property
  def id(self): return self.__id

  @abstractmethod
  def start_charge(self):
    pass

  @abstractmethod
  def stop_charge(self):
    pass

class AC(Charger):
  def __init__(self, id, power_kw: float) -> None:
    super().__init__(id, power_kw)

  def start_charge(self):
    if self.is_avalible:
      print(f"Start Charging AC Charger ID: {self.id}, At Power: {self.__power_kw}")
      self.mark_not_avalible()
    else:
      print(f"Charger ID: {self.id} Is not Avalible")
  
  def stop_charge(self):
    if not self.is_avalible:
      print(f"Stop Charging AC Charger ID: {self.id}, At Power: {self.__power_kw}")
      self.mark_avalible()
    else:
      print(f"Charger ID: {self.id} Is Not charging")

class DC(Charger):
  def __init__(self, id, power_kw: float) -> None:
    super().__init__(id, power_kw)

  def start_charge(self):
    if self.is_avalible:
      print(f"Start Charging DC Charger ID: {self.id}, At Power: {self.__power_kw}")
      print("Liquid Cooling System Start!")
      self.mark_not_avalible()
    else:
      print(f"Charger ID: {self.id} Is not Avalible")
    
  def stop_charge(self):
    if not self.is_avalible:
      print(f"Stop Charging DC Charger ID: {self.id}, At Power: {self.__power_kw}")
      print("Liquid Cooling System Stop!")
      self.mark_avalible()
    else:
      print(f"Charger ID: {self.id} Is Not charging")

class Station:
  def __init__(self, name, location) -> None:
    self.__name = name
    self.__location = location
    self.__charger: list[Charger] = []
  
  @property
  def name(self): return self.__name
  
  def show_avalible_charger(self):
    avalible_list = []
    for charger in self.__charger:
      if charger.is_avalible:
        avalible_list.append(charger)
    if not len(avalible_list):
      print(f"Avalible Charger ID: {avalible_list}")
    else:
      print("No Avalible Charger Found")

class CentralManager:
  def __init__(self) -> None:
    self.__charger: list[Charger] = []
    self.__station: list[Station] = []

  def add_charger(self, charger: Charger):
    self.__charger.append(charger)
  
  def add_station(self, station: Station):
    self.__station.append(station)

  def avalible_charger_by_station(self, station_name):
    for station in self.__station:
      if station.name == station_name:
        station.show_avalible_charger()
        return
    print(f"Can't Find Station Name: {station_name}")

  def start_charger_by_id(self, charger_id):
    for charger in self.__charger:
      if charger.id == charger_id:
        charger.start_charge()
        return
    print(f"Can't Find Charger Id: {charger_id}")
  
  def stop_charger_by_id(self, charger_id):
    for charger in self.__charger:
      if charger.id == charger_id:
        charger.stop_charge()
        return
    print(f"Can't Find Charger Id: {charger_id}")
  