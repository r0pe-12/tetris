import sys
import pygame
import random
import requests
import tkinter as tk
from tkinter import simpledialog

pygame.init()

# constants
WIDTH, HEIGHT = 300, 500
FPS = 35
CELL = 20
PADDING_BOTTOM = 120
ROWS, COLS = (HEIGHT - PADDING_BOTTOM) // CELL, WIDTH // CELL

SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
pygame.display.set_caption('Tetris')

# colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BG_COLOR = (31, 25, 76)
GRID = (31, 25, 132)
WIN = (50, 230, 50)
LOSE = (252, 91, 122)
API_ENDPOINT = "https://udg.tetris.simonovicp.com/save_score"

# assets
ASSETS = {
    1: pygame.image.load('Assets/1.png'),
    2: pygame.image.load('Assets/2.png'),
    3: pygame.image.load('Assets/3.png'),
    4: pygame.image.load('Assets/4.png')
}

# fonts
font = pygame.font.SysFont('Inter', 50)
font2 = pygame.font.SysFont('Inter', 15)


# shape class
class Shape:
    VERSION = {
        'I': [[1, 5, 9, 13], [4, 5, 6, 7]],
        'Z': [[4, 5, 9, 10], [2, 6, 5, 9]],
        'S': [[6, 7, 9, 10], [1, 5, 6, 10]],
        'L': [[1, 2, 5, 9], [0, 4, 5, 6], [1, 5, 9, 8], [4, 5, 6, 10]],
        'J': [[1, 2, 6, 10], [5, 6, 7, 9], [2, 6, 10, 11], [3, 5, 6, 7]],
        'T': [[1, 4, 5, 6], [1, 4, 5, 9], [4, 5, 6, 9], [1, 5, 6, 9]],
        'O': [[1, 2, 5, 6]]
    }
    SHAPES = ['I', 'Z', 'S', 'L', 'J', 'T', 'O']

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.type = random.choice(self.SHAPES)
        self.shape = self.VERSION[self.type]
        self.color = random.randint(1, 4)
        self.orientation = 0

    # orientation of shape
    def image(self):
        return self.shape[self.orientation]

    # rotation
    def rotate(self):
        self.orientation = (self.orientation + 1) % len(self.shape)


