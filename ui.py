import tkinter as tk
from tkinter import simpledialog, messagebox
from game import TicTacToe
from player import HumanPlayer, ComputerPlayer
import requests

class TicTacToeGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Tic Tac Toe")
        self.api_url = "http://your-flask-api-url"  # Update with the actual API URL
        self.player_name = self.get_player_name()
        self.game = TicTacToe()
        self.x_player = HumanPlayer('X', self.player_name)
        self.o_player = ComputerPlayer('O')
        self.buttons = [[None for _ in range(3)] for _ in range(3)]
        self.create_widgets()
        self.play_game()

    def create_widgets(self):
        for row in range(3):
            for col in range(3):
                button = tk.Button(self.root, text='', width=10, height=3,
                                   command=lambda r=row, c=col: self.handle_click(r, c))
                button.grid(row=row, column=col)
                self.buttons[row][col] = button

    def handle_click(self, row, col):
        if self.game.board[row * 3 + col] == ' ' and self.game.current_winner is None:
            self.game.make_move(row * 3 + col, 'X')
            self.buttons[row][col].config(text='X')
            if self.game.current_winner:
                self.end_game(f'{self.player_name} (X) wins!')
                return
            elif not self.game.empty_squares():
                self.end_game('It\'s a tie!')
                return

            self.computer_move()
            if self.game.current_winner:
                self.end_game('Computer (O) wins!')
                return
            elif not self.game.empty_squares():
                self.end_game('It\'s a tie!')

    def computer_move(self):
        empty_squares = self.game.available_moves()
        move = random.choice(empty_squares)
        self.game.make_move(move, 'O')
        row, col = divmod(move, 3)
        self.buttons[row][col].config(text='O')

    def end_game(self, message):
        messagebox.showinfo("Game Over", message)
        if 'wins' in message:
            self.update_leaderboard(self.player_name)
        self.print_leaderboard()
        self.root.after(2000, self.reset_game)

    def reset_game(self):
        self.game = TicTacToe()
        for row in range(3):
            for col in range(3):
                self.buttons[row][col].config(text='')

    def get_player_name(self):
        name = simpledialog.askstring("Enter Username", "Please enter your name:", parent=self.root)
        if name:
            self.register_user(name)
            return name
        else:
            messagebox.showerror("Error", "Username is required to play the game.")
            self.root.quit()

    def register_user(self, username):
        try:
            response = requests.post(f"{self.api_url}/register", json={"username": username, "password": "defaultpassword"})
            if response.status_code == 201:
                messagebox.showinfo("Success", "User registered successfully.")
            elif response.status_code == 409:
                messagebox.showinfo("Info", "User already registered.")
            else:
                messagebox.showerror("Error", "Failed to register user.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def update_leaderboard(self, username):
        try:
            response = requests.post(f"{self.api_url}/update_leaderboard", json={"username": username})
            if response.status_code != 200:
                messagebox.showerror("Error", "Failed to update leaderboard.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def print_leaderboard(self):
        try:
            response = requests.get(f"{self.api_url}/leaderboard")
            if response.status_code == 200:
                leaderboard = response.json()
                leaderboard_text = "\n".join([f"{entry['username']}: {entry['wins']} wins" for entry in leaderboard])
                messagebox.showinfo("Leaderboard", leaderboard_text)
            else:
                messagebox.showerror("Error", "Failed to fetch leaderboard.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def play_game(self):
        self.root.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    app = TicTacToeGUI(root)
