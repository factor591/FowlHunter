import pygame
import random
import math
from dataclasses import dataclass

# Initialize Pygame
pygame.init()

# Mobile-friendly window dimensions (portrait orientation)
WINDOW_WIDTH = 768
WINDOW_HEIGHT = 720
FPS = 60

# Color definitions
SKY_BLUE    = (135, 206, 235)   # Sky background color
GRASS_GREEN = (34, 139, 34)     # Ground color
DARK_GRASS  = (0, 100, 0)       # Dark green for grass blade outlines
TITLE_COLOR = (204, 85, 0)      # Dark orange for title

@dataclass
class DuckVariant:
    color: tuple
    wing_color: tuple
    bill_color: tuple
    points: int
    speed: float

DUCK_VARIANTS = {
    'normal': DuckVariant(
        color=(139, 69, 19),      # Brown
        wing_color=(101, 67, 33), # Dark brown
        bill_color=(255, 215, 0), # Gold
        points=100,
        speed=5.0
    ),
    'mallard': DuckVariant(
        color=(27, 79, 42),       # Dark green
        wing_color=(20, 61, 32),  # Darker green
        bill_color=(255, 215, 0), # Gold
        points=150,
        speed=6.0
    ),
    'golden': DuckVariant(
        color=(255, 215, 0),      # Gold
        wing_color=(218, 165, 32),# Dark gold
        bill_color=(255, 165, 0), # Orange
        points=300,
        speed=7.0
    ),
    'ruby': DuckVariant(
        color=(139, 0, 0),        # Dark red
        wing_color=(102, 0, 0),   # Darker red
        bill_color=(255, 215, 0), # Gold
        points=500,
        speed=8.0
    )
}

class TitleScreen:
    """Handles the game's title screen display and animation."""
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.timer = 0
        self.alpha = 0
        self.title_y = height * 0.3
        self.ducks = []  # List to hold multiple ducks
        self.environment = Environment(width, height)
        
        # Create pixelated looking text for DUCK and HUNTER separately
        small_font = pygame.font.Font(None, 32)
        duck_text = small_font.render("BIRD", False, TITLE_COLOR)
        hunter_text = small_font.render("HUNTER", False, TITLE_COLOR)
        
        # Scale up by 4x for pixelated look
        self.duck_surface = pygame.transform.scale(
            duck_text,
            (duck_text.get_width() * 4, duck_text.get_height() * 4)
        )
        self.hunter_surface = pygame.transform.scale(
            hunter_text,
            (hunter_text.get_width() * 4, hunter_text.get_height() * 4)
        )
        
        # Create pixelated "Click to Start" text
        start_text = small_font.render("Click to Start", False, (0, 0, 0))
        self.start_surface = pygame.transform.scale(
            start_text,
            (start_text.get_width() * 2, start_text.get_height() * 2)
        )
        
        # Initial duck spawning
        self.spawn_timer = 0
        self.spawn_duck()
        
    def spawn_duck(self):
        """Create a new duck for the title screen."""
        # Randomly choose starting position (top or sides)
        spawn_type = random.choice(['top', 'side'])
        if spawn_type == 'top':
            x = random.randint(0, self.width)
            y = -50
            duck = Duck('golden', (x, y))
            # Angle downward
            duck.speed_y = abs(duck.speed_y)
        else:
            # Choose left or right side
            x = -50 if random.random() < 0.5 else self.width + 50
            y = random.randint(100, int(self.height * 0.6))
            duck = Duck('golden', (x, y))
            # Ensure duck flies toward center
            duck.speed_x = abs(duck.speed_x) if x < 0 else -abs(duck.speed_x)
        
        self.ducks.append(duck)
        
    def update(self):
        """Update title screen elements."""
        self.timer += 1
        self.environment.update()
        
        # Fade in title
        if self.alpha < 255:
            self.alpha = min(255, self.alpha + 2)
            self.duck_surface.set_alpha(self.alpha)
            self.hunter_surface.set_alpha(self.alpha)
            self.start_surface.set_alpha(self.alpha)
            
        # Update duck spawning
        self.spawn_timer += 1
        if self.spawn_timer >= 120:  # Spawn new duck every 2 seconds
            self.spawn_timer = 0
            if len(self.ducks) < 5:  # Limit maximum ducks
                self.spawn_duck()
            
        # Update all ducks and remove those off screen
        for duck in self.ducks[:]:
            duck.update()
            # Remove if duck is far off screen
            if (duck.rect.right < -100 or 
                duck.rect.left > self.width + 100 or
                duck.rect.bottom < -100 or
                duck.rect.top > self.height + 100):
                self.ducks.remove(duck)
                
    def draw(self, screen):
        """Draw the title screen."""
        # Draw environment first
        self.environment.draw(screen)
        
        # Draw DUCK text
        duck_rect = self.duck_surface.get_rect(
            centerx=self.width // 2,
            y=self.title_y
        )
        screen.blit(self.duck_surface, duck_rect)
        
        # Draw HUNTER text below DUCK
        hunter_rect = self.hunter_surface.get_rect(
            centerx=self.width // 2,
            y=self.title_y + duck_rect.height + 20
        )
        screen.blit(self.hunter_surface, hunter_rect)
        
        # Draw all ducks
        for duck in self.ducks:
            screen.blit(duck.image, duck.rect)
            
        # Draw "Click to Start" text with pulsing effect
        pulse = abs(math.sin(self.timer * 0.05)) * 0.3 + 0.7
        alpha = int(255 * pulse)
        self.start_surface.set_alpha(alpha)
        start_rect = self.start_surface.get_rect(
            centerx=self.width // 2,
            y=self.height * 0.7
        )
        screen.blit(self.start_surface, start_rect)

