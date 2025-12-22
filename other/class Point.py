class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    @classmethod
    def from_string(cls, s):
        x, y = s.split(",")
        return cls(int(x), int(y))
    
    def __repr__(self) -> str:
        return f'x = {self.x}, y = {self.y}'
    
p = Point.from_string("10,20")
print(p)