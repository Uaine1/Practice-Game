import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
BG_COLOR = (135, 206, 235)  # Light blue color
PLAYER_COLOR = (255, 0, 0)  # Red color
ENEMY_COLOR = (0, 0, 255)  # Blue color
PLATFORM_COLOR = (0, 255, 0)  # Green color
GRAVITY = 1
PLAYER_JUMP_STRENGTH = 20
ATTACK_COLOR = (255, 255, 0)  # Yellow color
ATTACK_COOLDOWN = 500  # in milliseconds
HEART_IMAGE = pygame.image.load('heart.png')  # Load heart image

# Scale down the heart image
HEART_IMAGE = pygame.transform.scale(HEART_IMAGE, (30, 30))


def create_screen(width, height):
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Bootleg Hollow Knight")
    return screen


def create_player(x, y, width, height):
    return pygame.Rect(x, y, width, height)


def create_platforms():
    return [
        pygame.Rect(50, 550, 700, 50),
        pygame.Rect(200, 400, 150, 20),
        pygame.Rect(400, 300, 200, 20),
        pygame.Rect(650, 450, 100, 20),
        pygame.Rect(50, 200, 100, 20)
    ]


def create_enemy(x, y, width, height):
    return pygame.Rect(x, y, width, height)


def spawn_enemy(enemies, platforms):
    platform = random.choice(platforms)
    new_enemy_x = random.randint(platform.x, platform.x + platform.width - 50)
    new_enemy_y = platform.y - 50  # Position the enemy on top of the platform
    new_enemy = create_enemy(new_enemy_x, new_enemy_y, 50, 50)
    enemies.append(new_enemy)


def handle_events():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()


def get_player_input(player, is_jumping, facing_right):
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player.x -= 5
        facing_right = False
    if keys[pygame.K_RIGHT]:
        player.x += 5
        facing_right = True
    if keys[pygame.K_SPACE] and not is_jumping:
        return -PLAYER_JUMP_STRENGTH, facing_right
    return 0, facing_right


def apply_gravity(velocity_y):
    return velocity_y + GRAVITY


def check_collisions(player, platforms, velocity_y):
    is_on_ground = False
    for platform in platforms:
        if player.colliderect(platform) and velocity_y >= 0:
            player.y = platform.y - player.height
            velocity_y = 0
            is_on_ground = True
    return velocity_y, is_on_ground


def draw_elements(screen, player, platforms, enemies, attack_hitbox, health):
    screen.fill(BG_COLOR)
    pygame.draw.rect(screen, PLAYER_COLOR, player)
    for platform in platforms:
        pygame.draw.rect(screen, PLATFORM_COLOR, platform)
    for enemy in enemies:
        pygame.draw.rect(screen, ENEMY_COLOR, enemy)
    if attack_hitbox:
        pygame.draw.rect(screen, ATTACK_COLOR, attack_hitbox)
    draw_health_bar(screen, health)
    pygame.display.flip()


def handle_attack(player, enemies, last_attack_time, attack_cooldown, platforms, facing_right):
    keys = pygame.key.get_pressed()
    if keys[pygame.K_a] and pygame.time.get_ticks() - last_attack_time > attack_cooldown:
        if facing_right:
            attack_hitbox = pygame.Rect(player.right, player.y, 30, player.height)  # Attack to the right
        else:
            attack_hitbox = pygame.Rect(player.left - 30, player.y, 30, player.height)  # Attack to the left

        last_attack_time = pygame.time.get_ticks()
        for enemy in enemies[:]:  # Iterate over a copy of enemies list
            if attack_hitbox.colliderect(enemy):
                enemies.remove(enemy)  # Remove enemy if hit
                spawn_enemy(enemies, platforms)  # Spawn a new enemy on a platform
        return attack_hitbox, last_attack_time
    return None, last_attack_time


def draw_health_bar(screen, health):
    heart_width = HEART_IMAGE.get_width()
    heart_height = HEART_IMAGE.get_height()
    for i in range(3):
        screen.blit(HEART_IMAGE, (SCREEN_WIDTH - 10 - (i + 1) * (heart_width + 5), 10))

    for i in range(3 - health):
        pygame.draw.rect(screen, BG_COLOR, (SCREEN_WIDTH - 10 - (i + 1) * (heart_width + 5), 10, heart_width, heart_height))


def check_enemy_collision(player, enemies, health):
    for enemy in enemies:
        if player.colliderect(enemy):
            health -= 1  # Decrease health on collision with enemy
            if player.x < enemy.x:  # If player collided from left of enemy
                player.x -= 20
            else:  # If player collided from right of enemy
                player.x += 20
    return health


def game_over(screen):
    screen.fill(BG_COLOR)
    font = pygame.font.Font(None, 36)
    text = font.render("You Died", True, (255, 0, 0))
    text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    screen.blit(text, text_rect)
    font = pygame.font.Font(None, 24)
    retry_text = font.render("Press SPACE to Retry", True, (0, 0, 0))
    retry_rect = retry_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
    screen.blit(retry_text, retry_rect)
    pygame.display.flip()

    retry = False
    while not retry:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    retry = True

    # Reset game variables and restart the game
    main()


def main():
    screen = create_screen(SCREEN_WIDTH, SCREEN_HEIGHT)
    player = create_player(100, 500, 50, 50)
    platforms = create_platforms()
    enemies = []
    spawn_enemy(enemies, platforms)  # Spawn the initial enemy
    player_velocity_y = 0
    is_jumping = False
    facing_right = True  # Player starts facing right
    last_attack_time = 0
    health = 3  # Player's initial health

    running = True
    clock = pygame.time.Clock()

    while running:
        handle_events()
        jump_velocity, facing_right = get_player_input(player, is_jumping, facing_right)
        if jump_velocity:
            player_velocity_y = jump_velocity
            is_jumping = True

        player_velocity_y = apply_gravity(player_velocity_y)
        player.y += player_velocity_y
        player_velocity_y, is_on_ground = check_collisions(player, platforms, player_velocity_y)

        if is_on_ground:
            is_jumping = False
        else:
            is_jumping = True

        attack_hitbox, last_attack_time = handle_attack(player, enemies, last_attack_time, ATTACK_COOLDOWN, platforms, facing_right)

        health = check_enemy_collision(player, enemies, health)

        draw_elements(screen, player, platforms, enemies, attack_hitbox, health)

        if health <= 0:
            game_over(screen)  # Game over if health reaches zero
            main()  # Restart the game

        clock.tick(60)


if __name__ == "__main__":
    main()
