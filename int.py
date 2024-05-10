from flask import Flask, request, jsonify, render_template
import os
import json
from flask_socketio import SocketIO
import pygame
import random

app = Flask(__name__)
socketio = SocketIO(app)

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 500
SCREEN_HEIGHT = 600

# Colors
WHITE = (255, 255, 255)
GREY = (128, 128, 128)
BLACK = (0, 0, 0)

# Load background image
background_image = pygame.image.load("background.png").convert()

# Load game sounds
coin_sound = pygame.mixer.Sound("coin.wav")
collision_sound = pygame.mixer.Sound("crash.wav")

class PlayerCar(pygame.sprite.Sprite):
    def __init__(self, image_path):
        super().__init__()
        self.image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, (75, 150))
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = SCREEN_HEIGHT - 100
        self.speed_x = 0
        self.speed_y = 0
        self.max_speed = 10

    def update(self):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y
        if self.rect.left < 0:
            self.rect.left = 0
        elif self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.top < 0:
            self.rect.top = 0
        elif self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT

class RedCar(pygame.sprite.Sprite):
    def __init__(self, image_path):
        super().__init__()
        self.image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, (64, 36))
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(0, SCREEN_WIDTH - self.rect.width)
        self.rect.y = -self.rect.height
        self.speed = random.randint(4, 8)

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

class Coin(pygame.sprite.Sprite):
    def __init__(self, image_path):
        super().__init__()
        self.image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, (50, 50))
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(0, SCREEN_WIDTH - self.rect.width)
        self.rect.y = -self.rect.height
        self.speed = random.randint(4, 8)

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

@app.route('/')
def index():
    return render_template('int.html')

@socketio.on('start_game')
def start_game():
    main()

def main():  
    player = PlayerCar("car.png")
    all_sprites = pygame.sprite.Group(player)

    red_car_images = ["1.png","2.png","3.png", "4.png", "5.png", "6.png", "7.png"]
    coin_image = "coin.png"

    red_cars = pygame.sprite.Group()
    coins = pygame.sprite.Group()

    score = 0
    spawn_counter = 0
    coin_spawn_rate = 120
    red_car_spawn_rate = 45
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    player.speed_x = -player.max_speed
                elif event.key == pygame.K_RIGHT:
                    player.speed_x = player.max_speed
                elif event.key == pygame.K_UP:
                    player.speed_y = -player.max_speed
                elif event.key == pygame.K_DOWN:
                    player.speed_y = player.max_speed

            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                    player.speed_x = 0
                elif event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                    player.speed_y = 0

        if spawn_counter % red_car_spawn_rate == 0:
            red_car = RedCar(random.choice(red_car_images))
            all_sprites.add(red_car)
            red_cars.add(red_car)

        if spawn_counter % coin_spawn_rate == 0:
            coin = Coin(coin_image)
            all_sprites.add(coin)
            coins.add(coin)

        hits = pygame.sprite.spritecollide(player, red_cars, False)
        if hits:
            running = False
            collision_sound.play()

        coin_hits = pygame.sprite.spritecollide(player, coins, True)
        for coin in coin_hits:
            score += 10
            coin_sound.play()

        all_sprites.update()

        screen.blit(background_image, (0, 0))
        all_sprites.draw(screen)
        spawn_counter += 1
        pygame.display.flip()

if __name__ == '__main__':
    socketio.run(app, debug=True)
