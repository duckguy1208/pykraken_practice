import pykraken as kn
import random

# Initialize Kraken
kn.init()
kn.window.create("Rust Runner MVP", 1280, 720)

# Physics Setup
world = kn.physics.World(kn.Vec2(0, 9.81 * 100)) # Gravity down
kn.physics.set_fixed_delta(1.0 / 60.0)

class Vehicle:
    def __init__(self, world, pos):
        self.world = world
        
        # Chassis
        self.chassis = kn.physics.RigidBody(world)
        self.chassis.pos = pos
        self.chassis.add_collider(kn.Rect(-60, -20, 120, 40), density=1.0, friction=0.5)
        
        # Wheels
        self.wheel_back = kn.physics.RigidBody(world)
        self.wheel_back.pos = pos + kn.Vec2(-40, 30)
        self.wheel_back.add_collider(kn.Circle(0, 0, 25), density=1.5, friction=0.9, restitution=0.2)
        
        self.wheel_front = kn.physics.RigidBody(world)
        self.wheel_front.pos = pos + kn.Vec2(40, 30)
        self.wheel_front.add_collider(kn.Circle(0, 0, 25), density=1.5, friction=0.9, restitution=0.2)
        
        # Joints (Suspension)
        axis = kn.Vec2(0, 1)
        self.joint_back = world.create_wheel_joint(self.chassis, self.wheel_back, self.wheel_back.pos, axis)
        self.joint_front = world.create_wheel_joint(self.chassis, self.wheel_front, self.wheel_front.pos, axis)
        
        # Setup Suspension properties
        for joint in [self.joint_back, self.joint_front]:
            joint.spring_enabled = True
            joint.spring_hz = 4.0
            joint.spring_damping_ratio = 0.7
            
        # Motor properties
        self.max_torque = 10000.0
        self.target_speed = 0.0
        
        # Decay State
        self.engine_health = 1.0 # 0.0 to 1.0
        self.wheel_health = 1.0
        
    def update(self, dt):
        # Apply Decay
        self.engine_health -= 0.01 * dt # Decays over 100 seconds
        self.wheel_health -= 0.005 * dt
        
        # Input handling
        self.target_speed = 0.0
        if kn.key.is_pressed(kn.key.S_d):
            self.target_speed = 30.0 * self.engine_health
        elif kn.key.is_pressed(kn.key.S_a):
            self.target_speed = -15.0 * self.engine_health
            
        # Apply Motor
        self.joint_back.motor_enabled = True
        self.joint_back.motor_speed = self.target_speed
        self.joint_back.max_motor_torque = self.max_torque * self.engine_health
        
        # Chassis Balance (leaning)
        if kn.key.is_pressed(kn.key.S_q):
            self.chassis.apply_torque(-500000.0 * self.engine_health)
        if kn.key.is_pressed(kn.key.S_e):
            self.chassis.apply_torque(500000.0 * self.engine_health)

    def draw(self):
        # Debug draw physics shapes
        self.chassis.debug_draw()
        self.wheel_back.debug_draw()
        self.wheel_front.debug_draw()
        
        # Draw HUD for health
        kn.draw.text(f"Engine: {self.engine_health*100:.1f}%", kn.Vec2(20, 20), kn.Color.WHITE)
        kn.draw.text(f"Tires: {self.wheel_health*100:.1f}%", kn.Vec2(20, 50), kn.Color.WHITE)

# Environment
ground = kn.physics.StaticBody(world)
ground.pos = kn.Vec2(0, 600)
# Create a long bumpy floor
points = [kn.Vec2(i * 100, random.uniform(-20, 20)) for i in range(50)]
# Simple flat ground for now to ensure MVP works
ground.add_collider(kn.Rect(0, 0, 5000, 100), friction=1.0)

car = Vehicle(world, kn.Vec2(200, 400))
camera = kn.Camera()

while kn.window.is_open():
    kn.event.poll()
    dt = kn.time.get_delta()
    
    # Update
    car.update(dt)
    
    # Camera follow
    camera.pos = car.chassis.pos - kn.Vec2(640, 360)
    
    # Render
    kn.renderer.clear(kn.Color("#1a1a1a"))
    
    with kn.renderer.use_camera(camera):
        ground.debug_draw()
        car.draw()
        
    kn.renderer.present()

kn.quit()
