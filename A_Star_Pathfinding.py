import pygame
import math
from queue import PriorityQueue
import sys

GRID_WIDTH = 800
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 900

# COLORS
RED          = (255, 0, 0)
GREEN        = (0, 255, 0)
BLUE         = (50, 50, 220)
ELECTRIC     = (126, 249, 255)
AIRFORCE     = (126, 139, 174)
TEAL         = (0, 128, 129)
CORNFLOWER   = (101, 147, 245)
OLYMPIC      = (0, 142, 204)
TURQUOISE    = (63, 224, 208)
AZURE        = (0, 128, 255)
YELLOW       = (255, 255, 0)
WHITE        = (220, 220, 220)
BLACK        = (0, 0, 0)
PURPLE       = (128, 0, 128)
ORANGE       = (255, 165, 0)
GREY         = (30, 30, 30)

class Node:
    def __init__(self, row, column, width, total_rows):
        self.row = row
        self.column = column
        self.x = row * width
        self.y = column * width
        self.color = BLACK
        self.neighbours = []
        self.width = width
        self.total_rows = total_rows

    def get_position(self):
        return (self.row, self.column)

    def is_closed(self):
        return self.color == CORNFLOWER

    def is_open(self):
        return self.color == BLUE

    def is_block(self):
        return self.color == WHITE

    def is_start(self):
        return self.color == AIRFORCE

    def is_end(self):
        return self.color == TEAL

    def start(self):
        self.color = AIRFORCE

    def reset(self):
        self.color = BLACK

    def close(self):
        self.color = CORNFLOWER

    def open(self):
        self.color = BLUE

    def block(self):
        self.color = WHITE

    def end(self):
        self.color = TEAL

    def path(self):
        self.color = TURQUOISE

    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))

    def update_neighbours(self, grid):
        self.neighbours = []

        # Check Down
        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.column].is_block():
            self.neighbours.append(grid[self.row + 1][self.column])

        # Check Up
        if self.row > 0 and not grid[self.row - 1][self.column].is_block():
            self.neighbours.append(grid[self.row - 1][self.column])

        # Check Right
        if self.column < self.total_rows - 1 and not grid[self.row][self.column + 1].is_block():
            self.neighbours.append(grid[self.row][self.column + 1])

        # Check Left
        if self.column > 0 and not grid[self.row][self.column - 1].is_block():
            self.neighbours.append(grid[self.row][self.column - 1])

def heuristic(point_1, point_2):
    x1, y1 = point_1
    x2, y2 = point_2

    return abs(x1 - x2) + abs(y1 - y2)

def build_grid(rows, width):
    grid = []
    gap = width // rows

    for i in range(rows):
        grid.append([])
        for j in range(rows):
            node = Node(i, j, gap, rows)
            grid[i].append(node)

    return grid

def draw_grid(win, rows, width):
    gap = width // rows

    for i in range(rows):
        pygame.draw.line(win, GREY, (0, i * gap), (width, i * gap))
        for j in range(rows):
            pygame.draw.line(win, GREY, (j * gap, 0), (j * gap, width))

def draw(win, grid, rows, width):

    win.fill(GREY)
    drawText('Right Click - Select ', 100, 820, WHITE)
    drawText('Left Click - Erase ', 93, 850, WHITE)
    drawText('Space - Solve ', 85, 880, WHITE)
    drawText('R - Reset ', 200, 880, WHITE)

    for row in grid:
        for node in row:
            node.draw(win)

    draw_grid(win, rows, width)
    pygame.display.update()

def get_clicked_position(pos, rows, width):
     gap = width // rows
     y, x = pos

     row = y // gap
     column = x // gap

     return row, column

def reconstruct_path(previous, current, draw):
    while current in previous:
        current = previous[current]
        current.path()
        draw()

# A* Algorithm
def solve(draw, grid, start, end):

    count = 0
    opSet = PriorityQueue()
    opSet.put((0, count, start))

    previous = {}

    g_score = {node: float("inf") for row in grid for node in row}
    g_score[start] = 0

    f_score = {node: float("inf") for row in grid for node in row}
    f_score[start] = heuristic(start.get_position(), end.get_position())

    opSet_hash = {start}

    while not opSet.empty():

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        current = opSet.get()[2]
        opSet_hash.remove(current)

        if current == end:
            reconstruct_path(previous, end, draw)
            end.end()
            start.start()
            return True

        for neighbour in current.neighbours:
            temp_g_score = g_score[current] + 1

            if temp_g_score < g_score[neighbour]:
                previous[neighbour] = current
                g_score[neighbour] = temp_g_score
                f_score[neighbour] = temp_g_score + heuristic(neighbour.get_position(), end.get_position())

                if neighbour not in opSet_hash:
                    count += 1
                    opSet.put((f_score[neighbour], count, neighbour))
                    opSet_hash.add(neighbour)
                    neighbour.open()

        draw()

        if current != start:
            current.close()

    return False

def drawText(message, x, y, color):


    font = pygame.font.SysFont('arial', 14)
    text = font.render(message, True, color, GREY)

    textRect = text.get_rect()
    textRect.center = (x, y)

    SCREEN.blit(text, textRect)

# MAIN FUCTION
def main(win, width):
    ROWS = 50
    grid = build_grid(ROWS, GRID_WIDTH)

    start = None
    end = None

    run = True
    started = False
    ended = False

    pygame.init()

    while run:
        draw(win, grid, ROWS, width)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.KEYDOWN:
                # Reset
                if event.key == pygame.K_r and ended:
                    start = None
                    end = None
                    started = False
                    ended = False
                    grid = build_grid(ROWS, width)
                # start the algorithm
                if event.key == pygame.K_SPACE and not started:
                    for row in grid:
                        for node in row:
                            node.update_neighbours(grid)
                    # Whenever there's a call for the algorithm we call draw()
                    started = True
                    res = solve(lambda: draw(win, grid, ROWS, width), grid, start, end)
                    if not res:
                        print("Couldn't resolve.")
                    else:
                        print("Solved!")
                    ended = True
            # algorithm is running
            if started:
                continue
            # press left
            if pygame.mouse.get_pressed()[0]:
                pos = pygame.mouse.get_pos()
                row, column = get_clicked_position(pos, ROWS, width)
                node = grid[row][column]
                if not start:
                    start = node
                    start.start()
                elif not end and node != start:
                    end = node
                    end.end()
                elif node != end and node != start:
                    node.block()
            # press right
            elif pygame.mouse.get_pressed()[2]:
                pos = pygame.mouse.get_pos()
                row, column = get_clicked_position(pos, ROWS, width)
                node = grid[row][column]
                node.reset()
                if node == start:
                    start = None
                if node == end:
                    end = None

    pygame.quit()

if __name__ == '__main__':
    SCREEN = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("A* Pathfinding Algorithm.")
    main(SCREEN, WINDOW_WIDTH)
