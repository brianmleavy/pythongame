import random

WALL = '#'

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def move(self, dx, dy, maze):
        new_x = self.x + dx
        new_y = self.y + dy
        if maze[new_y][new_x] != WALL:
            self.x = new_x
            self.y = new_y

class Minotaur:
    def __init__(self, x, y, hp):
        self.x = x
        self.y = y
        self.hp = hp

    def chase(self, maze, player):
        if player.x > self.x and maze[self.y][self.x + 1] != WALL:
            self.x += 1
        elif player.x < self.x and maze[self.y][self.x - 1] != WALL:
            self.x -= 1
        elif player.y > self.y and maze[self.y + 1][self.x] != WALL:
            self.y += 1
        elif player.y < self.y and maze[self.y - 1][self.x] != WALL:
            self.y -= 1

class PatrollingEnemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]

    def patrol(self, maze):
        dx, dy = random.choice(self.directions)
        new_x = self.x + dx
        new_y = self.y + dy
        if maze[new_y][new_x] != WALL:
            self.x = new_x
            self.y = new_y
