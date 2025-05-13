import numpy as np
import pygame
import sys
from ortools.sat.python import cp_model
import time
import random

# Constants
WIDTH, HEIGHT = 540, 620
GRID_SIZE = 9
CELL_SIZE = WIDTH // GRID_SIZE
WHITE = (255, 255, 255)
BLACK = (30, 30, 30)
GRAY = (220, 220, 220)
BLUE = (0, 100, 255)
GREEN = (0, 180, 100)
RED = (255, 50, 50)
LIGHT_YELLOW = (255, 255, 204)
FONT_SIZE = 36

pygame.init()
pygame.font.init()

def generate_random_sudoku():
    board = [[0 for _ in range(9)] for _ in range(9)]

    def is_valid(num, row, col):
        for i in range(9):
            if board[row][i] == num or board[i][col] == num:
                return False
        box_start_row, box_start_col = 3 * (row // 3), 3 * (col // 3)
        for r in range(box_start_row, box_start_row + 3):
            for c in range(box_start_col, box_start_col + 3):
                if board[r][c] == num:
                    return False
        return True

    def fill_board():
        for i in range(9):
            for j in range(9):
                if board[i][j] == 0:
                    nums = list(range(1, 10))
                    random.shuffle(nums)
                    for num in nums:
                        if is_valid(num, i, j):
                            board[i][j] = num
                            if fill_board():
                                return True
                            board[i][j] = 0
                    return False
        return True

    def remove_numbers(count=45):
        removed = 0
        while removed < count:
            row = random.randint(0, 8)
            col = random.randint(0, 8)
            if board[row][col] != 0:
                board[row][col] = 0
                removed += 1

    fill_board()
    remove_numbers()
    return board

class AnimatedSudokuSolver(cp_model.CpSolverSolutionCallback):
    def __init__(self, vars, gui):
        super().__init__()
        self.vars = vars
        self.gui = gui
        self.solution_found = False
        self.board = [[0 for _ in range(9)] for _ in range(9)]

    def on_solution_callback(self):
        for r in range(9):
            for c in range(9):
                self.board[r][c] = self.Value(self.vars[r][c])
                self.gui.update_cell(r, c, self.board[r][c])
                self.gui.draw_board()
                pygame.time.delay(25)
        self.solution_found = True

class SudokuGUI:
    def __init__(self, board):
        self.original_board = board
        self.board = [row[:] for row in board]
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("🎉 Animated Sudoku Solver")
        self.font = pygame.font.SysFont('Comic Sans MS', FONT_SIZE)
        self.small_font = pygame.font.SysFont('Comic Sans MS', 24)
        self.solve_button = pygame.Rect(WIDTH // 2 - 150, HEIGHT - 60, 140, 45)
        self.new_button = pygame.Rect(WIDTH // 2 + 10, HEIGHT - 60, 140, 45)
        self.solved = False
        self.solving = False

    def update_cell(self, row, col, value):
        if self.original_board[row][col] == 0:
            self.board[row][col] = value

    def draw_board(self):
        self.screen.fill(LIGHT_YELLOW)

        for i in range(GRID_SIZE + 1):
            width = 3 if i % 3 == 0 else 1
            pygame.draw.line(self.screen, BLACK, (0, i * CELL_SIZE), (WIDTH, i * CELL_SIZE), width)
            pygame.draw.line(self.screen, BLACK, (i * CELL_SIZE, 0), (i * CELL_SIZE, WIDTH), width)

        for row in range(9):
            for col in range(9):
                num = self.board[row][col]
                if num != 0:
                    color = BLACK if self.original_board[row][col] != 0 else BLUE
                    text = self.font.render(str(num), True, color)
                    x = col * CELL_SIZE + (CELL_SIZE - text.get_width()) // 2
                    y = row * CELL_SIZE + (CELL_SIZE - text.get_height()) // 2
                    self.screen.blit(text, (x, y))

        mouse = pygame.mouse.get_pos()
        solve_color = GREEN if self.solve_button.collidepoint(mouse) else GRAY
        new_color = GREEN if self.new_button.collidepoint(mouse) else GRAY
        pygame.draw.rect(self.screen, solve_color, self.solve_button, border_radius=10)
        pygame.draw.rect(self.screen, new_color, self.new_button, border_radius=10)

        solve_text = self.small_font.render("Solve Puzzle", True, BLACK)
        solve_x = self.solve_button.x + (self.solve_button.width - solve_text.get_width()) // 2
        solve_y = self.solve_button.y + (self.solve_button.height - solve_text.get_height()) // 2
        self.screen.blit(solve_text, (solve_x, solve_y))

        new_text = self.small_font.render("New Puzzle", True, BLACK)
        new_x = self.new_button.x + (self.new_button.width - new_text.get_width()) // 2
        new_y = self.new_button.y + (self.new_button.height - new_text.get_height()) // 2
        self.screen.blit(new_text, (new_x, new_y))

        status = "Click Solve to begin!"
        if self.solving:
            status = "Solving..."
        elif self.solved:
            if pygame.time.get_ticks() % 1000 < 500:
                status = "🎉 Solved! 🎉"
            else:
                status = ""
        status_text = self.small_font.render(status, True, RED)
        self.screen.blit(status_text, (20, HEIGHT - 30))

        pygame.display.flip()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.solve_button.collidepoint(event.pos) and not self.solving:
                    self.solving = True
                    return "solve"
                elif self.new_button.collidepoint(event.pos):
                    return "new"
        return None

def solve_with_animation(board, gui):
    model = cp_model.CpModel()
    cells = [[model.NewIntVar(1, 9, f'cell_{r}_{c}') for c in range(9)] for r in range(9)]

    for r in range(9):
        for c in range(9):
            if board[r][c] != 0:
                model.Add(cells[r][c] == board[r][c])

    for i in range(9):
        model.AddAllDifferent(cells[i])
        model.AddAllDifferent([cells[r][i] for r in range(9)])

    for br in range(0, 9, 3):
        for bc in range(0, 9, 3):
            box = [cells[r][c] for r in range(br, br + 3) for c in range(bc, bc + 3)]
            model.AddAllDifferent(box)

    solver = AnimatedSudokuSolver(cells, gui)
    cp_solver = cp_model.CpSolver()
    cp_solver.parameters.enumerate_all_solutions = False
    cp_solver.Solve(model, solver)

    gui.board = solver.board
    return solver.solution_found

def main():
    board = generate_random_sudoku()
    gui = SudokuGUI(board)

    while True:
        action = gui.handle_events()
        gui.draw_board()

        if action == "solve" and not gui.solved:
            if solve_with_animation(gui.board, gui):
                gui.solved = True
            else:
                print("No solution found.")
            gui.solving = False

        elif action == "new":
            board = generate_random_sudoku()
            gui = SudokuGUI(board)

        pygame.time.delay(50)

if __name__ == "__main__":
    main()
