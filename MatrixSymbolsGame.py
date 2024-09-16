import pygame # type: ignore
import random
import time

# Initialize Pygame
pygame.init()

# Set up the display
width, height = 1920, 1080  # Adjust for your screen resolution
screen = pygame.display.set_mode((width, height), pygame.FULLSCREEN)
clock = pygame.time.Clock()

# Add this variable to track fullscreen state
is_fullscreen = True

# Colors
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)

# Speed control
MIN_SPEED = 1
MAX_SPEED = 5
speed_multiplier = 1.0

# Add this set to keep track of eliminated symbols
eliminated_symbols = set()

class MatrixChar:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.char = self.generate_char()
        self.speed = random.uniform(MIN_SPEED, MAX_SPEED)
        self.color = (0, random.randint(50, 255), 0)
        self.base_size = 14
        self.size = self.base_size
        self.rect = pygame.Rect(self.x, self.y, self.size, self.size)
        self.selected = False

    def generate_char(self):
        available_chars = [c for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()_+-=[]{}|;:,.<>?" if c not in eliminated_symbols]
        return random.choice(available_chars) if available_chars else ' '

    def move(self):
        self.y += self.speed * speed_multiplier
        if self.y > height:
            self.y = random.randint(-100, -20)
            self.x = random.randint(0, width)
            self.char = self.generate_char()
            self.selected = False
            self.size = self.base_size
        self.rect.topleft = (self.x, self.y)
        self.rect.width = self.size
        self.rect.height = self.size

    def draw(self):
        char_font = pygame.font.Font(None, self.size)
        char_surface = char_font.render(self.char, True, (255, 255, 0) if self.selected else self.color)
        screen.blit(char_surface, (self.x, self.y))

    def increase_size(self):
        self.size = int(self.base_size * 1.5)
        self.selected = True

    def adjust_size(self, factor):
        self.base_size = max(8, min(40, int(self.base_size * factor)))
        if not self.selected:
            self.size = self.base_size

def draw_stats(total_symbols, matched_symbols, elapsed_time, eliminated_symbols):
    stats_font = pygame.font.Font(None, 30)
    
    # Draw total symbols
    symbols_text = f"Symbols: {total_symbols}"
    symbols_surface = stats_font.render(symbols_text, True, (0, 255, 0))
    screen.blit(symbols_surface, (10, 10))
    
    # Draw matched symbols
    matched_text = f"Matched: {matched_symbols}"
    matched_surface = stats_font.render(matched_text, True, (0, 255, 0))
    screen.blit(matched_surface, (10, 40))
    
    # Draw timer
    minutes, seconds = divmod(int(elapsed_time), 60)
    timer_text = f"Time: {minutes:02d}:{seconds:02d}"
    timer_surface = stats_font.render(timer_text, True, (0, 255, 0))
    screen.blit(timer_surface, (width - 150, 10))

    # Draw eliminated symbols in the lower right corner
    eliminated_text = f"Eliminated: {', '.join(eliminated_symbols)}"
    eliminated_surface = stats_font.render(eliminated_text, True, (255, 0, 0))  # Red color for visibility
    eliminated_rect = eliminated_surface.get_rect(bottomright=(width - 10, height - 10))  # Positioning in the lower right corner
    screen.blit(eliminated_surface, eliminated_rect)

# Create matrix characters
matrix_chars = [MatrixChar(x, random.randint(-100, height)) for x in range(0, width, 14)]

# Main loop
running = True
paused = False
selected_char = None
matched_symbols = 0
start_time = time.time()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                speed_multiplier = min(speed_multiplier * 1.1, 2.0)
            elif event.key == pygame.K_DOWN:
                speed_multiplier = max(speed_multiplier / 1.1, 0.5)
            elif event.key == pygame.K_SPACE:
                paused = not paused
            elif event.key in (pygame.K_PLUS, pygame.K_KP_PLUS, pygame.K_EQUALS):  # Handle + key
                for char in matrix_chars:
                    char.adjust_size(1.1)
            elif event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):  # Handle - key
                for char in matrix_chars:
                    char.adjust_size(0.9)
            elif event.key == pygame.K_TAB:
                is_fullscreen = not is_fullscreen
                if is_fullscreen:
                    screen = pygame.display.set_mode((width, height), pygame.FULLSCREEN)
                else:
                    screen = pygame.display.set_mode((width, height))
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                for char in matrix_chars:
                    if char.rect.collidepoint(event.pos):
                        if selected_char is None:
                            char.increase_size()
                            selected_char = char
                            paused = True
                        elif char != selected_char and char.char == selected_char.char:
                            eliminated_symbols.add(char.char)  # Add the matched symbol to eliminated set
                            matrix_chars.remove(char)
                            matrix_chars.remove(selected_char)
                            selected_char = None
                            paused = False
                            matched_symbols += 2
                        else:
                            selected_char.selected = False
                            selected_char.size = selected_char.base_size
                            char.increase_size()
                            selected_char = char
                        break

    screen.fill(BLACK)

    if not paused:
        for char in matrix_chars:
            char.move()
    
    for char in matrix_chars:
        char.draw()

    total_symbols = len(matrix_chars)
    elapsed_time = time.time() - start_time
    draw_stats(total_symbols, matched_symbols, elapsed_time, eliminated_symbols)

    if total_symbols == 0:
        victory_font = pygame.font.Font(None, 72)
        victory_text = f"You won! Time: {int(elapsed_time)} seconds"
        victory_surface = victory_font.render(victory_text, True, (0, 255, 0))
        victory_rect = victory_surface.get_rect(center=(width // 2, height // 2))
        screen.blit(victory_surface, victory_rect)
        pygame.display.flip()
        pygame.time.wait(5000)  # Wait 5 seconds before closing
        running = False

    pygame.display.flip()
    clock.tick(30)

pygame.quit()