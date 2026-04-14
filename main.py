import pykraken as kn
import random

# Initialize Kraken
kn.init()
kn.window.create("Rust Runner", 1280, 720)

# Physics Setup
kn.physics.set_fixed_delta(1.0 / 60.0)

class GameState:
    MENU = 0
    PLAYING = 1
    WON = 2
    LOST = 3

class Button:
    def __init__(self, rect, text, color, hover_color):
        self.rect = rect
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False

    def update(self, mouse_pos):
        self.is_hovered = kn.collision.overlap(mouse_pos, self.rect)
        return self.is_hovered and kn.mouse.is_just_pressed(kn.MouseButton.M_LEFT)

    def draw(self):
        color = self.hover_color if self.is_hovered else self.color
        kn.draw.rect(self.rect, color)
        # Center text in button (approximate)
        text_pos = kn.Vec2(self.rect.x + 20, self.rect.y + 15)
        kn.draw.text(self.text, text_pos, kn.Color.WHITE)

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
        
        for joint in [self.joint_back, self.joint_front]:
            joint.spring_enabled = True
            joint.spring_hz = 4.0
            joint.spring_damping_ratio = 0.7
            
        self.max_torque = 10000.0
        self.target_speed = 0.0
        self.engine_health = 1.0
        self.wheel_health = 1.0
        
    def update(self, dt):
        self.engine_health -= 0.005 * dt
        self.wheel_health -= 0.002 * dt
        
        self.target_speed = 0.0
        if kn.key.is_pressed(kn.Scancode.S_d):
            self.target_speed = 40.0 * self.engine_health
        elif kn.key.is_pressed(kn.Scancode.S_a):
            self.target_speed = -20.0 * self.engine_health
            
        self.joint_back.motor_enabled = True
        self.joint_back.motor_speed = self.target_speed
        self.joint_back.max_motor_torque = self.max_torque * self.engine_health
        
        if kn.key.is_pressed(kn.Scancode.S_q):
            self.chassis.apply_torque(-600000.0 * self.engine_health)
        if kn.key.is_pressed(kn.Scancode.S_e):
            self.chassis.apply_torque(600000.0 * self.engine_health)

    def draw(self):
        self.chassis.debug_draw()
        self.wheel_back.debug_draw()
        self.wheel_front.debug_draw()

# Game State Variables
current_state = GameState.MENU
world = None
car = None
ground = None
camera = kn.Camera()
win_distance = 4000

# UI Buttons
start_button = Button(kn.Rect(540, 300, 200, 60), "START GAME", kn.Color("#2c3e50"), kn.Color("#34495e"))
restart_button = Button(kn.Rect(540, 400, 200, 60), "RESTART", kn.Color("#27ae60"), kn.Color("#2ecc71"))
menu_button = Button(kn.Rect(540, 480, 200, 60), "MAIN MENU", kn.Color("#7f8c8d"), kn.Color("#95a5a6"))

def reset_game():
    global world, car, ground, current_state
    world = kn.physics.World(kn.Vec2(0, 9.81 * 100))
    ground = kn.physics.StaticBody(world)
    ground.pos = kn.Vec2(0, 600)
    ground.add_collider(kn.Rect(0, 0, win_distance + 1000, 100), friction=1.0)
    
    # Add some obstacles
    for i in range(5):
        obs = kn.physics.StaticBody(world)
        obs.pos = kn.Vec2(800 + i * 600, 580)
        obs.add_collider(kn.Rect(0, 0, 40, 40), friction=0.5)

    car = Vehicle(world, kn.Vec2(200, 400))
    current_state = GameState.PLAYING

while kn.window.is_open():
    kn.event.poll()
    dt = kn.time.get_delta()
    mouse_pos = kn.mouse.get_pos()
    
    if current_state == GameState.MENU:
        if start_button.update(mouse_pos):
            reset_game()
            
    elif current_state == GameState.PLAYING:
        car.update(dt)
        
        # Win Condition
        if car.chassis.pos.x > win_distance:
            current_state = GameState.WON
            
        # Lose Conditions
        if car.engine_health <= 0 or car.wheel_health <= 0 or abs(car.chassis.rotation) > 2.8:
            current_state = GameState.LOST
            
        camera.pos = car.chassis.pos - kn.Vec2(640, 360)
        
    elif current_state in [GameState.WON, GameState.LOST]:
        if restart_button.update(mouse_pos):
            reset_game()
        if menu_button.update(mouse_pos):
            current_state = GameState.MENU

    # Rendering
    kn.renderer.clear(kn.Color("#1a1a1a"))
    
    if current_state == GameState.MENU:
        kn.draw.text("RUST RUNNER", kn.Vec2(510, 200), kn.Color.WHITE)
        start_button.draw()
        
    elif current_state == GameState.PLAYING:
        with kn.renderer.use_camera(camera):
            ground.debug_draw()
            # Draw win line
            kn.draw.rect(kn.Rect(win_distance, 0, 10, 600), kn.Color("#f1c40f"))
            car.draw()
        
        # HUD
        kn.draw.text(f"Engine: {max(0, car.engine_health*100):.1f}%", kn.Vec2(20, 20), kn.Color.WHITE)
        kn.draw.text(f"Tires: {max(0, car.wheel_health*100):.1f}%", kn.Vec2(20, 50), kn.Color.WHITE)
        kn.draw.text(f"Distance: {int(car.chassis.pos.x)} / {win_distance}", kn.Vec2(20, 80), kn.Color.WHITE)

    elif current_state == GameState.WON:
        kn.draw.text("YOU SURVIVED!", kn.Vec2(540, 200), kn.Color("#f1c40f"))
        restart_button.draw()
        menu_button.draw()
        
    elif current_state == GameState.LOST:
        reason = "TOTAL DECAY" if car.engine_health <= 0 else "FLIPPED OVER"
        kn.draw.text(f"VEHICLE LOST: {reason}", kn.Vec2(480, 200), kn.Color("#e74c3c"))
        restart_button.draw()
        menu_button.draw()
        
    kn.renderer.present()

kn.quit()
