import pygame
import sys
import importlib
from settings import SCREEN_WIDTH as WIDTH, SCREEN_HEIGHT as HEIGHT, FPS, WHITE, BLACK, RED, BLUE, GREEN

# handy alias expected by your visualization script
SCREEN_HEIGHT = HEIGHT

# extra palette colors used by visualizer / powerups
BROWN = (139, 69, 19)
DARK_GREEN = (0, 100, 0)
LIGHT_BLUE = (173, 216, 230)

GRAVITY = 0.8
LEVEL_WIDTH = 3000  # linear world width

LEVEL_MODULES = [
    "levels.level1",
    "levels.level2",
    "levels.level3",
]

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h):
        super().__init__()
        self.image = pygame.Surface((w, h))
        self.image.fill(BROWN)
        pygame.draw.rect(self.image, DARK_GREEN, (0, 0, w, min(h, 8)))
        self.rect = self.image.get_rect(topleft=(x, y))

class Door(pygame.sprite.Sprite):
    SIZE = 48
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((self.SIZE, self.SIZE))
        self.image.fill(BROWN)
        pygame.draw.rect(self.image, BLACK, (5, 5, self.SIZE - 10, self.SIZE - 10), 2)
        pygame.draw.circle(self.image, (255, 255, 0), (self.SIZE - 15, self.SIZE // 2), 3)
        self.rect = self.image.get_rect(bottomleft=(x, y))

class Player(pygame.sprite.Sprite):
    SIZE = 36
    SPEED = 5
    JUMP_SPEED = -15

    def __init__(self, x, y, platforms, enemies, all_sprites, door_group):
        super().__init__()
        self.image = pygame.Surface((self.SIZE, self.SIZE), pygame.SRCALPHA)
        self.image.fill(BLUE)
        eye_pos = (self.SIZE * 2 // 3, self.SIZE // 3)
        pygame.draw.circle(self.image, WHITE, eye_pos, 4)
        pygame.draw.circle(self.image, BLACK, eye_pos, 2)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.vx = 0
        self.vy = 0
        self.platforms = platforms
        self.enemies = enemies
        self.all_sprites = all_sprites
        self.door_group = door_group
        self.on_ground = False
        self.spawn = (x, y)
        self.reached_goal = False

    def handle_input(self):
        keys = pygame.key.get_pressed()
        self.vx = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vx = -self.SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vx = self.SPEED
        if (keys[pygame.K_UP] or keys[pygame.K_SPACE] or keys[pygame.K_w]) and self.on_ground:
            self.vy = self.JUMP_SPEED
            self.on_ground = False

    def update(self):
        self.handle_input()
        self.vy += GRAVITY

        # horizontal
        self.rect.x += int(self.vx)
        hits = pygame.sprite.spritecollide(self, self.platforms, False)
        for p in hits:
            if self.vx > 0:
                self.rect.right = p.rect.left
            elif self.vx < 0:
                self.rect.left = p.rect.right

        # vertical
        self.rect.y += int(self.vy)
        hits = pygame.sprite.spritecollide(self, self.platforms, False)
        self.on_ground = False
        for p in hits:
            if self.vy > 0:
                self.rect.bottom = p.rect.top
                self.vy = 0
                self.on_ground = True
            elif self.vy < 0:
                self.rect.top = p.rect.bottom
                self.vy = 0

        # world bounds
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > LEVEL_WIDTH:
            self.rect.right = LEVEL_WIDTH

        # enemy collisions
        enemy_hit = pygame.sprite.spritecollideany(self, self.enemies)
        if enemy_hit:
            if self.vy > 0 and (self.rect.bottom - enemy_hit.rect.top) < 20:
                enemy_hit.kill()
                self.vy = self.JUMP_SPEED / 1.6
                self.on_ground = False
            else:
                self.respawn()

        # door collision (level complete)
        if pygame.sprite.spritecollideany(self, self.door_group):
            self.reached_goal = True

    def respawn(self):
        self.rect.topleft = self.spawn
        self.vx = self.vy = 0
        self.reached_goal = False

class Enemy(pygame.sprite.Sprite):
    SIZE = 32

    def __init__(self, x, y, patrol_min_x=None, patrol_max_x=None, platforms=None, enemy_type=None):
        """
        Backwards-compatible constructor:
        - Normal use in levels: Enemy(x, y, patrol_min_x, patrol_max_x, platforms)
        - Visualization use:  Enemy(x, y, "trash")  (string passed as patrol_min_x)
        """
        super().__init__()

        # allow shorthand where the third argument is a type string
        if isinstance(patrol_min_x, str) and patrol_max_x is None:
            enemy_type = patrol_min_x
            # give a small default patrol range around x
            patrol_min_x = x - 40
            patrol_max_x = x + 40
            platforms = platforms  # might be None

        self.enemy_type = enemy_type or "default"

        self.image = pygame.Surface((self.SIZE, self.SIZE), pygame.SRCALPHA)
        # choose appearance based on type string for visualization
        if self.enemy_type == "trash":
            self.image.fill(BROWN)
        elif self.enemy_type == "plane":
            self.image.fill(LIGHT_BLUE)
            pygame.draw.polygon(self.image, (200,200,200), [(4, self.SIZE//2), (self.SIZE-4, 4), (self.SIZE-4, self.SIZE-4)])
        elif self.enemy_type == "car":
            self.image.fill(DARK_GREEN)
            pygame.draw.rect(self.image, (20,20,20), (4, self.SIZE-10, self.SIZE-8, 6))
        else:
            self.image.fill(RED)

        self.rect = self.image.get_rect(topleft=(x, y))
        self.speed = 2
        self.direction = 1
        self.patrol_min_x = patrol_min_x if patrol_min_x is not None else x - 40
        self.patrol_max_x = patrol_max_x if patrol_max_x is not None else x + 40
        self.platforms = platforms if platforms is not None else pygame.sprite.Group()
        self.vy = 0

    def update(self):
        self.rect.x += int(self.speed * self.direction)
        if self.rect.left < self.patrol_min_x:
            self.rect.left = self.patrol_min_x
            self.direction *= -1
        if self.rect.right > self.patrol_max_x:
            self.rect.right = self.patrol_max_x
            self.direction *= -1

        # gravity/stick to platform
        self.vy += GRAVITY
        self.rect.y += int(self.vy)
        hits = pygame.sprite.spritecollide(self, self.platforms, False)
        for p in hits:
            if self.vy > 0:
                self.rect.bottom = p.rect.top
                self.vy = 0

class PowerUp(pygame.sprite.Sprite):
    """
    Simple visual powerup placeholder. Types: "tree", "faucet", "solar", "recycle" (visualized)
    """
    SIZE = 28

    def __init__(self, x, y, pu_type="tree"):
        super().__init__()
        self.type = pu_type
        self.image = pygame.Surface((self.SIZE, self.SIZE), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(x, y))
        self._draw_type()

    def _draw_type(self):
        self.image.fill((0,0,0,0))  # transparent
        if self.type == "tree":
            # trunk + foliage
            pygame.draw.rect(self.image, BROWN, (10, 14, 8, 12))
            pygame.draw.circle(self.image, DARK_GREEN, (14, 10), 10)
        elif self.type == "faucet":
            # faucet body + droplet
            pygame.draw.rect(self.image, (160,160,160), (6,8,16,6))
            pygame.draw.ellipse(self.image, LIGHT_BLUE, (10,18,8,10))
        elif self.type == "solar":
            # sun / panel
            pygame.draw.circle(self.image, (255, 215, 0), (14, 10), 8)
            pygame.draw.rect(self.image, (200,200,200), (4,20,20,6))
        elif self.type == "recycle":
            # simple recycle symbol (triangle-ish)
            pygame.draw.polygon(self.image, (100,200,100), [(6,20),(22,20),(14,6)])
            pygame.draw.circle(self.image, (60,160,60), (14,14), 6, 2)
        else:
            # fallback
            pygame.draw.rect(self.image, (180,180,180), (4,4,self.SIZE-8,self.SIZE-8))

    def update(self):
        pass  # static visuals for now

class Game:
    def __init__(self):
        pygame.display.set_caption("Platformer — Levels")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 28)

        # sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.platforms = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.door_group = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()

        self.level_index = 0
        self.running = True
        self.won_game = False

        # load first level
        self.load_level(self.level_index)

    def load_level(self, index):
        # clear groups
        self.all_sprites.empty()
        self.platforms.empty()
        self.enemies.empty()
        self.door_group.empty()
        self.powerups.empty()

        # import chosen level module and get data
        mod_name = LEVEL_MODULES[index]
        mod = importlib.import_module(mod_name)
        data = mod.get_level_data(LEVEL_WIDTH, HEIGHT)

        # create platforms
        for p in data.get("platforms", []):
            Platform(*p).add(self.platforms, self.all_sprites)

        # create enemies
        for e in data.get("enemies", []):
            x, y, mn, mx = e
            enemy = Enemy(x, y, mn, mx, self.platforms)
            self.enemies.add(enemy)
            self.all_sprites.add(enemy)

        # create powerups
        for p in data.get("powerups", []):
            pu = PowerUp(p[0], p[1], p[2])
            self.powerups.add(pu)
            self.all_sprites.add(pu)

        # door
        door_x = data.get("door_x", LEVEL_WIDTH - 120)
        door = Door(door_x, HEIGHT - 40)
        self.door_group.add(door)
        self.all_sprites.add(door)

        # player spawn
        spawn = data.get("player_spawn", (64, HEIGHT - 200))
        self.player = Player(spawn[0], spawn[1], self.platforms, self.enemies, self.all_sprites, self.door_group)
        self.all_sprites.add(self.player)
        self.player.reached_goal = False
        self.won_game = False

    def draw_instructions(self):
        lines = [
            "Arrow keys (or A/D) to move, Up/Space to jump.",
            "Reach the door at the right to advance. Stomp red enemies.",
            "Press R to restart level, Esc to quit."
        ]
        y = 8
        for line in lines:
            surf = self.font.render(line, True, WHITE)
            self.screen.blit(surf, (8, y))
            y += 22

    def draw_background(self, camera_x):
        self.screen.fill((20, 20, 80)) # Dark blue night sky
        # Parallax effect for stars
        for i in range(200):
            # Use a hash of i to get pseudo-random but consistent positions
            x = (hash(i*3) % (LEVEL_WIDTH * 2)) - LEVEL_WIDTH // 2
            y = hash(i*7) % HEIGHT
            size = 1 + (hash(i*11) % 2)
            # Slower scroll for distant stars
            screen_x = (x - camera_x * 0.5) % WIDTH
            pygame.draw.circle(self.screen, WHITE, (screen_x, y), size)

    def draw_world(self, camera_x):
        # draw each sprite at offset (world -> screen)
        for sprite in self.all_sprites:
            draw_rect = sprite.rect.move(-camera_x, 0)
            self.screen.blit(sprite.image, draw_rect)

    def next_level(self):
        self.level_index += 1
        if self.level_index >= len(LEVEL_MODULES):
            # finished all levels
            self.won_game = True
            # keep showing final message until R pressed
        else:
            self.load_level(self.level_index)

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    if event.key == pygame.K_r:
                        # restart entire game (back to level 0)
                        self.level_index = 0
                        self.load_level(0)

            # update sprites
            self.all_sprites.update()

            # advance level if player reached door
            if self.player.reached_goal and not self.won_game:
                # small pause could be added here; immediate advance:
                self.next_level()

            # camera follows player but stays within world bounds
            camera_x = max(0, min(self.player.rect.centerx - WIDTH // 2, LEVEL_WIDTH - WIDTH))

            # draw
            self.draw_background(camera_x)
            self.draw_world(camera_x)
            self.draw_instructions()

            # level messages
            if self.player.reached_goal and not self.won_game and self.level_index < len(LEVEL_MODULES):
                msg = f"Level {self.level_index} complete! Advancing..."
                surf = self.font.render(msg, True, WHITE)
                self.screen.blit(surf, (WIDTH//2 - surf.get_width()//2, 40))

            if self.won_game:
                win_surf = self.font.render("You beat the game! Press R to play again.", True, WHITE)
                self.screen.blit(win_surf, (WIDTH//2 - win_surf.get_width()//2, HEIGHT//2 - 16))

            pygame.display.flip()

        pygame.quit()
        sys.exit()

    def restart_level(self):
        # not used now — kept for compatibility
        self.load_level(self.level_index)