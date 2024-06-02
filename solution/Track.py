import numpy as np
from collections import deque
import math

class Track:
    directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def __init__(self, file_path):
        self.grid = self.load_track(file_path)
        self.distances = self.calculate_distances(self.grid)
        self.distances_to_object = self.calculate_distances_to_object(self.grid)
        self.longest_track = self.longest_consecutive_tracks(self.grid)
        self.recommended_max_speed = math.floor(math.sqrt(self.longest_track))

    # Loads track file
    def load_track(self, file_path):
        with open(file_path, 'r') as file:
            lines = file.readlines()

        list_of_lists = [list(line.strip()) for line in lines]
        array_2d = np.array(list_of_lists)

        return array_2d

    def longest_consecutive_tracks(self, matrix):
        def max_consecutive_in_line(line):
            max_count = 0
            current_count = 0
            for cell in line:
                if cell == 'T':
                    current_count += 1
                    max_count = max(max_count, current_count)
                else:
                    current_count = 0
            return max_count

        max_length = 0

        # Check rows
        for row in matrix:
            max_length = max(max_length, max_consecutive_in_line(row))

        # Check columns
        for col in matrix.T:
            max_length = max(max_length, max_consecutive_in_line(col))

        # Check diagonals
        def diagonals(matrix):
            # Get all diagonals from top-left to bottom-right
            for i in range(-matrix.shape[0] + 1, matrix.shape[1]):
                yield np.diagonal(matrix, offset=i)
            # Get all diagonals from top-right to bottom-left
            flipped_matrix = np.fliplr(matrix)
            for i in range(-flipped_matrix.shape[0] + 1, flipped_matrix.shape[1]):
                yield np.diagonal(flipped_matrix, offset=i)

        for diag in diagonals(matrix):
            max_length = max(max_length, max_consecutive_in_line(diag))

        return max_length

    # Calculates distance of every state to the finish via BFS
    def calculate_distances(self, grid):
        rows, cols = len(grid), len(grid[0])
        distance = [[float('inf')] * cols for _ in range(rows)]

        # Find all finish positions
        finish_positions = []
        for r in range(rows):
            for c in range(cols):
                if grid[r][c] == 'F':
                    finish_positions.append((r, c))
                    distance[r][c] = 0

        # Initialize BFS
        queue = deque(finish_positions)

        while queue:
            current_pos = queue.popleft()
            current_distance = distance[current_pos[0]][current_pos[1]]

            for direction in Track.directions:
                if direction in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
                    if self.grid[current_pos[0] + direction[0]][current_pos[1]] == 'O' or self.grid[current_pos[0]][current_pos[1] + direction[1]] == 'O':
                        continue

                new_r, new_c = current_pos[0] + direction[0], current_pos[1] + direction[1]

                if 0 <= new_r < rows and 0 <= new_c < cols and grid[new_r][new_c] != 'O':
                    new_distance = current_distance + 1
                    if new_distance < distance[new_r][new_c]:
                        distance[new_r][new_c] = new_distance
                        queue.append((new_r, new_c))

        return distance

    # Calculates distance of every state to the nearest object 'O' via BFS
    def calculate_distances_to_object(self, grid):
        rows, cols = len(grid), len(grid[0])
        distance = [[float('inf')] * cols for _ in range(rows)]

        # Find all object 'O' positions
        object_positions = []
        for r in range(rows):
            for c in range(cols):
                if grid[r][c] == 'O':
                    object_positions.append((r, c))
                    distance[r][c] = 0

        # Initialize BFS for each object 'O'
        for obj_pos in object_positions:
            queue = deque([obj_pos])
            visited = set([obj_pos])

            while queue:
                current_pos = queue.popleft()
                current_distance = distance[current_pos[0]][current_pos[1]]

                for direction in Track.directions:
                    new_r, new_c = current_pos[0] + direction[0], current_pos[1] + direction[1]

                    if 0 <= new_r < rows and 0 <= new_c < cols and grid[new_r][new_c] != 'O' and (new_r, new_c) not in visited:
                        new_distance = current_distance + 1
                        if new_distance < distance[new_r][new_c]:
                            distance[new_r][new_c] = new_distance
                            queue.append((new_r, new_c))
                            visited.add((new_r, new_c))

        # Scale down the distances inversely and rescale between 0 and 0.99
        max_distance = np.max(distance)
        min_distance = 1
        for r in range(rows):
            for c in range(cols):
                if grid[r][c] != 'O':
                    if distance[r][c] != 0:
                        distance[r][c] = 0.99 - (distance[r][c] - min_distance) / (max_distance - min_distance) * 0.99
                    else:
                        distance[r][c] = 0.99  # Assign 0.99 to squares right by an object

        return distance

    def print_distances(self):
        for row in self.distances:
            print(' '.join(f'{cell:4}' for cell in row))

    def is_valid_position(self, pos):
        rows, cols = len(self.grid), len(self.grid[0])
        r, c = pos
        return 0 <= r < rows and 0 <= c < cols and self.grid[r][c] != 'O'
