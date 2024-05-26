import pygame
import json

FONT_SIZE = 24
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

class StartScreen:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, FONT_SIZE)
        self.scores_file = 'scores.json'

    def show(self):
        while True:
            self.screen.fill((0, 0, 0))
            title = self.font.render("Escape the Minotaur!", True, (255, 255, 255))
            instruction = self.font.render("Press Enter to Start", True, (255, 255, 255))
            view_scores = self.font.render("Press S to View Scores", True, (255, 255, 255))
            controls = self.font.render("Controls: W, A, S, D to move, SPACE to shoot, F to drop torch", True, (255, 255, 255))
            self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, SCREEN_HEIGHT // 3))
            self.screen.blit(instruction, (SCREEN_WIDTH // 2 - instruction.get_width() // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(view_scores, (SCREEN_WIDTH // 2 - view_scores.get_width() // 2, SCREEN_HEIGHT // 2 + 30))
            self.screen.blit(controls, (SCREEN_WIDTH // 2 - controls.get_width() // 2, SCREEN_HEIGHT // 2 + 60))
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        return "start"
                    if event.key == pygame.K_s:
                        return "scores"

    def display_scores(self):
        while True:
            self.screen.fill((0, 0, 0))
            title = self.font.render("Top Scores", True, (255, 255, 255))
            self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 20))

            top_scores = self.get_top_scores()
            for i, score in enumerate(top_scores):
                score_text = f"{i+1}. {score['datetime']} - Time: {score['time']:.2f}s, Enemies: {score['enemies_killed']}, Score: {score['score']:.2f}"
                score_render = self.font.render(score_text, True, (255, 255, 255))
                self.screen.blit(score_render, (10, 60 + i * 30))

            exit_text = self.font.render("Press B to go back", True, (255, 255, 255))
            self.screen.blit(exit_text, (SCREEN_WIDTH // 2 - exit_text.get_width() // 2, SCREEN_HEIGHT - 50))
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_b:
                        return

    def get_top_scores(self):
        try:
            with open(self.scores_file, 'r') as file:
                scores = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

        scores = sorted(scores, key=lambda x: x['score'], reverse=True)
        return scores[:10]
