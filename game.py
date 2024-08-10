import random
from player import Bird

class FlappyBirdGame:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.bird = Bird(self.width // 4, self.height // 2)
        self.pipes = []
        self.score = 0
        self.game_over = False

    def add_pipe(self):
        gap = 100
        pipe_height = random.randint(50, self.height - gap - 50)
        self.pipes.append([self.width, pipe_height])

    def update(self):
        if self.game_over:
            return

        self.bird.update()
        if self.bird.y > self.height or self.bird.y < 0:
            self.game_over = True

        for pipe in self.pipes:
            pipe[0] -= 5
            pipe_x, pipe_height = pipe
            if pipe_x < self.bird.x < pipe_x + 50:
                if self.bird.y < pipe_height or self.bird.y > pipe_height + 100:
                    self.game_over = True

        self.pipes = [pipe for pipe in self.pipes if pipe[0] > -50]

        if not self.game_over:
            self.score += 1

        if len(self.pipes) == 0 or self.pipes[-1][0] < self.width // 2:
            self.add_pipe()
