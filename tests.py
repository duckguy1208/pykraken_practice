import pykraken as kn
import unittest
import math

# We need to init kraken once for types to work
kn.init()

class Platform:
    def __init__(self, rect, is_stable=True):
        self.rect = rect
        self.is_stable = is_stable
        self.life = 5.0
        self.is_dead = False

    def update(self, dt):
        if not self.is_stable:
            self.life -= dt
            if self.life <= 0:
                self.is_dead = True

class Player:
    def __init__(self, pos):
        self.pos = kn.Vec2(pos.x, pos.y)
        self.vel = kn.Vec2(0, 0)
        self.rect = kn.Rect(self.pos, kn.Vec2(40, 60))
        self.on_ground = False
        self.essence = 1.0
        self.gravity = 1500.0

    def update(self, dt, platforms):
        self.essence -= 0.02 * dt
        self.vel.y += self.gravity * dt
        self.pos += self.vel * dt
        self.sync_rect()

        self.on_ground = False
        for p in platforms:
            if self.rect.collide_rect(p.rect):
                if self.vel.y > 0:
                    self.pos.y = p.rect.y - self.rect.h
                    self.vel.y = 0
                    self.on_ground = True
                    if p.is_stable:
                        self.essence = min(1.0, self.essence + 0.5 * dt)
                self.sync_rect()

    def sync_rect(self):
        self.rect.x = self.pos.x
        self.rect.y = self.pos.y

class TestWither(unittest.TestCase):
    def test_movement(self):
        p = Player(kn.Vec2(0, 0))
        p.vel = kn.Vec2(100, 0)
        p.update(0.1, [])
        self.assertAlmostEqual(p.pos.x, 10.0)

    def test_decay(self):
        p = Player(kn.Vec2(0, 0))
        initial_essence = p.essence
        p.update(1.0, [])
        self.assertLess(p.essence, initial_essence)

    def test_collision_and_recharge(self):
        p = Player(kn.Vec2(0, 500))
        p.essence = 0.5
        platforms = [Platform(kn.Rect(kn.Vec2(0, 550), kn.Vec2(100, 50)), True)]
        
        # Fall onto platform (smaller dt to ensure collision)
        p.update(0.1, platforms)
        self.assertTrue(p.on_ground)
        self.assertGreater(p.essence, 0.5)
        self.assertEqual(p.pos.y, 550 - 60)

    def test_temporary_platform(self):
        plat = Platform(kn.Rect(kn.Vec2(0, 0), kn.Vec2(10, 10)), False)
        plat.life = 0.1
        plat.update(0.2)
        self.assertTrue(plat.is_dead)

if __name__ == "__main__":
    unittest.main()
