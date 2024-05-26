import pygame
import sys
from maze import create_maze
from entities import Player, Minotaur, PatrollingEnemy
from datetime import datetime
import random
import time
import json
import os

# Constants
TILE_SIZE = 20
LEVELS = [
    {"width": 40, "height": 30, "torches": 4, "minotaur_hp": 8, "minotaurs": 1, "minotaur_speed": 250, "music": "level1_music.mp3"},
    {"width": 50, "height": 40, "torches": 5, "minotaur_hp": 8, "minotaurs": 2, "minotaur_speed": 250, "music": "level2_music.mp3"},
    {"width": 60, "height": 50, "torches": 6, "minotaur_hp": 15, "minotaurs": 1, "minotaur_speed": 200, "music": "level3_music.mp3"}
]
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FONT_SIZE = 24
MOVE_DELAY = 200  # Milliseconds between moves
ENEMY_MOVE_DELAY = 500  # Milliseconds between enemy moves
MINOTAUR_PAUSE = 2000  # Milliseconds the minotaur stops after hitting the player
TORCH_RADIUS = 3  # Radius of visibility around torches
PLAYER_RADIUS = 4  # Radius of visibility around player
MAX_PATROLLING_ENEMIES = 8  # Maximum number of patrolling enemies

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class Game:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, FONT_SIZE)
        self.running = True
        self.start_menu = True
        self.hit_points = 3
        self.last_move_time = 0
        self.last_enemy_move_time = 0
        self.last_minotaur_move_time = 0
        self.last_minotaur_hit_time = -MINOTAUR_PAUSE
        self.start_time = None
        self.enemies_killed = 0
        self.torch_positions = []
        self.enemy_spawn_time = 0  # Track the time for spawning enemies
        self.scores_file = resource_path('scores.json')
        self.minotaurs_spring_to_life_message_displayed = False
        self.minotaurs_message_start_time = 0  # Track the time when the message is displayed
        self.message_display_duration = 3000  # Duration to display the message in milliseconds
        self.fog_of_war = True  # Initialize fog of war as enabled
        self.level = 0
        self.setup_level()

    def setup_level(self):
        level_info = LEVELS[self.level]
        self.width = level_info["width"]
        self.height = level_info["height"]
        self.torches = level_info["torches"]
        self.minotaur_speed = level_info["minotaur_speed"]

        self.maze, self.player_start = create_maze(self.width, self.height)
        self.player = Player(*self.find_free_space())
        self.last_move_direction = (0, -1)  # Initial direction (up)

        # Ensure minotaur and key are placed in empty spaces
        self.minotaurs = [Minotaur(*self.find_free_space(), level_info["minotaur_hp"]) for _ in range(level_info["minotaurs"])]
        self.key_pos = self.find_empty_space_far_from(self.player_start)
        self.exit_pos = self.find_empty_space_far_from(self.key_pos)
        self.has_key = False
        self.bullets = 6
        self.ammo_positions = self.place_ammo(5)
        self.bullet_positions = []
        self.blood_positions = []
        self.body_positions = []

        # Add random patrolling enemies
        self.patrolling_enemies = [PatrollingEnemy(*self.find_empty_space_away_from_player()) for _ in range(5)]

        # Load sounds
        self.load_sounds(level_info["music"])

        # Play background music
        pygame.mixer.music.play(-1)

    def find_free_space(self):
        while True:
            x, y = random.randint(1, self.width - 2), random.randint(1, self.height - 2)
            if self.maze[y][x] == ' ':
                return x, y

    def find_empty_space_far_from(self, position, min_distance=10):
        while True:
            x, y = random.randint(1, self.width - 2), random.randint(1, self.height - 2)
            if self.maze[y][x] == ' ' and abs(x - position[0]) + abs(y - position[1]) >= min_distance:
                return x, y

    def find_empty_space_away_from_player(self):
        while True:
            x, y = random.randint(1, self.width - 2), random.randint(1, self.height - 2)
            if self.maze[y][x] == ' ' and (abs(x - self.player.x) > 4 or abs(y - self.player.y) > 4):
                return x, y

    def find_accessible_exit(self):
        while True:
            x, y = random.randint(1, self.width - 2), random.randint(1, self.height - 2)
            if self.maze[y][x] == ' ':
                return x, y

    def place_ammo(self, amount):
        ammo_positions = []
        for _ in range(amount):
            x, y = self.find_free_space()
            ammo_positions.append((x, y))
        return ammo_positions

    def load_sounds(self, music_file):
        self.gun_sound = pygame.mixer.Sound(resource_path('sounds/gun_fire.mp3'))
        self.hit_sound = pygame.mixer.Sound(resource_path('sounds/hit.mp3'))
        self.death_sound = pygame.mixer.Sound(resource_path('sounds/death.mp3'))  # Add a death sound
        self.ammo_sound = pygame.mixer.Sound(resource_path('sounds/ammo_pickup.mp3'))  # Add ammo pickup sound
        self.minotaur_roar = pygame.mixer.Sound(resource_path('sounds/minotaur_roar.mp3'))  # Add minotaur roar sound
        self.win_sound = pygame.mixer.Sound(resource_path('sounds/win.mp3'))  # Add win sound
        self.lose_sound = pygame.mixer.Sound(resource_path('sounds/lose.mp3'))  # Add lose sound
        self.torch_drop_sound = pygame.mixer.Sound(resource_path('sounds/torch_drop.mp3'))  # Add torch drop sound

        pygame.mixer.music.load(resource_path(f'sounds/{music_file}'))

    def run(self):
        while self.running:
            if self.start_menu:
                self.show_start_menu()
            else:
                self.game_loop()
        pygame.quit()
        sys.exit()

    def show_start_menu(self):
        self.screen.fill((0, 0, 0))
        title = self.font.render("Escape the Minotaur!", True, (255, 255, 255))
        instruction = self.font.render("Press Enter to Start", True, (255, 255, 255))
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, SCREEN_HEIGHT // 3))
        self.screen.blit(instruction, (SCREEN_WIDTH // 2 - instruction.get_width() // 2, SCREEN_HEIGHT // 2))
        pygame.display.flip()

        while self.start_menu:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    self.start_menu = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        self.start_menu = False
                        self.start_time = time.time()  # Start the timer
                        self.enemy_spawn_time = self.start_time  # Initialize the enemy spawn time

    def game_loop(self):
        while self.running and not self.start_menu:
            current_time = pygame.time.get_ticks()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_f:
                        self.drop_torch()
                    if event.key == pygame.K_r:
                        self.restart_game()
                    if event.key == pygame.K_SPACE and self.bullets > 0:
                        self.shoot()
                    if event.key == pygame.K_z:  # Toggle fog of war
                        self.fog_of_war = not self.fog_of_war

            keys = pygame.key.get_pressed()
            if current_time - self.last_move_time > MOVE_DELAY:
                if keys[pygame.K_w]:
                    self.player.move(0, -1, self.maze)
                    self.last_move_time = current_time
                    self.last_move_direction = (0, -1)
                if keys[pygame.K_s]:
                    self.player.move(0, 1, self.maze)
                    self.last_move_time = current_time
                    self.last_move_direction = (0, 1)
                if keys[pygame.K_a]:
                    self.player.move(-1, 0, self.maze)
                    self.last_move_time = current_time
                    self.last_move_direction = (-1, 0)
                if keys[pygame.K_d]:
                    self.player.move(1, 0, self.maze)
                    self.last_move_time = current_time
                    self.last_move_direction = (1, 0)

            if current_time - self.last_enemy_move_time > ENEMY_MOVE_DELAY:
                for enemy in self.patrolling_enemies:
                    enemy.patrol(self.maze)
                self.last_enemy_move_time = current_time

            if current_time - self.last_minotaur_move_time > self.minotaur_speed:
                if self.has_key and current_time - self.last_minotaur_hit_time > MINOTAUR_PAUSE:
                    for minotaur in self.minotaurs:
                        minotaur.chase(self.maze, self.player)
                self.last_minotaur_move_time = current_time

            self.update_bullets()

            # Spawn new enemy every 10 seconds if there are less than the maximum number of patrolling enemies
            if time.time() - self.enemy_spawn_time > 10 and len(self.patrolling_enemies) < MAX_PATROLLING_ENEMIES:
                self.patrolling_enemies.append(PatrollingEnemy(*self.find_empty_space_away_from_player()))
                self.enemy_spawn_time = time.time()

            if (self.player.x, self.player.y) == self.key_pos:
                self.has_key = True
                self.key_pos = None
                self.minotaur_roar.play()  # Play minotaur roar sound
                self.minotaurs_spring_to_life_message_displayed = True
                self.minotaurs_message_start_time = current_time

            if (self.player.x, self.player.y) == self.exit_pos and self.has_key:
                elapsed_time = time.time() - self.start_time
                self.win_sound.play()
                pygame.mixer.music.stop()
                score = self.calculate_score(elapsed_time)
                self.save_score(elapsed_time, self.enemies_killed, score)
                self.level += 1
                if self.level < len(LEVELS):
                    self.setup_level()
                else:
                    self.show_game_over(f"You escaped the dungeon in {elapsed_time:.2f} seconds! Score: {score:.2f}")

            for minotaur in self.minotaurs:
                if self.has_key and (self.player.x, self.player.y) == (minotaur.x, minotaur.y):
                    self.hit_points -= 1
                    self.last_minotaur_hit_time = current_time
                    self.hit_sound.play()
                    if self.hit_points <= 0:
                        self.lose_sound.play()
                        pygame.mixer.music.stop()
                        elapsed_time = time.time() - self.start_time
                        self.save_score(elapsed_time, self.enemies_killed, 0)
                        self.show_game_over("The minotaur caught you!")

            for enemy in self.patrolling_enemies:
                if (self.player.x, self.player.y) == (enemy.x, enemy.y):
                    self.hit_points -= 1
                    self.hit_sound.play()
                    if self.hit_points <= 0:
                        self.lose_sound.play()
                        pygame.mixer.music.stop()
                        elapsed_time = time.time() - self.start_time
                        self.save_score(elapsed_time, self.enemies_killed, 0)
                        self.show_game_over("A patrolling enemy caught you!")

            for ammo in self.ammo_positions:
                if (self.player.x, self.player.y) == ammo:
                    self.bullets += 3
                    self.ammo_positions.remove(ammo)
                    self.ammo_sound.play()

            # Clear the "minotaurs spring to life" message after the specified duration
            if self.minotaurs_spring_to_life_message_displayed and (current_time - self.minotaurs_message_start_time > self.message_display_duration):
                self.minotaurs_spring_to_life_message_displayed = False

            self.draw()

    def shoot(self):
        self.bullets -= 1
        bullet_x, bullet_y = self.player.x, self.player.y
        bullet_dx, bullet_dy = self.last_move_direction
        self.bullet_positions.append((bullet_x, bullet_y, bullet_dx, bullet_dy))
        self.gun_sound.play()

    def drop_torch(self):
        if self.torches > 0:
            self.torches -= 1
            self.torch_positions.append((self.player.x, self.player.y))
            self.torch_drop_sound.play()

    def restart_game(self):
        self.level = 0
        self.__init__(self.screen)
        self.run()

    def update_bullets(self):
        new_bullet_positions = []
        for bullet in self.bullet_positions:
            x, y, dx, dy = bullet
            new_x, new_y = x + dx, y + dy
            if 0 <= new_x < self.width and 0 <= new_y < self.height and self.maze[new_y][new_x] != '#':
                for minotaur in self.minotaurs:
                    if (new_x, new_y) == (minotaur.x, minotaur.y) and self.has_key:  # Only damage if the key is collected
                        minotaur.hp -= 1
                        if minotaur.hp <= 0:
                            self.blood_positions.extend(self.generate_blood(new_x, new_y))
                            self.body_positions.append((new_x, new_y))
                            self.death_sound.play()
                            self.minotaurs.remove(minotaur)
                        else:
                            new_bullet_positions.append((new_x, new_y, dx, dy))
                        break
                else:
                    for enemy in self.patrolling_enemies:
                        if (new_x, new_y) == (enemy.x, enemy.y):
                            self.patrolling_enemies.remove(enemy)
                            self.blood_positions.extend(self.generate_blood(new_x, new_y))
                            self.body_positions.append((new_x, new_y))
                            self.death_sound.play()
                            self.enemies_killed += 1
                            break
                    else:
                        new_bullet_positions.append((new_x, new_y, dx, dy))
        self.bullet_positions = new_bullet_positions

    def generate_blood(self, x, y):
        blood = [(x, y)]
        for _ in range(10):  # Increase the number of blood spots
            blood.append((x + random.randint(-1, 1), y + random.randint(-1, 1)))
        return blood

    def calculate_score(self, elapsed_time):
        score = (self.enemies_killed * 100) / elapsed_time
        return score

    def save_score(self, elapsed_time, enemies_killed, score):
        score_entry = {
            "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "time": elapsed_time,
            "enemies_killed": enemies_killed,
            "score": score
        }
        try:
            with open(self.scores_file, 'r') as file:
                scores = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            scores = []

        scores.append(score_entry)
        with open(self.scores_file, 'w') as file:
            json.dump(scores, file, indent=4)

    def draw(self):
        self.screen.fill((0, 0, 0))

        # Determine the visible region of the maze based on player position
        view_x_start = max(0, self.player.x - SCREEN_WIDTH // (2 * TILE_SIZE))
        view_x_end = min(self.width, self.player.x + SCREEN_WIDTH // (2 * TILE_SIZE))
        view_y_start = max(0, self.player.y - SCREEN_HEIGHT // (2 * TILE_SIZE))
        view_y_end = min(self.height, self.player.y + SCREEN_HEIGHT // (2 * TILE_SIZE))

        for y in range(view_y_start, view_y_end):
            for x in range(view_x_start, view_x_end):
                rect = pygame.Rect((x - view_x_start) * TILE_SIZE, (y - view_y_start) * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                char = ' '
                color = (255, 255, 255)
                if self.maze[y][x] == '#':
                    char = '#'
                elif self.maze[y][x] == '^':
                    char = '^'
                    color = (128, 128, 128)  # Grey color for traps
                elif (x, y) == (self.player.x, self.player.y):
                    char = '@'
                    color = (0, 255, 0)
                elif any((x, y) == (minotaur.x, minotaur.y) for minotaur in self.minotaurs):
                    char = 'M'
                    color = (255, 0, 0)
                elif (x, y) == self.key_pos:
                    char = 'K'
                    color = (255, 215, 0)
                elif (x, y) == self.exit_pos:
                    char = 'E'
                    color = (0, 0, 255)
                elif any((x, y) == (enemy.x, enemy.y) for enemy in self.patrolling_enemies):
                    char = 'P'
                    color = (255, 0, 255)
                elif any((x, y) == (bx, by) for bx, by, _, _ in self.bullet_positions):
                    char = '*'
                    color = (255, 255, 0)
                elif (x, y) in self.ammo_positions:
                    char = 'A'
                    color = (255, 255, 0)
                elif (x, y) in self.blood_positions:
                    char = '+'
                    color = (139, 0, 0)  # Blood red
                elif (x, y) in self.body_positions:
                    char = 'b'
                    color = (139, 0, 0)  # Dark red for body
                elif (x, y) in self.torch_positions:
                    char = 'T'
                    color = (255, 140, 0)  # Orange for torch

                if not self.fog_of_war or self.is_visible(x, y):
                    text = self.font.render(char, True, color)
                    self.screen.blit(text, rect)
                else:
                    text = self.font.render(' ', True, color)
                    self.screen.blit(text, rect)

        hp_text = self.font.render(f"HP: {self.hit_points}", True, (255, 0, 0))
        bullets_text = self.font.render(f"Bullets: {self.bullets}", True, (0, 255, 0))
        torches_text = self.font.render(f"Torches: {self.torches}", True, (255, 165, 0))
        self.screen.blit(hp_text, (10, SCREEN_HEIGHT - 30))
        self.screen.blit(bullets_text, (200, SCREEN_HEIGHT - 30))
        self.screen.blit(torches_text, (400, SCREEN_HEIGHT - 30))

        minotaur_hp_texts = [self.font.render(f"Minotaur HP: {minotaur.hp}", True, (255, 0, 0)) for minotaur in self.minotaurs]
        for i, minotaur_hp_text in enumerate(minotaur_hp_texts):
            self.screen.blit(minotaur_hp_text, (10, SCREEN_HEIGHT - 60 - (i * 30)))

        if self.minotaurs_spring_to_life_message_displayed:
            spring_message = self.font.render("The Minotaurs spring to life! Run!", True, (255, 255, 255))
            self.screen.blit(spring_message, (SCREEN_WIDTH - spring_message.get_width() - 10, SCREEN_HEIGHT - 30))

        pygame.display.flip()
        self.clock.tick(60)

    def is_visible(self, x, y):
        if abs(x - self.player.x) <= PLAYER_RADIUS and abs(y - self.player.y) <= PLAYER_RADIUS:
            return True
        for tx, ty in self.torch_positions:
            if abs(x - tx) <= TORCH_RADIUS and abs(y - ty) <= TORCH_RADIUS:
                return True
        return False

    def show_game_over(self, message):
        self.screen.fill((0, 0, 0))
        game_over_text = self.font.render(message, True, (173, 216, 230))  # Light blue
        exit_text = self.font.render("Press 'q' to exit or 'r' to restart", True, (255, 255, 255))
        self.screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(exit_text, (SCREEN_WIDTH // 2 - exit_text.get_width() // 2, SCREEN_HEIGHT // 2 + 40))
        
        top_scores = self.get_top_scores()
        for i, score in enumerate(top_scores):
            score_text = f"{i+1}. {score['datetime']} - Time: {score['time']:.2f}s, Enemies: {score['enemies_killed']}, Score: {score['score']:.2f}"
            score_render = self.font.render(score_text, True, (255, 255, 255))
            self.screen.blit(score_render, (10, SCREEN_HEIGHT // 2 + 80 + i * 20))
        
        pygame.display.flip()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        self.running = False
                        return
                    if event.key == pygame.K_r:
                        self.restart_game()
                        return

    def get_top_scores(self):
        try:
            with open(self.scores_file, 'r') as file:
                scores = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

        scores = sorted(scores, key=lambda x: x['score'], reverse=True)
        return scores[:10]

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Escape the Minotaur!")
    game = Game(screen)
    game.run()
