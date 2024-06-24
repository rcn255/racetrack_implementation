import tkinter as tk
import matplotlib.pyplot as plt
import numpy as np

class Race:
    def __init__(self, racecar, track, name='Grand Prix',
                 draw_last_possible_moves=1, draw_racecar_path=1, draw_distances=1, draw_indices=1, draw_best_path=1):
        self.name = name
        self.track = track
        self.racecar = racecar
        self.time = None
        self.draw_last_possible_moves = draw_last_possible_moves
        self.draw_racecar_path = draw_racecar_path
        self.draw_distances = draw_distances
        self.draw_indices = draw_indices
        self.draw_best_path = draw_best_path
        self.cell_size = 15

    def save_trip(self, filename):
        with open(filename, 'w') as file:
            for i, j in self.translate_positions(self.racecar.pos_hist):
                file.write(f"{i}, {j}\n")

    def translate_positions(self, pos_list):
        num_rows = len(self.track.grid)
        translated_pos_list = []
        for x, y in pos_list:
            translated_x = num_rows - 1 - x
            translated_pos_list.append((y, translated_x))
        return translated_pos_list

    def make_move_and_refresh(self, canvas):
        self.racecar.make_move()

        if self.draw_indices:
            self.draw_indices_f(canvas)

        self.draw_track(canvas)

        if self.draw_racecar_path:
            self.draw_racecar_path_f(canvas)
        if self.draw_best_path and self.racecar.best_path is not None:
            self.draw_best_path_f(canvas)
        if self.draw_last_possible_moves:
            self.draw_last_possible_moves_f(canvas)

    def draw_indices_f(self, canvas):
        for i in range(len(self.track.grid)):
            canvas.create_text(self.cell_size // 2, (i + 1.5) * self.cell_size, text=str(i), anchor='e')
        for j in range(len(self.track.grid[0])):
            canvas.create_text((j + 1.5) * self.cell_size, self.cell_size // 2, text=str(j), anchor='s')

    def draw_track(self, canvas):
        COLORS = {
            'T': 'lightgrey',
            'S': 'yellow',
            'F': 'blue',
            'O': 'black',
            'G': 'green'
        }
        for i, row in enumerate(self.track.grid):
            for j, cell in enumerate(row):
                color = COLORS.get(cell, 'white')
                x1, y1 = (j + 1) * self.cell_size, (i + 1) * self.cell_size
                x2, y2 = x1 + self.cell_size, y1 + self.cell_size
                canvas.create_rectangle(x1, y1, x2, y2, fill=color)
                if cell in 'SF':
                    canvas.create_text((x1 + x2) // 2, (y1 + y2) // 2, text=cell, fill='white')

                if self.draw_distances:
                    number = self.track.distances[i][j]
                    canvas.create_text(x1 + 5, y1 + 5, text=str(number), fill='white', anchor='nw', font=('Helvetica', 5))

    def draw_racecar_path_f(self, canvas):
        for k, (x, y) in enumerate(self.racecar.pos_hist):
            x_center = (y + 1.5) * self.cell_size
            y_center = (x + 1.5) * self.cell_size
            canvas.create_oval(x_center - 5, y_center - 5, x_center + 5, y_center + 5, fill='red')
            canvas.create_text(x_center, y_center, text=str(k), fill='cyan')

            if k < len(self.racecar.pos_hist) - 1:
                x_next_center = (self.racecar.pos_hist[k + 1][1] + 1.5) * self.cell_size
                y_next_center = (self.racecar.pos_hist[k + 1][0] + 1.5) * self.cell_size
                canvas.create_line(x_center, y_center, x_next_center, y_next_center, fill='red', width=3)

    def draw_best_path_f(self, canvas):
        for k, (x, y) in enumerate(self.racecar.best_path[1:], start=1):
            x_center = (y + 1.5) * self.cell_size
            y_center = (x + 1.5) * self.cell_size
            canvas.create_oval(x_center - 3, y_center - 3, x_center + 3, y_center + 3, fill='blue')
            canvas.create_text(x_center, y_center, text=str(k), fill='white')

            if k < len(self.racecar.best_path) - 1:
                x_next_center = (self.racecar.best_path[k + 1][1] + 1.5) * self.cell_size
                y_next_center = (self.racecar.best_path[k + 1][0] + 1.5) * self.cell_size
                canvas.create_line(x_center, y_center, x_next_center, y_next_center, fill='blue', width=2)

    def draw_last_possible_moves_f(self, canvas):
        for move in self.racecar.calculate_possible_pos(self.racecar.pos, self.racecar.inertia):
            x, y = move
            x_center = (y + 1.5) * self.cell_size
            y_center = (x + 1.5) * self.cell_size
            canvas.create_oval(x_center - 2, y_center - 2, x_center + 2, y_center + 2, fill='yellow')

    def draw_race(self):
        root = tk.Tk()
        root.title(self.name)

        width = (len(self.track.grid[0]) + 1) * self.cell_size
        height = (len(self.track.grid) + 1) * self.cell_size

        canvas = tk.Canvas(root, width=width, height=height)
        canvas.pack()

        if self.draw_indices:
            self.draw_indices_f(canvas)

        self.draw_track(canvas)
        if self.draw_racecar_path:
            self.draw_racecar_path_f(canvas)
        if self.draw_best_path and self.racecar.best_path is not None:
            self.draw_best_path_f(canvas)
        if self.draw_last_possible_moves:
            self.draw_last_possible_moves_f(canvas)

        button = tk.Button(root, text="Make Move", command=lambda: self.make_move_and_refresh(canvas))
        button.pack()

        root.mainloop()

    def draw_multiple_paths(self, paths):
        root = tk.Tk()
        root.title(f"{self.name} - Multiple Paths")

        width = (len(self.track.grid[0]) + 1) * self.cell_size
        height = (len(self.track.grid) + 1) * self.cell_size

        canvas = tk.Canvas(root, width=width, height=height)
        canvas.pack()

        if self.draw_indices:
            self.draw_indices_f(canvas)

        self.draw_track(canvas)

        # Use a colormap to dynamically generate colors based on the number of paths
        num_paths = len(paths)
        colors = plt.cm.get_cmap('Wistia', num_paths)

        for idx, path in enumerate(paths):
            translated_path = path
            color = colors(idx)[:3]  # Extract RGB components
            color = "#{:02x}{:02x}{:02x}".format(int(color[0]*255), int(color[1]*255), int(color[2]*255))  # Convert to hexadecimal
            for k, (x, y) in enumerate(translated_path):
                x_center = (y + 1.5) * self.cell_size
                y_center = (x + 1.5) * self.cell_size
                canvas.create_oval(x_center - 3, y_center - 3, x_center + 3, y_center + 3, fill=color)
                canvas.create_text(x_center, y_center, text=str(k), fill='white')

                if k < len(translated_path) - 1:
                    x_next_center = (translated_path[k + 1][1] + 1.5) * self.cell_size
                    y_next_center = (translated_path[k + 1][0] + 1.5) * self.cell_size
                    canvas.create_line(x_center, y_center, x_next_center, y_next_center, fill=color, width=2)

        root.mainloop()
