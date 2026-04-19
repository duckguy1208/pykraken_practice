import pykraken as kn
import random
import math

# Initialize Kraken
kn.init()
# Using scaled=True can sometimes help with high-DPI displays
kn.window.create("Wither's Wake", kn.Vec2(1280, 720), True)

# Load fonts - Reduced sizes slightly
font_small = kn.Font("kraken-clean", 18)
font_medium = kn.Font("kraken-clean", 24)
font_large = kn.Font("kraken-clean", 48)

class GameState:
    MENU = 0
    PLAYING = 1
    WON = 2
    LOST = 3

class Platform:
    def __init__(self, rect, is_stable=True):
        self.rect = rect
        self.is_stable = is_stable
        self.life = 5.0
        self.max_life = 5.0
        self.is_dead = False

    def update(self, dt):
        if not self.is_stable:
            self.life -= dt
            if self.life <= 0:
                self.is_dead = True

    def draw(self):
        color = kn.Color(100, 100, 100)
        if not self.is_stable:
            alpha = int((self.life / self.max_life) * 255)
            color = kn.Color(50, 255, 50, alpha)
        kn.draw.rect(self.rect, color)

class Player:
    def __init__(self, pos):
        self.pos = kn.Vec2(pos.x, pos.y)
        self.vel = kn.Vec2(0, 0)
        self.rect = kn.Rect(self.pos, kn.Vec2(40, 60))
        self.on_ground = False
        self.essence = 1.0
        
        self.speed = 400.0
        self.jump_force = -600.0
        self.gravity = 1500.0

    def update(self, dt, platforms):
        move_dir = 0
        if kn.key.is_pressed(kn.Scancode.S_a): move_dir -= 1
        if kn.key.is_pressed(kn.Scancode.S_d): move_dir += 1
        self.vel.x = move_dir * self.speed
        
        self.vel.y += self.gravity * dt
        self.essence -= 0.02 * dt # Constant decay
        self.essence = max(0.0, self.essence)
        self.pos.x += self.vel.x * dt
        self.sync_rect()
        
        for p in platforms:
            if self.rect.collide_rect(p.rect):
                if self.vel.x > 0: self.pos.x = p.rect.x - self.rect.w
                elif self.vel.x < 0: self.pos.x = p.rect.x + p.rect.w
                self.vel.x = 0
                self.sync_rect()

        self.pos.y += self.vel.y * dt
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
                elif self.vel.y < 0:
                    self.pos.y = p.rect.y + p.rect.h
                    self.vel.y = 0
                self.sync_rect()

        if self.on_ground and kn.key.is_pressed(kn.Scancode.S_SPACE):
            self.vel.y = self.jump_force
            self.on_ground = False

    def sync_rect(self):
        self.rect.x = self.pos.x
        self.rect.y = self.pos.y

    def draw(self):
        kn.draw.rect(self.rect, kn.color.WHITE)

# Game Logic
current_state = GameState.MENU
player = None
platforms = []
camera = kn.Camera()
default_camera = kn.Camera()
screen_res = kn.renderer.get_res()

def reset_game():
    global player, platforms, current_state
    player = Player(kn.Vec2(100, 500))
    platforms = [
        Platform(kn.Rect(kn.Vec2(0, 650), kn.Vec2(400, 50))),
        Platform(kn.Rect(kn.Vec2(1000, 500), kn.Vec2(200, 50))),
    ]
    current_state = GameState.PLAYING

while kn.window.is_open():
    kn.event.poll()
    dt = min(kn.time.get_delta(), 0.1) # Cap delta to prevent massive jumps
    mouse_pos = kn.mouse.get_pos()
    
    if current_state == GameState.MENU:
        if kn.key.is_just_pressed(kn.Scancode.S_SPACE):
            reset_game()
            
    elif current_state == GameState.PLAYING:
        if kn.mouse.is_just_pressed(kn.MouseButton.M_LEFT) and player.essence >= 0.2:
            world_mouse = mouse_pos + camera.pos
            platforms.append(Platform(kn.Rect(world_mouse - kn.Vec2(50, 10), kn.Vec2(100, 20)), False))
            player.essence -= 0.2
            
        player.update(dt, platforms)
        for p in platforms[:]:
            p.update(dt)
            if p.is_dead:
                platforms.remove(p)
                
        if player.pos.x > 1000 and player.on_ground:
            current_state = GameState.WON
        if player.pos.y > 1000:
            current_state = GameState.LOST
            
        camera.pos = player.pos - (screen_res / 2)
        
    elif current_state in [GameState.WON, GameState.LOST]:
        if kn.key.is_just_pressed(kn.Scancode.S_SPACE):
            current_state = GameState.MENU

    # Render
    kn.renderer.clear(kn.Color(20, 20, 25))
    
    if current_state == GameState.MENU:
        # Drawing a screen border to see usable area
        kn.draw.rect(kn.Rect(kn.Vec2(10, 10), screen_res - kn.Vec2(20, 20)), kn.Color(255, 255, 255, 50))
        
        font_large.draw("WITHER'S WAKE", kn.Vec2(screen_res.x * 0.35, screen_res.y * 0.3), kn.color.WHITE)
        font_small.draw("PRESS SPACE TO START", kn.Vec2(screen_res.x * 0.4, screen_res.y * 0.5), kn.color.WHITE)
        
    elif current_state == GameState.PLAYING:
        camera.set()
        for p in platforms:
            p.draw()
        player.draw()
        
        default_camera.set()
        font_small.draw(f"ESSENCE: {int(player.essence * 100)}%", kn.Vec2(20, 20), kn.color.GREEN)
        font_small.draw("L-CLICK: BLOOM PLATFORM", kn.Vec2(20, 50), kn.color.WHITE)

    elif current_state == GameState.WON:
        font_large.draw("THE BLOOM PREVAILS", kn.Vec2(screen_res.x * 0.3, screen_res.y * 0.3), kn.color.YELLOW)
        font_small.draw("PRESS SPACE FOR MENU", kn.Vec2(screen_res.x * 0.4, screen_res.y * 0.5), kn.color.WHITE)
        
    elif current_state == GameState.LOST:
        font_large.draw("WITHERED AWAY", kn.Vec2(screen_res.x * 0.35, screen_res.y * 0.3), kn.color.RED)
        font_small.draw("PRESS SPACE FOR MENU", kn.Vec2(screen_res.x * 0.4, screen_res.y * 0.5), kn.color.WHITE)
        
    kn.renderer.present()

kn.quit()
