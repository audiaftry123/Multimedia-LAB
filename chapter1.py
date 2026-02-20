import sys
import random
import pygame
from pygame.locals import *

pygame.init()
pygame.mixer.init()

# =====================
# ASSETS
# =====================
player_ship = 'plyship.png'
enemy_ship = 'enemyship.png'
ufo_ship = 'ufo.png'
player_bullet_img = 'pbullet.png'
enemy_bullet_img = 'enemybullet.png'

laser_sound = pygame.mixer.Sound('laser.wav')
explosion_sound = pygame.mixer.Sound('low_expl.wav')
go_sound = pygame.mixer.Sound('go.wav')
game_over_sound = pygame.mixer.Sound('game_over.wav')
start_screen_music = pygame.mixer.Sound('cyberfunk.mp3')
game_over_music = pygame.mixer.Sound('illusoryrealm.mp3')

pygame.mixer.music.load('epicsong.mp3')

# =====================
# SCREEN
# =====================
screen = pygame.display.set_mode((0, 0), FULLSCREEN)
s_width, s_height = screen.get_size()
pygame.display.set_caption("SPACE WAR")

clock = pygame.time.Clock()
FPS = 60

pygame.mouse.set_visible(False)

# =====================
# SPRITE GROUPS
# =====================
all_sprites = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
player_bullets = pygame.sprite.Group()
enemy_bullets = pygame.sprite.Group()
ufo_group = pygame.sprite.Group()

# =====================
# CLASSES
# =====================

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load(player_ship).convert_alpha()
        self.rect = self.image.get_rect(center=(s_width//2, s_height-100))
        self.alive = True
        self.invincible_timer = 0

    def update(self):
        if self.alive:
            mouse_pos = pygame.mouse.get_pos()
            self.rect.center = mouse_pos

            if self.invincible_timer > 0:
                self.invincible_timer -= 1
                self.image.set_alpha(100)
            else:
                self.image.set_alpha(255)

    def shoot(self):
        bullet = Bullet(self.rect.centerx, self.rect.top, -15)
        player_bullets.add(bullet)
        all_sprites.add(bullet)
        laser_sound.play()

    def hit(self):
        if self.invincible_timer == 0:
            explosion_sound.play()
            self.invincible_timer = 120
            return True
        return False


class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load(enemy_ship).convert_alpha()
        self.rect = self.image.get_rect(
            x=random.randint(50, s_width-50),
            y=random.randint(-600, -50)
        )
        self.shoot_timer = random.randint(60, 180)

    def update(self):
        self.rect.y += 2

        if self.rect.top > s_height:
            self.rect.y = random.randint(-600, -50)
            self.rect.x = random.randint(50, s_width-50)

        self.shoot_timer -= 1
        if self.shoot_timer <= 0:
            self.shoot()
            self.shoot_timer = random.randint(90, 200)

    def shoot(self):
        bullet = Bullet(self.rect.centerx, self.rect.bottom, 6)
        enemy_bullets.add(bullet)
        all_sprites.add(bullet)


class UFO(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load(ufo_ship).convert_alpha()
        self.rect = self.image.get_rect(y=150)
        self.rect.x = -200
        self.speed = 4

    def update(self):
        self.rect.x += self.speed

        if self.rect.left > s_width or self.rect.right < 0:
            self.speed *= -1

        if random.randint(1, 120) == 1:
            bullet = Bullet(self.rect.centerx, self.rect.bottom, 8)
            enemy_bullets.add(bullet)
            all_sprites.add(bullet)


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, speed):
        super().__init__()
        if speed < 0:
            self.image = pygame.image.load(player_bullet_img).convert_alpha()
        else:
            self.image = pygame.image.load(enemy_bullet_img).convert_alpha()
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = speed

    def update(self):
        self.rect.y += self.speed
        if self.rect.bottom < 0 or self.rect.top > s_height:
            self.kill()


# =====================
# GAME CLASS
# =====================

class Game:
    def __init__(self):
        self.score = 0
        self.lives = 3
        self.running = True
        self.start_screen()

    def start_screen(self):
        start_screen_music.play(-1)

        while True:
            screen.fill("black")

            font = pygame.font.SysFont("Calibri", 60)
            text = font.render("SPACE WAR", True, "cyan")
            screen.blit(text, text.get_rect(center=(s_width//2, s_height//2)))

            font2 = pygame.font.SysFont("Calibri", 25)
            text2 = font2.render("Press ENTER to Start", True, "white")
            screen.blit(text2, text2.get_rect(center=(s_width//2, s_height//2+60)))

            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == KEYDOWN:
                    if event.key == K_RETURN:
                        start_screen_music.stop()
                        self.run()

                    if event.key == K_ESCAPE:
                        pygame.quit()
                        sys.exit()

            pygame.display.update()
            clock.tick(FPS)

    def run(self):
        go_sound.play()
        pygame.mixer.music.play(-1)

        player = Player()
        all_sprites.add(player)

        for _ in range(8):
            enemy = Enemy()
            enemy_group.add(enemy)
            all_sprites.add(enemy)

        ufo = UFO()
        ufo_group.add(ufo)
        all_sprites.add(ufo)

        while self.running:
            screen.fill("black")

            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                    if event.key == K_SPACE:
                        player.shoot()

            # COLLISIONS
            hits = pygame.sprite.groupcollide(enemy_group, player_bullets, True, True)
            for hit in hits:
                explosion_sound.play()
                self.score += 10
                enemy = Enemy()
                enemy_group.add(enemy)
                all_sprites.add(enemy)

            if pygame.sprite.spritecollide(player, enemy_bullets, True):
                if player.hit():
                    self.lives -= 1
                    if self.lives <= 0:
                        self.game_over()

            all_sprites.update()
            all_sprites.draw(screen)

            self.draw_ui()

            pygame.display.update()
            clock.tick(FPS)

    def draw_ui(self):
        font = pygame.font.SysFont("Calibri", 25)
        score_text = font.render(f"Score: {self.score}", True, "green")
        screen.blit(score_text, (s_width-200, 20))

        for i in range(self.lives):
            life_img = pygame.transform.scale(
                pygame.image.load(player_ship), (30, 30))
            screen.blit(life_img, (20 + i*40, 20))

    def game_over(self):
        pygame.mixer.music.stop()
        game_over_sound.play()
        game_over_music.play(-1)

        while True:
            screen.fill("black")

            font = pygame.font.SysFont("Calibri", 60)
            text = font.render("GAME OVER", True, "red")
            screen.blit(text, text.get_rect(center=(s_width//2, s_height//2)))

            font2 = pygame.font.SysFont("Calibri", 25)
            text2 = font2.render("Press ESC to Quit", True, "white")
            screen.blit(text2, text2.get_rect(center=(s_width//2, s_height//2+60)))

            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        pygame.quit()
                        sys.exit()

            pygame.display.update()
            clock.tick(FPS)


if __name__ == "__main__":
    Game()