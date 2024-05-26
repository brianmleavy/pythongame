import random

WALL = '#'
EMPTY = ' '
TRAP = '^'

def create_room(maze, x, y, room_width, room_height):
    for i in range(x, x + room_width):
        for j in range(y, y + room_height):
            maze[j][i] = EMPTY

def create_h_corridor(maze, x1, x2, y):
    for x in range(min(x1, x2), max(x1, x2) + 1):
        maze[y][x] = EMPTY

def create_v_corridor(maze, y1, y2, x):
    for y in range(min(y1, y2), max(y1, y2) + 1):
        maze[y][x] = EMPTY

def create_dungeon(width, height, max_rooms, room_min_size, room_max_size):
    maze = [[WALL for _ in range(width)] for _ in range(height)]
    rooms = []

    for _ in range(max_rooms):
        room_width = random.randint(room_min_size, room_max_size)
        room_height = random.randint(room_min_size, room_max_size)
        x = random.randint(1, width - room_width - 1)
        y = random.randint(1, height - room_height - 1)

        new_room = (x, y, room_width, room_height)

        failed = False
        for other_room in rooms:
            if (x < other_room[0] + other_room[2] and x + room_width > other_room[0] and
                y < other_room[1] + other_room[3] and y + room_height > other_room[1]):
                failed = True
                break

        if not failed:
            create_room(maze, x, y, room_width, room_height)
            if rooms:
                prev_x, prev_y, prev_w, prev_h = rooms[-1]
                prev_center_x = prev_x + prev_w // 2
                prev_center_y = prev_y + prev_h // 2
                new_center_x = x + room_width // 2
                new_center_y = y + room_height // 2

                if random.randint(0, 1) == 1:
                    create_h_corridor(maze, prev_center_x, new_center_x, prev_center_y)
                    create_v_corridor(maze, prev_center_y, new_center_y, new_center_x)
                else:
                    create_v_corridor(maze, prev_center_y, new_center_y, prev_center_x)
                    create_h_corridor(maze, prev_center_x, new_center_x, new_center_y)

            rooms.append(new_room)

    for _ in range(width * height // 15):  # Adjust the number of traps accordingly
        x, y = random.randint(1, width - 2), random.randint(1, height - 2)
        if maze[y][x] == EMPTY:
            maze[y][x] = TRAP

    return maze, (rooms[0][0] + rooms[0][2] // 2, rooms[0][1] + rooms[0][3] // 2)

def create_maze(width, height):
    return create_dungeon(width, height, max_rooms=15, room_min_size=3, room_max_size=7)