class Feather(pygame.sprite.Sprite):
    """Simple falling feather effect when a duck is hit."""
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((6, 12), pygame.SRCALPHA)
        color = (
            random.randint(200, 255),
            random.randint(200, 255),
            random.randint(200, 255)
        )
        pygame.draw.line(self.image, color, (3, 0), (3, 12), 2)
        self.rect = self.image.get_rect(center=(x, y))
        self.x = float(x)
        self.y = float(y)
        self.speed_x = random.uniform(-1, 1)
        self.speed_y = random.uniform(-2, 0)
        self.rotation = 0
        self.rotation_speed = random.uniform(-1, 1)
        self.lifetime = random.randint(20, 40)

    def update(self):
        self.speed_y += 0.1
        self.x += self.speed_x
        self.y += self.speed_y
        self.rect.topleft = (round(self.x), round(self.y))
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.kill()

class Duck(pygame.sprite.Sprite):
    """A duck that can fly, be hit, then fall or escape via the top."""
    def __init__(self, variant_name='normal', start_pos=None):
        super().__init__()
        self.variant = DUCK_VARIANTS[variant_name]
        self.state = 'flying'
        self.frame = 0
        self.frames = self._create_animation_frames()
        # Pre-generate flipped versions of each animation frame
        self.frames_flipped = {}
        for state, frames in self.frames.items():
            self.frames_flipped[state] = [
                pygame.transform.flip(frame, True, False) for frame in frames
            ]

        self.image = self.frames['flying'][0]
        self.rect = self.image.get_rect()
        self.hit_timer = 0

        if start_pos:
            self.rect.x, self.rect.y = start_pos
        else:
            self.reset()

        # Random flight direction & speed
        direction = random.choice([-1, 1])
        angle = random.uniform(30, 60)
        speed = self.variant.speed
        rad = math.radians(angle)
        self.speed_x = speed * math.cos(rad) * direction
        self.speed_y = -speed * math.sin(rad) * 1.5

    def _create_animation_frames(self):
        """
        Build duck frames for flying, hit, and falling.
        The 'hit' frames are just the first flying frame reused.
        """
        frames = {'flying': [], 'hit': [], 'falling': []}
        
        base_surface = pygame.Surface((80, 60), pygame.SRCALPHA)
        
        def draw_base_duck(surface, wing_offset=0):
            # Body (oval)
            pygame.draw.ellipse(surface, self.variant.color, (20, 15, 40, 30))
            
            # Tail feathers (triangular)
            tail_points = [(15, 25), (25, 30), (15, 35)]
            pygame.draw.polygon(surface, self.variant.color, tail_points)
            
            # Wing
            wing_y = 20 + wing_offset
            wing_points = [
                (25, wing_y),
                (45, wing_y - 5),
                (45, wing_y + 10),
                (25, wing_y + 15)
            ]
            pygame.draw.polygon(surface, self.variant.wing_color, wing_points)
            
            # Head
            pygame.draw.ellipse(surface, self.variant.color, (50, 15, 20, 18))
            # Eye
            pygame.draw.circle(surface, (0,0,0), (63, 23), 2)
            pygame.draw.circle(surface, (255,255,255), (63, 22), 1)
            
            # Bill
            bill_points = [
                (67, 24), (77, 23), (77, 26), (67, 27)
            ]
            pygame.draw.polygon(surface, self.variant.bill_color, bill_points)
            
            # Bill detail line
            pygame.draw.line(
                surface,
                (max(0, self.variant.bill_color[0] - 40),
                 max(0, self.variant.bill_color[1] - 40),
                 max(0, self.variant.bill_color[2] - 40)),
                (67, 25), (77, 25), 1
            )
            
            # Body shading
            pygame.draw.ellipse(
                surface,
                (max(0, self.variant.color[0] - 30),
                 max(0, self.variant.color[1] - 30),
                 max(0, self.variant.color[2] - 30)),
                (25, 18, 30, 20), 1
            )
            
            # Feet in some frames
            if wing_offset >= 0:
                foot_color = self.variant.bill_color
                # Left foot
                pygame.draw.line(surface, foot_color, (30, 43), (35, 48), 2)
                pygame.draw.line(surface, foot_color, (35, 48), (38, 46), 2)
                pygame.draw.line(surface, foot_color, (35, 48), (32, 46), 2)
                # Right foot
                pygame.draw.line(surface, foot_color, (40, 43), (45, 48), 2)
                pygame.draw.line(surface, foot_color, (45, 48), (48, 46), 2)
                pygame.draw.line(surface, foot_color, (45, 48), (42, 46), 2)

        # Flying frames
        wing_positions = [0, -5, 0, 5]
        for wing_pos in wing_positions:
            frame = base_surface.copy()
            draw_base_duck(frame, wing_pos)
            frames['flying'].append(frame)
        
        # Hit frames: reuse the "flying" first frame with no flash
        for _ in range(4):
            hit_frame = frames['flying'][0].copy()
            frames['hit'].append(hit_frame)

        # Falling frames
        falling_base = base_surface.copy()
        draw_base_duck(falling_base, 5)
        for i in range(4):
            angle = i * 5
            frame = pygame.transform.rotate(falling_base, angle)
            frames['falling'].append(frame)
        
        return frames

    def reset(self):
        """Reset the duck to near the bottom, ready to fly."""
        self.rect.y = WINDOW_HEIGHT - 150
        self.rect.x = random.randint(-100, WINDOW_WIDTH // 2)
        self.state = 'flying'
        self.hit_timer = 0
        self.frame = 0

    def update(self):
        """Handle movement and state transitions for the duck."""
        if self.state == 'flying':
            self.frame = (self.frame + 1) % len(self.frames['flying'])
            self.image = (self.frames_flipped['flying'][self.frame]
                          if self.speed_x < 0
                          else self.frames['flying'][self.frame])
            self.rect.x += self.speed_x
            self.rect.y += self.speed_y

            if self.rect.left < 0:
                self.rect.left = 0
                self.speed_x = -self.speed_x
            if self.rect.right > WINDOW_WIDTH:
                self.rect.right = WINDOW_WIDTH
                self.speed_x = -self.speed_x

            if self.rect.bottom < 0:
                self.kill()
                return

            if self.rect.bottom > WINDOW_HEIGHT - 100:
                self.rect.bottom = WINDOW_HEIGHT - 100
                if self.speed_y > 0:
                    self.speed_y = -self.speed_y

        elif self.state == 'hit':
            self.frame = (self.frame + 1) % len(self.frames['hit'])
            self.image = (self.frames_flipped['hit'][self.frame]
                          if self.speed_x < 0
                          else self.frames['hit'][self.frame])
            self.hit_timer += 1
            if self.hit_timer >= 12:
                self.state = 'falling'
                self.frame = 0

        elif self.state == 'falling':
            self.frame = (self.frame + 1) % len(self.frames['falling'])
            self.image = (self.frames_flipped['falling'][self.frame]
                          if self.speed_x < 0
                          else self.frames['falling'][self.frame])
            self.rect.y += self.variant.speed * 2
            if self.rect.bottom >= WINDOW_HEIGHT - 100:
                self.kill()

class Explosion(pygame.sprite.Sprite):
    """A simple expanding circle explosion at the mouse click."""
    def __init__(self, pos):
        super().__init__()
        self.frames = []
        for i in range(6):
            surface = pygame.Surface((50, 50), pygame.SRCALPHA)
            radius = 5 + i * 5
            # Outer red
            pygame.draw.circle(surface, (255, 0, 0), (25, 25), radius)
            # Inner orange
            pygame.draw.circle(surface, (255, 165, 0), (25, 25), radius // 2)
            self.frames.append(surface)

        self.index = 0
        self.image = self.frames[self.index]
        self.rect = self.image.get_rect(center=pos)
        self.timer = 0

    def update(self):
        self.timer += 1
        # Advance frame every 5 ticks
        if self.timer % 5 == 0:
            self.index += 1
            if self.index >= len(self.frames):
                self.kill()
            else:
                self.image = self.frames[self.index]

class Dog(pygame.sprite.Sprite):
    """
    The dog sprite appears at the end of a round,
    facing the player with a duck in its mouth.
    It moves up so ~1/4 of it is behind the grass block.
    """
    def __init__(self, mood):
        super().__init__()
        self.mood = mood

        # Make the dog taller so bottom quarter can be hidden
        self.image = pygame.Surface((120, 120), pygame.SRCALPHA)
        self.draw_dog(self.image)
        self.rect = self.image.get_rect()
        self.rect.centerx = WINDOW_WIDTH // 2
        
        # Slide upward so ~1/4 is below the grass line (grass top ~700)
        self.target_y = 610
        self.speed_y = -5
        # Start fully off-screen
        self.rect.top = WINDOW_HEIGHT

    def draw_dog(self, surface):
        """
        Draw a front-facing dog with ears behind its head.
        """
        surface.fill((0, 0, 0, 0))  # Transparent

        # Colors
        fur_color    = (205, 133, 63)
        belly_color  = (222, 184, 135)
        ear_color    = (139, 69, 19)
        nose_color   = (40, 20, 0)
        eye_color    = (0, 0, 0)

        mouth_color  = (0, 160, 0) if self.mood == "happy" else (160, 0, 0)

        head_center = (60, 35)
        head_radius = 20

        # EARS (draw FIRST, so they appear behind head)
        left_ear_points = [
            (head_center[0] - 12, head_center[1] - 20),
            (head_center[0] - 20, head_center[1] - 5),
            (head_center[0] - 2,  head_center[1] - 8)
        ]
        right_ear_points = [
            (head_center[0] + 12, head_center[1] - 20),
            (head_center[0] + 20, head_center[1] - 5),
            (head_center[0] + 2,  head_center[1] - 8)
        ]
        pygame.draw.polygon(surface, ear_color, left_ear_points)
        pygame.draw.polygon(surface, ear_color, right_ear_points)

        # HEAD
        pygame.draw.circle(surface, fur_color, head_center, head_radius)

        # MUZZLE
        muzzle_rect = (head_center[0] - 10, head_center[1], 20, 14)
        pygame.draw.ellipse(surface, belly_color, muzzle_rect)

        # NOSE
        pygame.draw.ellipse(surface, nose_color, (head_center[0] - 4, head_center[1] + 5, 8, 5))

        # EYES
        left_eye_center  = (head_center[0] - 6, head_center[1] - 5)
        right_eye_center = (head_center[0] + 6, head_center[1] - 5)
        pygame.draw.circle(surface, eye_color, left_eye_center, 3)
        pygame.draw.circle(surface, eye_color, right_eye_center, 3)

        # MOUTH (arc)
        mouth_rect = pygame.Rect(head_center[0] - 6, head_center[1] + 8, 12, 8)
        if self.mood == "happy":
            pygame.draw.arc(surface, mouth_color, mouth_rect, 0, math.pi, 2)
        else:
            pygame.draw.arc(surface, mouth_color, mouth_rect, math.pi, 2*math.pi, 2)

        # DUCK (in dog's mouth)
        duck_body_color = (255, 215, 0)
        duck_wing_color = (218, 165, 32)
        duck_body_rect = pygame.Rect(head_center[0] - 15, head_center[1] + 12, 20, 10)
        pygame.draw.ellipse(surface, duck_body_color, duck_body_rect)
        duck_wing = [
            (duck_body_rect.left + 3, duck_body_rect.top + 3),
            (duck_body_rect.left + 12, duck_body_rect.top),
            (duck_body_rect.left + 12, duck_body_rect.top + 6),
        ]
        pygame.draw.polygon(surface, duck_wing_color, duck_wing)
        pygame.draw.polygon(surface, (255, 165, 0), [
            (duck_body_rect.right - 1, duck_body_rect.top + 3),
            (duck_body_rect.right + 4, duck_body_rect.top + 2),
            (duck_body_rect.right + 4, duck_body_rect.top + 6)
        ])

        # BODY (bigger, so dog is tall)
        pygame.draw.ellipse(surface, fur_color, (30, 60, 60, 35))
        pygame.draw.ellipse(surface, belly_color, (36, 68, 48, 20))

        # LEGS
        leg_width = 10
        leg_height = 15
        left_leg_rect = pygame.Rect(35, 80, leg_width, leg_height)
        right_leg_rect = pygame.Rect(75, 80, leg_width, leg_height)
        pygame.draw.rect(surface, fur_color, left_leg_rect)
        pygame.draw.rect(surface, fur_color, right_leg_rect)
        pygame.draw.ellipse(surface, fur_color, (33, 92, leg_width+4, 8))
        pygame.draw.ellipse(surface, fur_color, (73, 92, leg_width+4, 8))

    def update(self):
        """Slide upward until it reaches target_y."""
        if self.rect.top + self.speed_y > self.target_y:
            self.rect.top += self.speed_y
        else:
            self.rect.top = self.target_y

class Environment:
    """
    Handles background: sky, clouds, trees, and grass.
    Only the clouds move horizontally. 
    """
    def __init__(self, width, height):
        self.width = width
        self.height = height

        # Clouds and trees data
        self.clouds = []
        self.cloud_surfaces = []
        self.trees = []
        self.tree_foliage_arcs = {}

        self._initialize_environment()
        self._initialize_grass()

    def _initialize_environment(self):
        """Create random positions for clouds & trees, plus arcs for foliage."""
        # Create some clouds
        for _ in range(3):
            cx = random.randint(80, self.width - 80)
            cy = random.randint(50, 200)
            speed = random.uniform(0.5, 1.5)  # drift speed
            cloud_surf = self._create_cloud_surface()
            self.clouds.append({'x': cx, 'y': cy, 'speed': speed})
            self.cloud_surfaces.append(cloud_surf)

        # Place some trees
        tree_xs = []
        attempts = 0
        while len(tree_xs) < 3 and attempts < 1000:
            candidate = random.randint(50, self.width - 50)
            if all(abs(candidate - x) >= 150 for x in tree_xs):
                tree_xs.append(candidate)
            attempts += 1

        for i, x in enumerate(tree_xs):
            scale = random.uniform(0.8, 1.2)
            self.trees.append({'x': x, 'y': self.height - 100, 'scale': scale})
            arcs_for_tree = self._generate_tree_arcs(x, self.height - 100, scale)
            self.tree_foliage_arcs[i] = arcs_for_tree

    def _create_cloud_surface(self):
        """
        Return a single Surface with a 'Super Mario 3–style' cloud shape + arcs.
        """
        cloud_surface = pygame.Surface((120, 80), pygame.SRCALPHA)
        # Base circles
        pygame.draw.circle(cloud_surface, (255, 255, 255), (40, 40), 25)
        pygame.draw.circle(cloud_surface, (255, 255, 255), (70, 35), 20)
        pygame.draw.circle(cloud_surface, (255, 255, 255), (90, 45), 20)
        pygame.draw.circle(cloud_surface, (255, 255, 255), (60, 55), 25)

        # SM3-style arcs inside
        pygame.draw.arc(cloud_surface, (220, 220, 220), (20, 25, 40, 20), 0, math.pi/2, 2)
        pygame.draw.arc(cloud_surface, (220, 220, 220), (50, 30, 35, 15), math.pi/2, math.pi, 2)

        return cloud_surface

    def _generate_tree_arcs(self, tree_x, tree_y, scale):
        """
        Create arcs inside each foliage layer for that 'SMB3' style look.
        We'll store them as (cx, cy, w_arc, h_arc, start, end, color).
        """
        arcs = []
        trunk_height = int(60 * scale)
        foliage_base_y = tree_y - trunk_height
        layers = [(80, 50), (70, 45), (60, 40), (40, 35)]
        base_y = foliage_base_y

        for (w, h) in layers:
            w_scaled = int(w * scale)
            h_scaled = int(h * scale)
            left_x  = tree_x - (w_scaled // 2)
            right_x = tree_x + (w_scaled // 2)
            top_y   = base_y - h_scaled

            for _ in range(5):
                cx = random.randint(left_x, right_x)
                cy = random.randint(top_y, base_y)
                if self._point_in_triangle((cx, cy),
                                           (left_x, base_y),
                                           (right_x, base_y),
                                           (tree_x, top_y)):
                    w_arc = random.randint(10, 20)
                    h_arc = random.randint(5, 12)
                    start_angle = random.choice([0, math.pi/2, math.pi, 3*math.pi/2])
                    end_angle   = start_angle + math.pi/2
                    variation = random.randint(-20, 20)
                    base_color = (46, 139, 34)
                    arc_color = (
                        max(0, min(255, base_color[0] + variation)),
                        max(0, min(255, base_color[1] + variation)),
                        max(0, min(255, base_color[2] + variation))
                    )
                    arcs.append((cx, cy, w_arc, h_arc, start_angle, end_angle, arc_color))

            base_y -= int(h_scaled * 0.7)

        return arcs

    def _point_in_triangle(self, p, a, b, c):
        """Check if point p is inside the triangle formed by a,b,c."""
        (px, py) = p
        (ax, ay) = a
        (bx, by) = b
        (cx, cy) = c

        area_full = abs(ax*(by-cy) + bx*(cy-ay) + cx*(ay-by))
        area1 = abs(px*(by-cy) + bx*(cy-py) + cx*(py-by))
        area2 = abs(ax*(py-cy) + px*(cy-ay) + cx*(ay-py))
        area3 = abs(ax*(by-py) + bx*(py-ay) + px*(ay-by))

        return (area1 + area2 + area3) == area_full

    def _initialize_grass(self):
        """Prepare grass blades in three layers."""
        self.grass_timer = 0
        self.grass_rows = {
            'bottom': self.height - 20,
            'middle': self.height - 50,
            'top': self.height - 80
        }
        self.grass_layers = {}
        num_blades = 60
        for layer, y in self.grass_rows.items():
            blades = []
            for _ in range(num_blades):
                blade = {
                    "x": random.randint(0, self.width),
                    "height": random.randint(10, 20),
                    "offset": random.randint(-2, 2)
                }
                blades.append(blade)
            self.grass_layers[layer] = blades

    def update(self):
        """Move clouds horizontally. Slightly adjust grass blades for a simple sway."""
        for i, cloud in enumerate(self.clouds):
            cloud['x'] += cloud['speed']
            if cloud['x'] > self.width + 100:
                cloud['x'] = -100

        self.grass_timer += 1
        if self.grass_timer >= FPS / 2:
            self.grass_timer = 0
            for blades in self.grass_layers.values():
                for blade in blades:
                    blade["offset"] = random.randint(-2, 2)

    def draw(self, screen):
        """Draw sky, clouds, trees, and grass."""
        # Sky
        screen.fill(SKY_BLUE)

        # Clouds
        for i, cloud in enumerate(self.clouds):
            surf = self.cloud_surfaces[i]
            x_pos = cloud['x'] - surf.get_width() // 2
            y_pos = cloud['y'] - surf.get_height() // 2
            screen.blit(surf, (x_pos, y_pos))

        # Trees
        for i, tree in enumerate(self.trees):
            x = tree['x']
            y = tree['y']
            scale = tree['scale']
            self._draw_tree(screen, x, y, scale)

            # Draw arcs for each tree
            for (cx, cy, w_arc, h_arc, start, end, color) in self.tree_foliage_arcs[i]:
                arc_rect = pygame.Rect(cx - w_arc//2, cy - h_arc//2, w_arc, h_arc)
                pygame.draw.arc(screen, color, arc_rect, start, end, 2)

        # Ground
        pygame.draw.rect(screen, GRASS_GREEN, (0, self.height - 100, self.width, 100))

        # Grass blades
        for layer, blades in self.grass_layers.items():
            base_y = self.grass_rows[layer]
            for blade in blades:
                base_x = blade["x"]
                tip_x = base_x + blade["offset"]
                tip_y = base_y - blade["height"]
                pygame.draw.line(screen, DARK_GRASS, (base_x, base_y), (tip_x, tip_y), 2)

    def _draw_tree(self, screen, x, y, scale):
        """Draw trunk + stacked foliage triangles."""
        trunk_width = int(20 * scale)
        trunk_height = int(60 * scale)
        trunk_rect = pygame.Rect(x - trunk_width // 2, y - trunk_height, trunk_width, trunk_height)
        pygame.draw.rect(screen, (75, 54, 33), trunk_rect)

        foliage_color = (46, 139, 34)
        base_y = y - trunk_height
        layers = [(80, 50), (70, 45), (60, 40), (40, 35)]
        for (w, h) in layers:
            w_scaled = int(w * scale)
            h_scaled = int(h * scale)
            points = [
                (x - w_scaled // 2, base_y),
                (x + w_scaled // 2, base_y),
                (x, base_y - h_scaled)
            ]
            pygame.draw.polygon(screen, foliage_color, points)
            base_y -= int(h_scaled * 0.7)

class DuckHunt:
    """Main Duck Hunt game controller."""
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Duck Hunter")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 48)

        self.score = 0
        self.environment = Environment(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.ducks = pygame.sprite.Group()
        self.feathers = pygame.sprite.Group()
        self.explosions = pygame.sprite.Group()

        self.round = 1
        self.spawn_timer = 0
        self.game_state = 'title'  # Changed from 'start' to 'title'
        self.ducks_per_round = 3
        self.ducks_spawned = 0
        self.ducks_hit = 0
        self.flash_timer = 0

        # Initialize title screen
        self.title_screen = TitleScreen(WINDOW_WIDTH, WINDOW_HEIGHT)

        # The dog will appear at round end
        self.dog = None

    def spawn_duck(self):
        """Randomly choose a duck variant to spawn."""
        variant = random.choices(list(DUCK_VARIANTS.keys()),
                                 weights=[70, 20, 8, 2])[0]
        duck = Duck(variant)
        self.ducks.add(duck)

    def update(self):
        """Advance game state each frame."""
        if self.game_state == 'title':
            self.title_screen.update()
        else:
            self.environment.update()
            self.ducks.update()
            self.feathers.update()
            self.explosions.update()

            if self.flash_timer > 0:
                self.flash_timer -= 1

            if self.game_state == 'playing':
                self.spawn_timer += 1
                if self.spawn_timer >= 120 and self.ducks_spawned < self.ducks_per_round:
                    self.spawn_timer = 0
                    if len(self.ducks) < 2:
                        if random.random() < 0.33 and (self.ducks_spawned + 1) < self.ducks_per_round:
                            self.spawn_duck()
                            self.spawn_duck()
                            self.ducks_spawned += 2
                        else:
                            self.spawn_duck()
                            self.ducks_spawned += 1

                if self.ducks_spawned == self.ducks_per_round and len(self.ducks) == 0:
                    self.game_state = 'round_end'
                    self.spawn_timer = 0

            if self.game_state == 'round_end' and self.dog is None:
                mood = "happy" if self.ducks_hit >= self.ducks_per_round / 2 else "sad"
                self.dog = Dog(mood)

            if self.dog:
                self.dog.update()

    def draw(self):
        """Render everything."""
        if self.game_state == 'title':
            self.title_screen.draw(self.screen)
        else:
            self.environment.draw(self.screen)
            self.ducks.draw(self.screen)
            self.feathers.draw(self.screen)
            self.explosions.draw(self.screen)

            # HUD
            score_text = self.font.render(f'Score: {self.score}', True, (0, 0, 0))
            round_text = self.font.render(f'Round: {self.round}', True, (0, 0, 0))
            ducks_text = self.font.render(f'Ducks: {self.ducks_hit}/{self.ducks_per_round}', True, (0, 0, 0))
            self.screen.blit(score_text, (10, 10))
            self.screen.blit(round_text, (10, 60))
            self.screen.blit(ducks_text, (10, 110))

            if self.game_state == 'round_end':
                end_text = self.font.render(f'Round {self.round} Complete!', True, (0, 0, 0))
                continue_text = self.font.render('Tap to continue', True, (0, 0, 0))
                text_rect = end_text.get_rect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))
                cont_rect = continue_text.get_rect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2 + 50))
                self.screen.blit(end_text, text_rect)
                self.screen.blit(continue_text, cont_rect)

            # Brief muzzle flash effect
            if self.flash_timer > 0 and self.game_state == 'playing':
                if (self.flash_timer % 2) == 0:
                    flash_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
                    flash_surface.fill((255, 255, 255))
                    flash_surface.set_alpha(128)
                    self.screen.blit(flash_surface, (0, 0))

            # Dog above the grass
            if self.dog:
                clip_rect = pygame.Rect(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT - 100)
                old_clip = self.screen.get_clip()
                self.screen.set_clip(clip_rect)
                self.screen.blit(self.dog.image, self.dog.rect)
                self.screen.set_clip(old_clip)

        pygame.display.flip()

    def shoot(self, pos):
        """Shoot a duck if it is flying and the click intersects it."""
        if self.game_state == 'playing':
            for duck in self.ducks:
                if duck.rect.collidepoint(pos) and duck.state == 'flying':
                    duck.state = 'hit'
                    self.score += duck.variant.points
                    self.ducks_hit += 1
                    self._create_feathers(duck.rect.center)
                    break

    def _create_feathers(self, pos):
        """Spawn a handful of Feather sprites."""
        for _ in range(6):
            feather = Feather(*pos)
            self.feathers.add(feather)

    def run(self):
        """Main game loop."""
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.game_state == 'title':
                        self.game_state = 'playing'
                    elif self.game_state == 'playing':
                        self.flash_timer = int(FPS * 0.25)
                        explosion = Explosion(event.pos)
                        self.explosions.add(explosion)
                        self.shoot(event.pos)
                    elif self.game_state == 'round_end':
                        # Reset for next round
                        self.round += 1
                        self.ducks_per_round = 3 + self.round
                        self.ducks_spawned = 0
                        self.ducks_hit = 0
                        self.game_state = 'playing'
                        self.dog = None

            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()

def main():
    pygame.mixer.init()
    game = DuckHunt()
    game.run()

if __name__ == '__main__':
    main()