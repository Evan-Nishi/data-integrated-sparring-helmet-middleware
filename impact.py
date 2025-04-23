import json
import math

class impact:
    def __init__(self, x, y, z, gx, gy, gz):
        self.x = x
        self.y = y
        self.z = z
        self.gx = gx
        self.gy = gy
        self.gz = gz

        self.magnitude = (math.sqrt(self.x**2 + self.y**2 + self.z**2))

    def payload_obj(self):
        payload = {
            'x': self.x,
            'y': self.y,
            'z': self.z,
            'gx': self.gx,
            'gy': self.gy,
            'gz': self.gz,
        }
        return payload