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
        self.minikube_ip = "http://184.73.10.190:32469"  # Replace <your-minikube-ip> with your actual Minikube IP
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
                messagebox.showerror("Error", f"Failed to register user: {response.status_code} - {response.text}")
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
        try:
            response = requests.post(f"{self.api_url}/update_leaderboard", json={"username": self.username, "score": score})
            if response.status_code == 200:
                messagebox.showinfo("Success", "Leaderboard updated successfully.")
            else:
                messagebox.showerror("Error", f"Failed to update leaderboard: {response.status_code} - {response.text}")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while updating the leaderboard: {e}")

    def print_leaderboard(self):
        try:
            response = requests.get(f"{self.api_url}/leaderboard")
            if response.status_code == 200:
                leaderboard = response.json()
                leaderboard_text = "\n".join([f"{user['username']}: {user['wins']} points" for user in leaderboard])
                messagebox.showinfo("Leaderboard", leaderboard_text)
            else:
                messagebox.showerror("Error", f"Failed to retrieve leaderboard: {response.status_code} - {response.text}")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while retrieving the leaderboard: {e}")

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
