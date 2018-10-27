class Point():
    x:float = None
    y:float = None
    z:float = None
    def __init__(sefl, x:float, y:float, z:float):
        self.x = x
        self.y = y
        self.z = z

class Node(Point):
    def __init__(self, x:float, y:float, z:float):
        super().__init__(x,y,z)

class Drone(Point):
    load_max:float = None
    def __init__(self, x:float, y:float, z:float):
        super().__init__(x,y,z)

