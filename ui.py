import tkinter as tk
from tkinter import simpledialog, messagebox
from game import FlappyBirdGame
import json
import os
import requests

class FlappyBirdGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Flappy Bird")
        
        # Set Minikube IP and API URL
        self.minikube_ip = "184.73.10.190:32469"  # Replace <your-minikube-ip> with your actual Minikube IP
        self.api_url = f"{self.minikube_ip}/api"

        # Prompt for username
        self.username = self.get_player_name()
        if not self.username:
            self.root.quit()  # Exit the game if no username is provided

        self.canvas = tk.Canvas(root, width=400, height=600, bg="skyblue")
        self.canvas.pack()
        self.game = FlappyBirdGame(400, 600)
        self.bird_image = self.canvas.create_oval(50, 300, 90, 340, fill="yellow")
        self.pipes = []
        self.root.bind("<space>", self.flap)
        self.update_game()

    def get_player_name(self):
        while True:
            name = simpledialog.askstring("Enter Username", "Please enter your name:", parent=self.root)
            if name and name.strip():  # Check if the name is not empty or just spaces
                self.register_user(name)
                return name
            else:
                messagebox.showerror("Error", "Username is required to play the game. Please enter a valid username.")

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

    def flap(self, event):
        self.game.bird.flap()

    def update_game(self):
        if self.game.game_over:
            self.canvas.create_text(200, 300, text="Game Over", font=('Helvetica', 30), fill="red")
            self.canvas.create_text(200, 340, text=f"Player: {self.username}", font=('Helvetica', 20), fill="white")
            self.canvas.create_text(200, 380, text=f"Score: {self.game.score}", font=('Helvetica', 20), fill="white")
            self.update_leaderboard(self.game.score)
            self.print_leaderboard()
            retry = messagebox.askyesno("Game Over", "Do you want to retry?")
            if retry:
                self.reset_game()
            else:
                self.root.quit()
            return

        # Update game logic
        self.game.update()

        # Update bird position on screen
        self.canvas.coords(self.bird_image, 50, self.game.bird.y, 90, self.game.bird.y + 40)

        # Clear old pipes
        for pipe in self.pipes:
            self.canvas.delete(pipe[0])
            self.canvas.delete(pipe[1])

        self.pipes.clear()

        # Draw new pipes
        for pipe_x, pipe_height in self.game.pipes:
            top_pipe = self.canvas.create_rectangle(pipe_x, 0, pipe_x + 50, pipe_height, fill="green")
            bottom_pipe = self.canvas.create_rectangle(pipe_x, pipe_height + 100, pipe_x + 50, 600, fill="green")
            self.pipes.append((top_pipe, bottom_pipe))

        # Call update_game again after a short delay
        self.root.after(30, self.update_game)

    def update_leaderboard(self, score):
        leaderboard_file = "leaderboard.json"
        
        # Load existing leaderboard
        if os.path.exists(leaderboard_file):
            with open(leaderboard_file, "r") as f:
                leaderboard = json.load(f)
        else:
            leaderboard = {}

        # Update user's score
        if self.username in leaderboard:
            leaderboard[self.username] = max(leaderboard[self.username], score)
        else:
            leaderboard[self.username] = score

        # Save updated leaderboard
        with open(leaderboard_file, "w") as f:
            json.dump(leaderboard, f)

    def print_leaderboard(self):
        leaderboard_file = "leaderboard.json"
        
        if os.path.exists(leaderboard_file):
            with open(leaderboard_file, "r") as f:
                leaderboard = json.load(f)
            
            # Sort the leaderboard by scores in descending order
            sorted_leaderboard = sorted(leaderboard.items(), key=lambda item: item[1], reverse=True)

            leaderboard_text = "\n".join([f"{user}: {score} points" for user, score in sorted_leaderboard])
            messagebox.showinfo("Leaderboard", leaderboard_text)
        else:
            messagebox.showinfo("Leaderboard", "No leaderboard data available.")

    def reset_game(self):
        # Reset the game state and start a new game
        self.game = FlappyBirdGame(400, 600)
        self.canvas.delete("all")
        self.bird_image = self.canvas.create_oval(50, 300, 90, 340, fill="yellow")
        self.pipes = []
        self.update_game()

if __name__ == "__main__":
    root = tk.Tk()
    app = FlappyBirdGUI(root)
    root.mainloop()