class Tetris:
    def __init__(self, rows, cols):
        self.figure = None
        self.rows = rows
        self.cols = cols
        self.score = 0
        self.level = 1
        self.next = None
        self.end = False
        self.new_shape()
        self.grid = [
            [0 for _ in range(self.cols)] for _ in range(self.rows)
        ]

    # draw grid
    def make_grid(self):
        for i in range(self.rows + 1):
            pygame.draw.line(SCREEN, GRID, (0, CELL * i), (WIDTH, CELL * i))
        for j in range(self.cols + 1):
            pygame.draw.line(SCREEN, GRID, (CELL * j, 0), (CELL * j, HEIGHT - PADDING_BOTTOM))

    # make new shape
    def new_shape(self):
        if not self.next:
            self.next = Shape(5, 0)
        self.figure = self.next
        self.next = Shape(5, 0)

    # collision
    def collision(self) -> bool:
        for i in range(4):
            for j in range(4):
                if (i * 4 + j) in self.figure.image():
                    block_row = i + self.figure.y
                    block_col = j + self.figure.x
                    if (block_row >= self.rows or block_col >= self.cols or block_col < 0 or
                            self.grid[block_row][block_col] > 0):
                        return True
        return False

    # remove row
    def remove_row(self):
        rerun = False
        for y in range(self.rows - 1, 0, -1):
            completed = True
            for x in range(0, self.cols):
                if self.grid[y][x] == 0:
                    completed = False
            if completed:
                del self.grid[y]
                self.grid.insert(0, [0 for _ in range(self.cols)])
                self.score += 1
                if self.score % 10 == 0:
                    self.level += 1
                rerun = True
        if rerun:
            self.remove_row()

    # freeze
    def freeze(self):
        for i in range(4):
            for j in range(4):
                if (i * 4 + j) in self.figure.image():
                    self.grid[i + self.figure.y][j + self.figure.x] = self.figure.color
        self.remove_row()
        self.new_shape()
        if self.collision():
            self.end = True

    # move down
    def move_down(self):
        self.figure.y += 1
        if self.collision():
            self.figure.y -= 1
            self.freeze()

    # move left
    def left(self):
        self.figure.x -= 1
        if self.collision():
            self.figure.x += 1

    # move right
    def right(self):
        self.figure.x += 1
        if self.collision():
            self.figure.x -= 1

    # freefall
    def freefall(self):
        while not self.collision():
            self.figure.y += 1
        self.figure.y -= 1
        self.freeze()

    # rotate
    def rotate(self):
        orientation = self.figure.orientation
        self.figure.rotate()
        if self.collision():
            self.figure.orientation = orientation

    @staticmethod
    def end_game():
        popup = pygame.Rect(50, 140, WIDTH - 100, HEIGHT - 350)
        pygame.draw.rect(SCREEN, BLACK, popup)
        pygame.draw.rect(SCREEN, LOSE, popup, 2)

        game_over = font2.render("GAME OVER!", True, WHITE)
        option1 = font2.render("Press r to restart", True, LOSE)
        option2 = font2.render("Press q to quit", True, LOSE)

        SCREEN.blit(game_over, (popup.centerx - game_over.get_width() // 2, popup.y + 20))
        SCREEN.blit(option1, (popup.centerx - option1.get_width() // 2, popup.y + 80))
        SCREEN.blit(option2, (popup.centerx - option2.get_width() // 2, popup.y + 110))


def get_username(screen_width=WIDTH, screen_height=HEIGHT):
    """
        Custom Pygame username input dialog
        """
    # Create a new window for username input
    username_screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption('Enter Username')

    # Colors
    BG_COLOR = (31, 25, 76)
    WHITE = (255, 255, 255)
    INPUT_COLOR = (50, 50, 100)
    ACTIVE_COLOR = (70, 70, 130)
    TEXT_COLOR = (255, 255, 255)

    # Fonts
    title_font = pygame.font.SysFont('Inter', 30)
    input_font = pygame.font.SysFont('Inter', 25)

    # Input box
    input_box = pygame.Rect(50, 250, screen_width - 100, 50)
    color_inactive = INPUT_COLOR
    color_active = ACTIVE_COLOR
    color = color_inactive
    active = False
    text = ''
    done = False

    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                # If the user clicked on the input_box rect
                if input_box.collidepoint(event.pos):
                    # Toggle the active variable
                    active = not active
                else:
                    active = False
                # Change the input box color
                color = color_active if active else color_inactive

            if event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN:
                        done = True
                    elif event.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                    else:
                        text += event.unicode

        # Clear the screen
        username_screen.fill(BG_COLOR)

        # Render title
        title = title_font.render('Enter Your Username', True, WHITE)
        title_rect = title.get_rect(center=(screen_width // 2, 150))
        username_screen.blit(title, title_rect)

        # Render instructions
        instructions = input_font.render('Press ENTER to confirm', True, (150, 150, 200))
        instructions_rect = instructions.get_rect(center=(screen_width // 2, 200))
        username_screen.blit(instructions, instructions_rect)

        # Render input box
        txt_surface = input_font.render(text, True, TEXT_COLOR)
        width = max(screen_width - 100, txt_surface.get_width() + 10)
        input_box.w = width

        # Draw the input box
        pygame.draw.rect(username_screen, color, input_box)
        pygame.draw.rect(username_screen, WHITE, input_box, 2)  # Border

        # Render the text
        text_rect = txt_surface.get_rect(center=input_box.center)
        username_screen.blit(txt_surface, text_rect)

        # Update the display
        pygame.display.flip()

    # Switch back to the original display mode
    pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption('Tetris')

    # Return the username or default if empty
    return text.strip() if text.strip() else "Anonymous"


def submit_score(username, score, level):
    try:
        payload = {
            "username": username,
            "score": score,
            "level": level
        }
        response = requests.post(API_ENDPOINT, json=payload, timeout=5)
        if response.status_code == 200:
            print("Score submitted successfully")
            return True
        else:
            print(f"Failed to submit score. Status code: {response.status_code}")
            return False
    except requests.RequestException as e:
        print(f"Error submitting score: {e}")
        return False


def main():
    username = get_username()
    tetris = Tetris(ROWS, COLS)
    space_pressed = False
    counter = 0
    move = True
    score_submitted = False

    run = True
    while run:
        SCREEN.fill(BG_COLOR)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                sys.exit()

            # event loop
            keys = pygame.key.get_pressed()
            if not tetris.end:
                if keys[pygame.K_LEFT]:
                    tetris.left()
                elif keys[pygame.K_RIGHT]:
                    tetris.right()
                elif keys[pygame.K_DOWN]:
                    tetris.move_down()
                elif keys[pygame.K_UP]:
                    tetris.rotate()
                elif keys[pygame.K_SPACE]:
                    space_pressed = True

            if keys[pygame.K_r]:
                tetris.__init__(ROWS, COLS)
                score_submitted = False

            if keys[pygame.K_ESCAPE] or keys[pygame.K_q]:
                run = False

        # constant rate block falling
        counter += 1
        if counter >= 15000:
            counter = 0

        if move:
            if counter % (FPS // (tetris.level * 1)) == 0:
                if not tetris.end:
                    if space_pressed:
                        tetris.freefall()
                        space_pressed = False
                    else:
                        tetris.move_down()

        tetris.make_grid()
        for x in range(ROWS):
            for y in range(COLS):
                if tetris.grid[x][y] > 0:
                    SCREEN.blit(ASSETS[tetris.grid[x][y]], (y * CELL, x * CELL))
                    pygame.draw.rect(SCREEN, WHITE, (y * CELL, x * CELL, CELL, CELL), 1)

        # show shapes
        if tetris.figure:
            for i in range(4):
                for j in range(4):
                    if (i * 4 + j) in tetris.figure.image():
                        shape = ASSETS[tetris.figure.color]
                        x = CELL * (tetris.figure.x + j)
                        y = CELL * (tetris.figure.y + i)
                        SCREEN.blit(shape, (x, y))
                        pygame.draw.rect(SCREEN, WHITE, (x, y, CELL, CELL), 1)

        # control panel
        if tetris.next:
            for i in range(4):
                for j in range(4):
                    if (i * 4 + j) in tetris.next.image():
                        SCREEN.blit(ASSETS[tetris.next.color],
                                    (CELL * (tetris.next.x + j - 4), HEIGHT - 100 + CELL * (tetris.next.y + i)))

        if tetris.end:
            if not score_submitted:
                submit_score(username, tetris.score, tetris.level)
                score_submitted = True
            tetris.end_game()

        score_text = font.render(f"{tetris.score}", True, WHITE)
        level_text = font2.render(f"level: {tetris.level}", True, WHITE)
        username_text = font2.render(f"Player: {username}", True, WHITE)

        SCREEN.blit(score_text, (250 - score_text.get_width() // 2, HEIGHT - 110))
        SCREEN.blit(level_text, (250 - level_text.get_width() // 2, HEIGHT - 30))
        SCREEN.blit(username_text, (10, HEIGHT - 20))

        pygame.display.update()
        clock.tick(FPS)


if __name__ == '__main__':
    main()
