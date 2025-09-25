import pygame
import sys

# Simple platformer: blue player cube, red enemy cubes, arrow-key controls

WIDTH, HEIGHT = 800, 600
FPS = 60
GRAVITY = 0.8

# Colors
BLUE = (60, 150, 255)
RED = (220, 50, 50)
GRAY = (50, 50, 50)
WHITE = (245, 245, 245)
BLACK = (10, 10, 10)

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h):
        super().__init__()
        self.image = pygame.Surface((w, h))
        self.image.fill(GRAY)
        self.rect = self.image.get_rect(topleft=(x, y))

class Player(pygame.sprite.Sprite):
    SIZE = 36
    SPEED = 4.5
    JUMP_SPEED = -14

    def __init__(self, x, y, platforms, enemies, all_sprites):
        super().__init__()
        self.image = pygame.Surface((self.SIZE, self.SIZE))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.vx = 0
        self.vy = 0
        self.platforms = platforms
        self.enemies = enemies
        self.all_sprites = all_sprites
        self.on_ground = False

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
        # apply gravity
        self.vy += GRAVITY
        # horizontal movement + collision
        self.rect.x += int(self.vx)
        hit_list = pygame.sprite.spritecollide(self, self.platforms, False)
        for p in hit_list:
            if self.vx > 0:
                self.rect.right = p.rect.left
            elif self.vx < 0:
                self.rect.left = p.rect.right
        # vertical movement + collision
        self.rect.y += int(self.vy)
        hit_list = pygame.sprite.spritecollide(self, self.platforms, False)
        self.on_ground = False
        for p in hit_list:
            if self.vy > 0:
                self.rect.bottom = p.rect.top
                self.vy = 0
                self.on_ground = True
            elif self.vy < 0:
                self.rect.top = p.rect.bottom
                self.vy = 0

        # keep inside screen horizontally
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH

        # enemy collisions
        enemy_hit = pygame.sprite.spritecollideany(self, self.enemies)
        if enemy_hit:
            # stomp enemy if falling onto it
            if self.vy > 0 and (self.rect.bottom - enemy_hit.rect.top) < 20:
                enemy_hit.kill()
                self.vy = self.JUMP_SPEED / 1.6
                self.on_ground = False
            else:
                # restart level on touch
                self.respawn()

    def respawn(self):
        # simple respawn: reset player to spawn point
        self.rect.topleft = (64, HEIGHT - 200)
        self.vx = self.vy = 0

class Enemy(pygame.sprite.Sprite):
    SIZE = 32

    def __init__(self, x, y, patrol_min_x, patrol_max_x, platforms):
        super().__init__()
        self.image = pygame.Surface((self.SIZE, self.SIZE))
        self.image.fill(RED)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.speed = 2
        self.direction = 1
        self.patrol_min_x = patrol_min_x
        self.patrol_max_x = patrol_max_x
        self.platforms = platforms
        self.vy = 0

    def update(self):
        # simple patrol
        self.rect.x += self.speed * self.direction
        if self.rect.left < self.patrol_min_x:
            self.rect.left = self.patrol_min_x
            self.direction *= -1
        if self.rect.right > self.patrol_max_x:
            self.rect.right = self.patrol_max_x
            self.direction *= -1

        # keep enemy on top of platforms if overlapping
        # basic gravity to stick to platforms
        self.vy += GRAVITY
        self.rect.y += int(self.vy)
        hits = pygame.sprite.spritecollide(self, self.platforms, False)
        for p in hits:
            if self.vy > 0:
                self.rect.bottom = p.rect.top
                self.vy = 0

class Level1:
    def __init__(self, all_sprites, platforms, enemies):
        # platforms layout for first level
        # ground
        Platform(0, HEIGHT - 40, WIDTH, 40).add(platforms, all_sprites)
        # some floating platforms
        Platform(100, HEIGHT - 140, 180, 20).add(platforms, all_sprites)
        Platform(360, HEIGHT - 220, 140, 20).add(platforms, all_sprites)
        Platform(540, HEIGHT - 300, 200, 20).add(platforms, all_sprites)
        Platform(240, HEIGHT - 360, 120, 20).add(platforms, all_sprites)
        Platform(20, HEIGHT - 260, 120, 20).add(platforms, all_sprites)
        Platform(660, HEIGHT - 180, 120, 20).add(platforms, all_sprites)

        # enemies: patrol between left/right bounds
        e1 = Enemy(120, HEIGHT - 172 - Enemy.SIZE + 20, 100, 100 + 160, platforms)
        e2 = Enemy(560, HEIGHT - 332 - Enemy.SIZE + 20, 540, 740, platforms)
        enemies.add(e1, e2)
        all_sprites.add(e1, e2)

class Game:
    def __init__(self):
        pygame.display.set_caption("Platformer — Level 1")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 28)

        # sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.platforms = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()

        # build level
        Level1(self.all_sprites, self.platforms, self.enemies)

        # create player
        self.player = Player(64, HEIGHT - 200, self.platforms, self.enemies, self.all_sprites)
        self.all_sprites.add(self.player)

        self.running = True

    def draw_instructions(self):
        lines = [
            "Arrow keys (or A/D) to move, Up/Space to jump.",
            "Stomp red enemies to defeat them. Touch them otherwise to respawn.",
            "Press R to restart level, Esc to quit."
        ]
        y = 8
        for line in lines:
            surf = self.font.render(line, True, WHITE)
            self.screen.blit(surf, (8, y))
            y += 22

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
                        self.restart_level()

            # update
            self.all_sprites.update()

            # draw
            self.screen.fill(BLACK)
            self.all_sprites.draw(self.screen)
            self.draw_instructions()
            pygame.display.flip()

        pygame.quit()
        sys.exit()

    def restart_level(self):
        # remove enemies and platforms and rebuild level and player
        self.all_sprites.empty()
        self.platforms.empty()
        self.enemies.empty()
        Level1(self.all_sprites, self.platforms, self.enemies)
        self.player = Player(64, HEIGHT - 200, self.platforms, self.enemies, self.all_sprites)
        self.all_sprites.add(self.player)