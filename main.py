import pygame
import random
import json

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 500
SCREEN_HEIGHT = 600

# Colors
WHITE = (255, 255, 255)
GREY = (128, 128, 128)
BLACK = (0, 0, 0)

# Initialize the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Rally Trader")

clock = pygame.time.Clock()

# Load background image
background_image = pygame.image.load("background.png").convert()

# Load background music
pygame.mixer.music.load("sound.mp3")
pygame.mixer.music.set_volume(0.5)  # Set volume level
pygame.mixer.music.play(-1)  # Play the music on loop

# Load sound effects
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

def save_score(user_name, score):
    with open("scores.json", "r") as file:
        data = json.load(file)
    if user_name not in data:
        data[user_name]["credits"] = score
    else:
        data[user_name]["credits"] += score
    with open("scores.json", "w") as file:
        json.dump(data, file, indent=4)

def get_user_name():
    running = True
    user_name = ""
    while running:
        screen.fill(WHITE)
        font = pygame.font.Font(None, 36)
        text = font.render("Enter Your Name:", True, BLACK)
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        screen.blit(text, text_rect)

        input_rect = pygame.Rect(150, SCREEN_HEIGHT // 2, 200, 50)
        pygame.draw.rect(screen, BLACK, input_rect, 2)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    running = False
                elif event.key == pygame.K_BACKSPACE:
                    user_name = user_name[:-1]
                else:
                    user_name += event.unicode

        font = pygame.font.Font(None, 36)
        user_text = font.render(user_name, True, BLACK)
        screen.blit(user_text, (input_rect.x + 5, input_rect.y + 5))

        pygame.display.flip()
        clock.tick(30)
    return user_name

def main(user_name):  # Pass user_name as an argument
    start_button = pygame.Rect(200, 400, 100, 50)
    quit_button = pygame.Rect(200, 475, 100, 50)  # Define quit button
    running = True
    while running:
        screen.fill(WHITE)
        font = pygame.font.Font(None, 36)
        text = font.render("Rally Racing", True, BLACK)
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        screen.blit(text, text_rect)

        pygame.draw.rect(screen, BLACK, start_button)
        text = font.render("Start", True, WHITE)
        text_rect = text.get_rect(center=start_button.center)
        screen.blit(text, text_rect)

        pygame.draw.rect(screen, BLACK, quit_button)  # Draw quit button
        text = font.render("Quit", True, WHITE)
        text_rect = text.get_rect(center=quit_button.center)
        screen.blit(text, text_rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if start_button.collidepoint(event.pos):
                    running = False
                elif quit_button.collidepoint(event.pos):  # Check if quit button is clicked
                    pygame.quit()
                    quit()

        pygame.display.flip()
        clock.tick(30)

    player = PlayerCar("car.png")  # Specify the path to the player car image
    all_sprites = pygame.sprite.Group(player)  # Add player to all_sprites

    # Load custom images for red cars and coin
    red_car_images = ["1.png","2.png","3.png", "4.png", "5.png", "6.png", "7.png"]  # Specify paths to red car images
    coin_image = "coin.png"  # Specify path to the coin image

    # Create red car instances with random images
    for _ in range(2):  # Example: spawn 2 red cars
        red_car = RedCar(random.choice(red_car_images))
        all_sprites.add(red_car)

    # Create custom coin
    for _ in range(0):  # Example: spawn 1 coins
        coin = Coin(coin_image)
        all_sprites.add(coin)

    red_cars = pygame.sprite.Group()  # Create a group for red cars
    coins = pygame.sprite.Group()  # Create a group for coins

    score = 0
    running = True
    spawn_counter = 0
    coin_spawn_rate = 120
    red_car_spawn_rate = 45
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Key events for moving the player car
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

        # Spawn red cars
        if spawn_counter % red_car_spawn_rate == 0:
            red_car = RedCar(random.choice(red_car_images))
            all_sprites.add(red_car)
            red_cars.add(red_car)

        # Spawn coins
        if spawn_counter % coin_spawn_rate == 0:
            coin = Coin(coin_image)
            all_sprites.add(coin)
            coins.add(coin)

        # Check for collisions with red cars
        hits = pygame.sprite.spritecollide(player, red_cars, False)
        if hits:
            running = False
            collision_sound.play()  # Play collision sound
            save_score(user_name, score)

        # Check for collisions with coins
        coin_hits = pygame.sprite.spritecollide(player, coins, True)
        for coin in coin_hits:
            score += 10
            coin_sound.play()  # Play coin sound

        all_sprites.update()

        # Draw background
        screen.blit(background_image, (0, 0))

        # Draw game elements
        all_sprites.draw(screen)

        spawn_counter += 1
        pygame.display.flip()
        clock.tick(60)

    font = pygame.font.Font(None, 36)
    text = font.render(f"Game Over! Your score: {score}", True, WHITE)
    text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2.5))
    screen.blit(text, text_rect)

    restart_button = pygame.Rect(200, 275, 100, 50)
    pygame.draw.rect(screen, WHITE, restart_button)
    text = font.render("Restart", True, GREY)
    text_rect = text.get_rect(center=restart_button.center)
    screen.blit(text, text_rect)

    quit_button = pygame.Rect(200, 350, 100, 50)  # Define quit button
    pygame.draw.rect(screen, WHITE, quit_button)
    text = font.render("Quit", True, GREY)
    text_rect = text.get_rect(center=quit_button.center)
    screen.blit(text, text_rect)

    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if restart_button.collidepoint(event.pos):
                    # Reset game state
                    main(user_name)  # Pass user_name to main function
                elif quit_button.collidepoint(event.pos):  # Check if quit button is clicked
                    pygame.quit()
                    quit()

if __name__ == "__main__":
    user_name = get_user_name()  # Get user name only once at the beginning
    main(user_name)  # Pass user_name to main function
