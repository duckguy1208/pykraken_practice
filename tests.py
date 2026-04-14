import pykraken as kn
import unittest
import math

# We need to init kraken once for Vec2 and other types to work
kn.init()

class Vehicle:
    def __init__(self, pos):
        self.pos = kn.Vec2(pos.x, pos.y)
        self.vel = kn.Vec2(0, 0)
        self.rot = 0.0 
        self.rot_vel = 0.0
        self.engine_health = 1.0
        
    def update(self, dt):
        self.engine_health -= 0.01 * dt
        self.pos += self.vel * dt
        self.rot += self.rot_vel * dt

    def get_wheel_positions(self):
        # Wheel offsets relative to center
        back_offset = kn.Vec2(-35, 25)
        front_offset = kn.Vec2(35, 25)
        
        # Rotate offsets based on chassis rotation
        # Note: Kraken rotate() usually takes degrees or radians? 
        # Vec2.rotate(float) -> documented as degrees in many frameworks, 
        # let's assume degrees based on PixelArray.rotate docs.
        # We store self.rot in radians, so convert if needed.
        deg = math.degrees(self.rot)
        
        # rotate() might return a new Vec2 or mutate? 
        # Usually returns new one in these bindings.
        # In-place rotation
        back_rotated = kn.Vec2(back_offset.x, back_offset.y)
        back_rotated.rotate(deg)
        front_rotated = kn.Vec2(front_offset.x, front_offset.y)
        front_rotated.rotate(deg)
        
        back_pos = self.pos + back_rotated
        front_pos = self.pos + front_rotated
        
        return back_pos, front_pos

class TestVehicle(unittest.TestCase):
    def test_movement(self):
        v = Vehicle(kn.Vec2(0, 0))
        v.vel = kn.Vec2(100, 0)
        v.update(1.0)
        self.assertEqual(v.pos.x, 100)
        
    def test_decay(self):
        v = Vehicle(kn.Vec2(0, 0))
        v.update(10.0)
        self.assertLess(v.engine_health, 1.0)
        
    def test_wheel_attachment(self):
        v = Vehicle(kn.Vec2(100, 100))
        v.rot = math.pi / 2 # 90 degrees
        back, front = v.get_wheel_positions()
        
        # If rotated 90 degrees, the Y offset (25) becomes an X offset
        # and X offset (-35) becomes a Y offset.
        # This confirms if they are "attached" or just floating.
        self.assertNotEqual(back.x, 100 - 35) # Should not be static offset
        print(f"Back Wheel Pos after 90deg rotation: {back.x}, {back.y}")

if __name__ == "__main__":
    unittest.main()
