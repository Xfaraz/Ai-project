Animated Sudoku Solver with Pygame & OR-Tools

This is an interactive animated Sudoku solver built using Python, Pygame, and Google OR-Tools. It features a graphical user interface, animated solving process, and the ability to generate new random puzzles.

Features:
- Random Sudoku puzzle generation
- Constraint Programming-based solver using Google OR-Tools
- Real-time animated solving visualization
- Simple and intuitive Pygame-based interface
- Buttons to solve the current puzzle or generate a new one

Requirements:
- Python 3.7 or higher
- Pygame
- numpy
- ortools

To install dependencies:
pip install pygame numpy ortools

To run the program:
python sudoku_solver.py

- Click “Solve Puzzle” to start the animated solving.
- Click “New Puzzle” to generate a new puzzle.

How it works:
- A valid Sudoku board is filled randomly and numbers are removed to create a puzzle.
- The puzzle is solved using OR-Tools with constraint satisfaction techniques.
- The GUI updates in real-time to show the progress of the solver.

This project is ideal for demonstrating how constraint programming can be applied to classic logic puzzles like Sudoku.
