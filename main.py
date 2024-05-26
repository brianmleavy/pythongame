import pygame
from game import Game
from start_screen import StartScreen

def main():
    pygame.init()
    pygame.mixer.init()  # Initialize the mixer for sound
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Escape the Minotaur!")

    start_screen = StartScreen(screen)
    while True:
        choice = start_screen.show()
        if choice == "start":
            game = Game(screen)
            game.run()
        elif choice == "scores":
            start_screen.display_scores()

if __name__ == "__main__":
    main()
