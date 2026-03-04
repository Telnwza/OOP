from abc import abstractmethod, ABC

class Device(ABC):
  def __init__(self, name) -> None:
    self.__name = name

  @property
  def name(self): return self.__name

  @abstractmethod
  def activete(self):
    pass

class Light(Device):
  def __init__(self, name, brightness, tone) -> None:
    super().__init__(name)
    self.__brightness = brightness
    self.__tone = tone

  def activete(self):
    print(f"Turning On Light: {self.name} ,tone : {self.__tone} ,At Brightness : {self.__brightness}")

class AirCondition(Device):
  def __init__(self, name, temp, fan_speed) -> None:
    super().__init__(name)
    self.__temp = temp
    self.__fan_speed = fan_speed

  def activete(self):
    print(f"Turing on AirCondution: {self.name}, Temp: {self.__temp}, At FanSpeed: {self.__fan_speed}")

class Speaker(Device):
  def __init__(self, name) -> None:
    super().__init__(name)
  
  def activete(self):
    print(f"Activating Speaker: {self.name}")

class Group(ABC):
  def __init__(self, name) -> None:
    self.__name = name
    self.__device: list[Device] = []

  @property
  def name(self): return self.__name

  def add_device(self, device: Device):
    self.__device.append(device)

  def activate_all(self):
    for device in self.__device:
      device.activete()

class Room(Group):
  def __init__(self, name) -> None:
    super().__init__(name)

class Scene(Group):
  def __init__(self, name) -> None:
    super().__init__(name)
   
class Home:
  def __init__(self) -> None:
    self.__device: list[Device] = []
    self.__room: list[Room] = []
    self.__scene: list[Scene] = []
  
  def add_device(self, device: Device):
    self.__device.append(device)

  def add_scene(self, scene: Scene):
    self.__scene.append(scene)

  def add_room(self, room: Room):
    self.__room.append(room)

  def activate_device_by_name(self, name):
    for device in self.__device:
      if device.name == name:
        device.activete()
        return
    print(f"Can't finde device name: {name}")

  def activete_room_by_name(self, room_name):
    for room in self.__room:
      if room.name == room_name:
        print(f"activate room: {room.name}")
        room.activate_all()
        return
    print(f"can't find room name: {room_name}")

  


