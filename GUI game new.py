import tkinter as tk
from tkinter import messagebox, simpledialog
import random
import time

class Board:
    def __init__(self, dim_size, num_bombs):
        self.dim_size = dim_size
        self.num_bombs = num_bombs
        self.board = self.make_new_board()
        self.assign_values_to_board()
        self.dug = set()

    def make_new_board(self):
        board = [[None for _ in range(self.dim_size)] for _ in range(self.dim_size)]
        bombs_planted = 0
        while bombs_planted < self.num_bombs:
            loc = random.randint(0, self.dim_size**2 - 1)
            row = loc // self.dim_size
            col = loc % self.dim_size

            if board[row][col] == '*':
                continue

            board[row][col] = '*'
            bombs_planted += 1

        return board

    def assign_values_to_board(self):
        for r in range(self.dim_size):
            for c in range(self.dim_size):
                if self.board[r][c] == '*':
                    continue
                self.board[r][c] = self.get_num_neighboring_bombs(r, c)

    def get_num_neighboring_bombs(self, row, col):
        num_neighboring_bombs = 0
        for r in range(max(0, row-1), min(self.dim_size-1, row+1)+1):
            for c in range(max(0, col-1), min(self.dim_size-1, col+1)+1):
                if r == row and c == col:
                    continue
                if self.board[r][c] == '*':
                    num_neighboring_bombs += 1
        return num_neighboring_bombs

    def dig(self, row, col):
        self.dug.add((row, col))
        if self.board[row][col] == '*':
            return False
        elif self.board[row][col] > 0:
            return True

        for r in range(max(0, row-1), min(self.dim_size-1, row+1)+1):
            for c in range(max(0, col-1), min(self.dim_size-1, col+1)+1):
                if (r, c) in self.dug:
                    continue
                self.dig(r, c)
        return True


class MinesweeperGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Minesweeper")
        self.dim_size = 10
        self.num_bombs = 10
        self.board = None
        self.buttons = {}
        self.start_time = None
        self.create_widgets()
        self.show_setup_dialog()
        self.new_game()

    def create_widgets(self):
        self.top_frame = tk.Frame(self.root)
        self.top_frame.pack(pady=10)

        self.status_label = tk.Label(self.top_frame, text="Welcome to Minesweeper!", font=("Helvetica", 14))
        self.status_label.pack(side=tk.LEFT, padx=10)

        self.new_game_button = tk.Button(self.top_frame, text="New Game", command=self.show_setup_dialog)
        self.new_game_button.pack(side=tk.RIGHT, padx=10)

        self.frame = tk.Frame(self.root)
        self.frame.pack()

    def show_setup_dialog(self):
        dim_size = simpledialog.askinteger("Input", "Enter the board size (default 10):", initialvalue=10, minvalue=2)
        num_bombs = simpledialog.askinteger("Input", "Enter the number of bombs (default 10):", initialvalue=10, minvalue=1)

        if dim_size is not None and num_bombs is not None:
            self.dim_size = dim_size
            self.num_bombs = min(num_bombs, dim_size * dim_size - 1)  # Ensure the number of bombs is valid
            self.new_game()

    def new_game(self):
        if self.board:
            for button in self.buttons.values():
                button.destroy()

        self.board = Board(self.dim_size, self.num_bombs)
        self.buttons = {}
        for r in range(self.dim_size):
            for c in range(self.dim_size):
                button = tk.Button(self.frame, text="", width=3, height=1, font=("Helvetica", 12),
                                   command=lambda row=r, col=c: self.on_button_click(row, col))
                button.grid(row=r, column=c, padx=1, pady=1)
                self.buttons[(r, c)] = button

        self.update_buttons()
        self.status_label.config(text="Game in progress...")
        self.start_time = time.time()

    def update_buttons(self):
        for (r, c), button in self.buttons.items():
            if (r, c) in self.board.dug:
                if self.board.board[r][c] == '*':
                    button.config(text='*', bg='red')
                else:
                    button.config(text=str(self.board.board[r][c]), bg='lightgrey')
            else:
                button.config(text='', bg='SystemButtonFace')

    def on_button_click(self, row, col):
        if not self.start_time:
            self.start_time = time.time()

        if (row, col) in self.board.dug:
            return

        safe = self.board.dig(row, col)
        self.update_buttons()

        if not safe:
            self.status_label.config(text="SORRY, YOU HIT A BOMB! GAME OVER!")
            self.game_over(False)
        elif len(self.board.dug) == self.dim_size ** 2 - self.num_bombs:
            self.status_label.config(text="CONGRATULATIONS! YOU WIN!")
            self.game_over(True)

    def game_over(self, won):
        for (r, c), button in self.buttons.items():
            if (r, c) not in self.board.dug:
                self.board.dig(r, c)
        self.update_buttons()
        end_time = time.time()
        elapsed_time = end_time - self.start_time

        if won:
            messagebox.showinfo("Game Over", "CONGRATULATIONS! YOU WIN!")
        else:
            messagebox.showinfo("Game Over", "SORRY, YOU HIT A BOMB! GAME OVER!")

        restart = messagebox.askyesno("Restart", "Do you want to start a new game?")
        if restart:
            self.show_setup_dialog()
        else:
            self.root.destroy()


if __name__ == '__main__':
    root = tk.Tk()
    game = MinesweeperGUI(root)
    root.mainloop()
