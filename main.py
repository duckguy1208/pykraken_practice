import pykraken as kn
import random
import math

# Initialize Kraken
kn.init()
# In 0.4.0, create() takes title: str, resolution: Vec2, scaled: bool
kn.window.create("Rust Runner", kn.Vec2(1280, 720))

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
        text_pos = kn.Vec2(self.rect.x + 20, self.rect.y + 15)
        kn.draw.text(self.text, text_pos, kn.Color.WHITE)

class Vehicle:
    def __init__(self, pos):
        self.pos = kn.Vec2(pos.x, pos.y)
        self.vel = kn.Vec2(0, 0)
        self.rot = 0.0 # Radians
        self.rot_vel = 0.0
        
        self.width = 100
        self.height = 40
        self.wheel_radius = 20
        
        self.engine_health = 1.0
        self.wheel_health = 1.0
        self.gravity = 800.0 # px/s^2
        self.ground_y = 600
        
    def update(self, dt, obstacles):
        # Decay
        self.engine_health -= 0.005 * dt
        self.wheel_health -= 0.002 * dt
        
        # Movement Input
        acceleration = 1200.0 * self.engine_health
        if kn.key.is_pressed(kn.Scancode.S_d):
            self.vel.x += acceleration * dt
        elif kn.key.is_pressed(kn.Scancode.S_a):
            self.vel.x -= (acceleration * 0.5) * dt
            
        # Air Balance / Rotation
        if kn.key.is_pressed(kn.Scancode.S_q):
            self.rot_vel -= 5.0 * dt * self.engine_health
        if kn.key.is_pressed(kn.Scancode.S_e):
            self.rot_vel += 5.0 * dt * self.engine_health
            
        # Apply Gravity
        self.vel.y += self.gravity * dt
        
        # Friction/Drag
        self.vel.x *= (1.0 - 0.5 * dt)
        self.rot_vel *= (1.0 - 1.0 * dt)
        
        # Integrate Position
        self.pos += self.vel * dt
        self.rot += self.rot_vel * dt
        
        # Simple Ground Collision
        car_bottom = self.pos.y + (self.height / 2) + self.wheel_radius
        if car_bottom > self.ground_y:
            self.pos.y = self.ground_y - (self.height / 2) - self.wheel_radius
            self.vel.y = 0
            # Friction on ground
            self.vel.x *= (1.0 - 2.0 * dt)
            # Alignment to ground (fake suspension feel)
            self.rot = kn.math.lerp(self.rot, 0.0, 5.0 * dt)
            self.rot_vel = kn.math.lerp(self.rot_vel, 0.0, 10.0 * dt)

        # Obstacle Collision (Simple AABB)
        car_rect = kn.Rect(self.pos.x - 50, self.pos.y - 20, 100, 40)
        for obs in obstacles:
            if kn.collision.overlap(car_rect, obs):
                # Simple bounce back
                self.vel.x = -self.vel.x * 0.5
                self.vel.y -= 200
                self.engine_health -= 0.05

    def draw(self):
        # Draw Chassis (Rotated)
        # Note: We simulate rotation by drawing a rectangle slightly offset
        # In a full game, we'd use sprites or a custom shader for rotation
        chassis_rect = kn.Rect(self.pos.x - 50, self.pos.y - 20, 100, 40)
        kn.draw.rect(chassis_rect, kn.Color("#7f8c8d"))
        
        # Draw Wheels
        back_wheel = kn.Circle(self.pos.x - 35, self.pos.y + 25, self.wheel_radius)
        front_wheel = kn.Circle(self.pos.x + 35, self.pos.y + 25, self.wheel_radius)
        kn.draw.circle(back_wheel, kn.Color("#2c3e50"))
        kn.draw.circle(front_wheel, kn.Color("#2c3e50"))

# Game State Variables
current_state = GameState.MENU
car = None
obstacles = []
camera = kn.Camera()
win_distance = 6000
ground_y = 600

# UI Buttons
start_button = Button(kn.Rect(540, 300, 200, 60), "START GAME", kn.Color("#2c3e50"), kn.Color("#34495e"))
restart_button = Button(kn.Rect(540, 400, 200, 60), "RESTART", kn.Color("#27ae60"), kn.Color("#2ecc71"))
menu_button = Button(kn.Rect(540, 480, 200, 60), "MAIN MENU", kn.Color("#7f8c8d"), kn.Color("#95a5a6"))

def reset_game():
    global car, obstacles, current_state
    car = Vehicle(kn.Vec2(200, 400))
    obstacles = []
    # Generate some obstacles along the road
    for i in range(10):
        obs_x = 1000 + i * 500 + random.uniform(-100, 100)
        obstacles.append(kn.Rect(obs_x, ground_y - 40, 40, 40))
    current_state = GameState.PLAYING

while kn.window.is_open():
    kn.event.poll()
    dt = kn.time.get_delta()
    mouse_pos = kn.mouse.get_pos()
    
    if current_state == GameState.MENU:
        if start_button.update(mouse_pos):
            reset_game()
            
    elif current_state == GameState.PLAYING:
        car.update(dt, obstacles)
        
        # Win Condition
        if car.pos.x > win_distance:
            current_state = GameState.WON
            
        # Lose Conditions
        if car.engine_health <= 0 or car.wheel_health <= 0 or abs(car.rot) > 2.0:
            current_state = GameState.LOST
            
        camera.pos = car.pos - kn.Vec2(640, 450)
        
    elif current_state in [GameState.WON, GameState.LOST]:
        if restart_button.update(mouse_pos):
            reset_game()
        if menu_button.update(mouse_pos):
            current_state = GameState.MENU

    # Rendering
    kn.renderer.clear(kn.Color("#1a1a1a"))
    
    if current_state == GameState.MENU:
        kn.draw.text("RUST RUNNER", kn.Vec2(530, 200), kn.Color.WHITE)
        start_button.draw()
        
    elif current_state == GameState.PLAYING:
        with kn.renderer.use_camera(camera):
            # Ground
            kn.draw.rect(kn.Rect(-1000, ground_y, win_distance + 3000, 200), kn.Color("#3d2b1f"))
            # Finish Line
            kn.draw.rect(kn.Rect(win_distance, 0, 20, 1000), kn.Color("#f1c40f"))
            
            # Obstacles
            for obs in obstacles:
                kn.draw.rect(obs, kn.Color("#e67e22"))
            
            car.draw()
        
        # HUD
        kn.draw.text(f"Engine: {max(0, car.engine_health*100):.1f}%", kn.Vec2(20, 20), kn.Color.WHITE)
        kn.draw.text(f"Tires: {max(0, car.wheel_health*100):.1f}%", kn.Vec2(20, 50), kn.Color.WHITE)
        kn.draw.text(f"Distance: {int(car.pos.x)} / {win_distance}", kn.Vec2(20, 80), kn.Color.WHITE)

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
