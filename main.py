import pykraken as kn
import random
import math

# Initialize Kraken
kn.init()
kn.window.create("Rust Runner", kn.Vec2(1280, 720))

# Load fonts
font_small = kn.Font("kraken-clean", 20)
font_medium = kn.Font("kraken-clean", 32)
font_large = kn.Font("kraken-clean", 64)

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
        self.is_hovered = self.rect.collide_point(mouse_pos)
        return self.is_hovered and kn.mouse.is_just_pressed(kn.MouseButton.M_LEFT)

    def draw(self):
        draw_color = self.hover_color if self.is_hovered else self.color
        kn.draw.rect(self.rect, draw_color)
        text_pos = kn.Vec2(self.rect.x + 20, self.rect.y + 15)
        font_small.draw(self.text, text_pos, kn.color.WHITE)

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
        self.gravity = 800.0
        self.ground_y = 600
        
    def update(self, dt, obstacles):
        # Decay
        self.engine_health -= 0.005 * dt
        self.wheel_health -= 0.002 * dt
        
        # Movement
        acceleration = 1200.0 * self.engine_health
        if kn.key.is_pressed(kn.Scancode.S_d):
            self.vel.x += acceleration * dt
        elif kn.key.is_pressed(kn.Scancode.S_a):
            self.vel.x -= (acceleration * 0.5) * dt
            
        # Air Rotation
        if kn.key.is_pressed(kn.Scancode.S_q):
            self.rot_vel -= 5.0 * dt * self.engine_health
        if kn.key.is_pressed(kn.Scancode.S_e):
            self.rot_vel += 5.0 * dt * self.engine_health
            
        self.vel.y += self.gravity * dt
        self.vel.x *= (1.0 - 0.5 * dt)
        self.rot_vel *= (1.0 - 1.0 * dt)
        
        self.pos += self.vel * dt
        self.rot += self.rot_vel * dt
        
        # Collision
        car_bottom = self.pos.y + 45 # Approximate bottom including wheels
        if car_bottom > self.ground_y:
            self.pos.y = self.ground_y - 45
            self.vel.y = 0
            self.vel.x *= (1.0 - 2.0 * dt)
            # Match ground rotation (horizontal ground = 0 radians)
            self.rot = kn.math.lerp(self.rot, 0.0, 5.0 * dt)
            self.rot_vel = kn.math.lerp(self.rot_vel, 0.0, 10.0 * dt)

        car_rect = kn.Rect(kn.Vec2(self.pos.x - 50, self.pos.y - 20), kn.Vec2(100, 40))
        for obs in obstacles:
            if car_rect.collide_rect(obs):
                self.vel.x = -self.vel.x * 0.5
                self.vel.y -= 200
                self.engine_health -= 0.05

    def draw(self):
        deg = math.degrees(self.rot)
        
        # Calculate rotated chassis corners
        corners = [
            kn.Vec2(-50, -20), kn.Vec2(50, -20), 
            kn.Vec2(50, 20), kn.Vec2(-50, 20)
        ]
        rotated_corners = []
        for c in corners:
            rc = kn.Vec2(c.x, c.y)
            rc.rotate(deg)
            rotated_corners.append(self.pos + rc)
            
        # Draw Rotated Chassis
        chassis_color = kn.Color(127, 140, 141)
        # Flicker if engine is dying
        if self.engine_health < 0.3 and random.random() < 0.2:
            chassis_color = kn.color.RED
            
        kn.draw.polygon(rotated_corners, chassis_color)
        
        # Calculate rotated wheel positions
        back_off = kn.Vec2(-35, 25)
        front_off = kn.Vec2(35, 25)
        back_off.rotate(deg)
        front_off.rotate(deg)
        
        back_pos = self.pos + back_off
        front_pos = self.pos + front_off
        
        kn.draw.circle(kn.Circle(back_pos, self.wheel_radius), kn.color.BLACK)
        kn.draw.circle(kn.Circle(front_pos, self.wheel_radius), kn.color.BLACK)

# Game State Variables
current_state = GameState.MENU
car = None
obstacles = []
camera = kn.Camera()
default_camera = kn.Camera()
win_distance = 6000
ground_y = 600

# UI Buttons
start_button = Button(kn.Rect(kn.Vec2(540, 300), kn.Vec2(200, 60)), "START GAME", kn.Color(44, 62, 80), kn.Color(52, 73, 94))
restart_button = Button(kn.Rect(kn.Vec2(540, 400), kn.Vec2(200, 60)), "RESTART", kn.Color(39, 174, 96), kn.Color(46, 204, 113))
menu_button = Button(kn.Rect(kn.Vec2(540, 480), kn.Vec2(200, 60)), "MAIN MENU", kn.Color(127, 140, 141), kn.Color(149, 165, 166))

def reset_game():
    global car, obstacles, current_state
    car = Vehicle(kn.Vec2(200, 400))
    obstacles = []
    for i in range(10):
        obs_x = 1000 + i * 800 + random.uniform(-100, 100)
        obstacles.append(kn.Rect(kn.Vec2(obs_x, ground_y - 40), kn.Vec2(40, 40)))
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
        if car.pos.x > win_distance:
            current_state = GameState.WON
        if car.engine_health <= 0 or car.wheel_health <= 0 or abs(car.rot) > 2.0:
            current_state = GameState.LOST
        camera.pos = car.pos - kn.Vec2(640, 450)
        
    elif current_state in [GameState.WON, GameState.LOST]:
        if restart_button.update(mouse_pos):
            reset_game()
        if menu_button.update(mouse_pos):
            current_state = GameState.MENU

    # Rendering
    kn.renderer.clear(kn.Color(26, 26, 26))
    
    if current_state == GameState.MENU:
        font_large.draw("RUST RUNNER", kn.Vec2(480, 200), kn.color.WHITE)
        start_button.draw()
        
    elif current_state == GameState.PLAYING:
        camera.set()
        # Ground
        kn.draw.rect(kn.Rect(kn.Vec2(-1000, ground_y), kn.Vec2(win_distance + 3000, 200)), kn.Color(61, 43, 31))
        # Finish Line
        kn.draw.rect(kn.Rect(kn.Vec2(win_distance, 0), kn.Vec2(20, 1000)), kn.color.YELLOW)
        
        for obs in obstacles:
            kn.draw.rect(obs, kn.Color(230, 126, 34))
        
        car.draw()
        
        default_camera.set()
        # HUD
        font_small.draw(f"Engine: {max(0, car.engine_health*100):.1f}%", kn.Vec2(20, 20), kn.color.WHITE)
        font_small.draw(f"Tires: {max(0, car.wheel_health*100):.1f}%", kn.Vec2(20, 50), kn.color.WHITE)
        font_small.draw(f"Distance: {int(car.pos.x)} / {win_distance}", kn.Vec2(20, 80), kn.color.WHITE)

    elif current_state == GameState.WON:
        font_medium.draw("YOU SURVIVED!", kn.Vec2(540, 200), kn.color.YELLOW)
        restart_button.draw()
        menu_button.draw()
        
    elif current_state == GameState.LOST:
        reason = "TOTAL DECAY" if car.engine_health <= 0 else "FLIPPED OVER"
        font_medium.draw(f"VEHICLE LOST: {reason}", kn.Vec2(480, 200), kn.color.RED)
        restart_button.draw()
        menu_button.draw()
        
    kn.renderer.present()

kn.quit()
