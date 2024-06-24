import numpy as np
import math
import random
from collections import deque
from bresenham import bresenham

class RaceCarStochastic:

    def __init__(self, track, max_depth=1, strategy='fo', max_speed=7, always_moving=1, speed_importance=5, seed=42, random_cost=0, backtrack=0):
        self.track = track
        self.start_pos = self.find_letter_indices('S')
        self.end_pos = self.find_letter_indices('F')
        self.pos = self.start_pos[0]
        self.inertia = (0, 0)
        self.pos_hist = [self.start_pos[0]]
        self.max_depth = max_depth
        self.init_max_depth = max_depth
        self.max_speed = max_speed
        self.strategy = strategy
        self.speed_importance = speed_importance # = k for logistic_function
        self.always_moving = always_moving
        self.best_path = [self.start_pos[0]]
        self.random_cost = random_cost
        self.random_weights = [0.8, 0.1, 0.05, 0.03, 0.02]
        self.backtrack = backtrack
        self.current_backtracks = 0

        random.seed(seed)

    def complete_moves(self):
        try:
            while self.pos not in self.end_pos:
                self.make_move()
        except Exception as e:
            print("Crashed:", e)
            if self.backtrack and self.current_backtracks < 1000  and len(self.pos_hist) > 3:
                self.current_backtracks += 1
                #print("Backtracking")
                self.pos_hist.pop()
                self.pos_hist.pop()
                self.pos = self.pos_hist[-1]
                previous_pos = self.pos_hist[-2]
                self.inertia = (self.pos[0] - previous_pos[0], self.pos[1] - previous_pos[1])
                self.complete_moves()

            return 1  # Crashed

    def make_move(self):
        if random.random() < 0.1:  # 10% probability to make a random move
            new_pos = self.random_move()
        else:
            new_pos = self.find_next_pos(self.pos, self.inertia)

        #print(f"{len(self.pos_hist)} {new_pos}")
        self.inertia = (new_pos[0] - self.pos[0], new_pos[1] - self.pos[1])
        #print(f"max inertia: {self.max_inertia(self.inertia)}")

        if self.max_inertia(self.inertia) > self.max_speed * 3/4:
            self.max_depth = self.init_max_depth
        else:
            self.max_depth = self.init_max_depth
        #print(f"Max depth: {self.max_depth}")

        self.pos = new_pos
        self.pos_hist.append(new_pos)

    def random_move(self):
        current_tries = 0
        possible_positions = self.calculate_possible_pos(self.pos, self.inertia)
        next_pos = random.choice(possible_positions) if possible_positions else self.pos
        while self.is_valid_path(self.pos, next_pos) == False and current_tries < 20:
            next_pos = random.choice(possible_positions) if possible_positions else self.pos
            current_tries += 1
        if self.is_valid_path(self.pos, next_pos) == False:
            raise Exception("No available moves")
        return next_pos

    def find_next_pos(self, start_pos, start_inertia):
        queue = deque([([start_pos], start_inertia, 0)])
        best_path = None
        best_inertia = None
        best_eval = np.inf
        best_depth = np.inf

        while queue:
            current_path, current_inertia, depth = queue.popleft()
            current_pos = current_path[-1]

            if depth == self.max_depth or self.track.grid[current_pos[0]][current_pos[1]] == 'F':
                eval_pos = self.evaluate_pos(current_pos, current_inertia)
                # print(current_path)
                # print(eval_pos)
                if eval_pos < best_eval:
                    best_path = current_path
                    best_inertia = current_inertia
                    best_eval = eval_pos
                    best_depth = depth
                elif eval_pos == best_eval and depth < best_depth:
                    best_path = current_path
                    best_inertia = current_inertia
                    best_eval = eval_pos
                    best_depth = depth
                elif (eval_pos == best_eval and depth == best_depth and
                self.evaluate_pos(current_path[1], (current_path[1][0] - current_path[0][0], current_path[1][1] - current_path[0][1])) < self.evaluate_pos(best_path[1], (best_path[1][0] - best_path[0][0], best_path[1][1] - best_path[0][1]))):
                    #print('yes')
                    best_path = current_path
                    best_inertia = current_inertia
                    best_eval = eval_pos
                    best_depth = depth
                elif eval_pos == best_eval and depth == best_depth and self.max_inertia(current_inertia) > self.max_inertia(best_inertia):
                    best_path = current_path
                    best_inertia = current_inertia
                    best_eval = eval_pos
                    best_depth = depth
            elif current_pos in current_path[:-1]:
                continue
            else:
                possible_positions = self.calculate_possible_pos(current_pos, current_inertia)
                current_eval = self.evaluate_pos(current_pos, current_inertia)
                for next_pos in possible_positions:
                    if (self.is_valid_path(current_pos, next_pos) and
                    self.evaluate_pos(next_pos, (next_pos[0] - current_pos[0], next_pos[1] - current_pos[1])) < current_eval):
                        next_inertia = (next_pos[0] - current_pos[0], next_pos[1] - current_pos[1])
                        next_path = current_path + [next_pos]
                        queue.append((next_path, next_inertia, depth + 1))
        # print(best_path)
        # print(best_eval)
        self.best_path = best_path
        return best_path[1] if best_path and len(best_path) > 1 else None

    def is_valid_position(self, pos):
        return 0 <= pos[0] < len(self.track.grid) and 0 <= pos[1] < len(self.track.grid[0]) and self.track.grid[pos[0]][pos[1]] != 'O'

    def is_valid_path(self, start_pos, end_pos):
        if self.is_valid_position(start_pos) and self.is_valid_position(end_pos) and (abs(start_pos[0] - end_pos[0]) < self.max_speed + 1) and (abs(start_pos[1] - end_pos[1]) < self.max_speed + 1):
            pos_inbetween = list(set(self.raytrace(start_pos, end_pos) + self.raytrace(end_pos, start_pos)))
            # print(f"start_pos: {start_pos}")
            # print(f"end_pos: {end_pos}")
            # print(f"pos_inbetween: {pos_inbetween}")
            for pos in pos_inbetween:
                if self.track.grid[pos[0]][pos[1]] == 'O':
                    return False
            return True
        else:
            return False

    def raytrace(self, start_pos, end_pos):
        # https://playtechs.blogspot.com/2007/03/raytracing-on-grid.html
        x0, y0 = start_pos
        x1, y1 = end_pos
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        x = x0
        y = y0
        n = 1 + dx + dy
        x_inc = 1 if x1 > x0 else -1
        y_inc = 1 if y1 > y0 else -1
        error = dx - dy
        dx *= 2
        dy *= 2
        line = []

        for _ in range(n):
            line.append((x, y))

            if error >= 0:
                x += x_inc
                error -= dy
            else:
                y += y_inc
                error += dx
        return line

    def calculate_possible_pos(self, pos, inertia):
        possible_pos = []
        if self.track.grid[pos[0]][pos[1]] == 'T' or self.track.grid[pos[0]][pos[1]] == 'S':
            for direction in self.track.directions:
                possible_pos.append((pos[0] + inertia[0] + direction[0], pos[1] + inertia[1] + direction[1]))
        elif self.track.grid[pos[0]][pos[1]] == 'G':
            if inertia in self.track.directions:
                for direction in self.track.directions:
                    possible_pos.append((pos[0] + direction[0], pos[1] + direction[1]))
            else:
                slow_inertia = self.slow_inertia(inertia)
                possible_pos.append((pos[0] + slow_inertia[0], pos[1] + slow_inertia[1]))

        if self.always_moving and pos in possible_pos:
            possible_pos.remove(pos)
        return possible_pos

    def calculate_all_possible_pos(self, pos, inertia):
        possible_pos = []
        if self.track.grid[pos[0]][pos[1]] == 'T' or self.track.grid[pos[0]][pos[1]] == 'S':
            for direction in self.track.directions:
                possible_pos.append((pos[0] + inertia[0] + direction[0], pos[1] + inertia[1] + direction[1]))
        elif self.track.grid[pos[0]][pos[1]] == 'G':
            if inertia in self.track.directions:
                for direction in self.track.directions:
                    possible_pos.append((pos[0] + direction[0], pos[1] + direction[1]))
            else:
                slow_inertia = self.slow_inertia(inertia)
                possible_pos.append((pos[0] + slow_inertia[0], pos[1] + slow_inertia[1]))

        return possible_pos

    def slow_inertia(self, inertia):
        slow_inertia = tuple(x + 1 if x < -1 else x - 1 if x > 1 else x for x in inertia)
        return slow_inertia

    def find_letter_indices(self, letter):
        indices = []
        for i, row in enumerate(self.track.grid):
            for j, cell in enumerate(row):
                if cell == letter:
                    indices.append((i, j))
        return indices

    def evaluate_pos(self, pos, inertia):
        if self.strategy == 'f':
            if self.is_valid_position(pos):
                if self.random_cost:
                    delta = random.choices([0, 1, 2, 3, 4], weights=self.random_weights)[0]
                    cost = k.distances[pos[0]][pos[1]] + delta
                else:
                    cost = k.distances[pos[0]][pos[1]]
                return cost
            else:
                return np.inf
        elif self.strategy == 'fo':
            if self.is_valid_position(pos):
                if self.random_cost:
                    delta = random.choices([0, 1, 2, 3, 4], weights=self.random_weights)[0]
                    cost = self.track.distances[pos[0]][pos[1]] + self.track.distances_to_object[pos[0]][pos[1]] + delta
                else:
                    cost = self.track.distances[pos[0]][pos[1]] + self.track.distances_to_object[pos[0]][pos[1]]
                return cost
            else:
                return np.inf
        else:
            if self.random_cost:
                delta = random.choices([0, 1, 2, 3, 4], weights=self.random_weights)[0]
                cost = self.track.distances[pos[0]][pos[1]] + self.track.distances_to_object[pos[0]][pos[1]] - self.logistic_function(self.max_inertia(inertia)) + delta
            else:
                cost = self.track.distances[pos[0]][pos[1]] + self.track.distances_to_object[pos[0]][pos[1]] - self.logistic_function(self.max_inertia(inertia))
            return cost

    def logistic_function(self, x):
        return 1 / (1 + np.exp(-self.speed_importance * (x - (self.max_speed / 2))))

    def max_inertia(self, inertia):
        return max(abs(inertia[0]), abs(inertia[1]))
