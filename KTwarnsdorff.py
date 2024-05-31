import tkinter as tk
from tkinter import messagebox, ttk
import time
import threading

# Dimensi papan catur
N = 8

# Semua kemungkinan gerakan kuda
move_x = [2, 1, -1, -2, -2, -1, 1, 2]
move_y = [1, 2, 2, 1, -1, -2, -2, -1]

# Fungsi untuk mengecek apakah petak berada di dalam papan dan belum dikunjungi
def is_valid(x, y, board):
    return 0 <= x < N and 0 <= y < N and board[x][y] == -1

# Fungsi untuk menghitung derajat petak
def get_degree(x, y, board):
    count = 0
    for i in range(8):
        new_x, new_y = x + move_x[i], y + move_y[i]
        if is_valid(new_x, new_y, board):
            count += 1
    return count

# Algoritma Warnsdorff dengan perekaman langkah
def solve_knight_tour(start_x, start_y, update_text_callback):
    # Inisialisasi papan catur
    board = [[-1 for _ in range(N)] for _ in range(N)]
    board[start_x][start_y] = 0
    path = [(start_x, start_y)]

    def solve(x, y, movei):
        if movei == N * N:
            return True
        
        moves = []
        for i in range(8):
            new_x, new_y = x + move_x[i], y + move_y[i]
            if is_valid(new_x, new_y, board):
                degree = get_degree(new_x, new_y, board)
                moves.append((degree, new_x, new_y))
        
        # Sort the moves based on the degree heuristic
        moves.sort()

        for degree, new_x, new_y in moves:
            board[new_x][new_y] = movei
            path.append((new_x, new_y))
            update_text_callback(f"Step: {movei}\nMove to: ({new_x}, {new_y})")
            if solve(new_x, new_y, movei + 1):
                return True
            board[new_x][new_y] = -1  # Backtracking
            path.pop()
            update_text_callback(f"Backtrack from: ({new_x}, {new_y})")
            
        return False

    if solve(start_x, start_y, 1):
        return path
    else:
        return None

class KnightsTourApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Knight's Tour using Warnsdorff's Rule")
        self.board = [[None for _ in range(N)] for _ in range(N)]
        self.speed = 500  # Default speed in milliseconds
        self.solution_path = None
        self.animation_id = None
        self.create_widgets()
        
    def create_widgets(self):
        self.canvas = tk.Canvas(self.root, width=400, height=400)
        self.canvas.pack()
        
        control_frame = tk.Frame(self.root)
        control_frame.pack()
        
        self.start_button = tk.Button(control_frame, text="Start", command=self.start_tour)
        self.start_button.grid(row=0, column=0, padx=(0, 10))  # Add padding to the right of the Start button
        
        self.speed_label = tk.Label(control_frame, text="Speed (ms):")
        self.speed_label.grid(row=0, column=1, padx=(10, 0))  # Add padding to the left of the Speed label
        
        self.speed_var = tk.IntVar(value=self.speed)
        self.speed_scale = tk.Scale(control_frame, from_=100, to=2000, variable=self.speed_var, orient=tk.HORIZONTAL, command=self.update_speed)
        self.speed_scale.grid(row=0, column=2)
        
        self.time_label = tk.Label(self.root, text="Execution Time: 0 ms")
        self.time_label.pack()

        text_frame = tk.Frame(self.root)
        text_frame.pack()
        
        self.text_output = tk.Text(text_frame, height=10, width=50)
        self.text_output.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.scrollbar = tk.Scrollbar(text_frame, command=self.text_output.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.text_output.config(yscrollcommand=self.scrollbar.set)
        
        self.canvas.bind("<Button-1>", self.get_start_position)
        self.start_x, self.start_y = None, None
        self.draw_board()
    
    def draw_board(self):
        self.canvas.delete("all")
        self.rectangles = [[None for _ in range(N)] for _ in range(N)]
        for i in range(N):
            for j in range(N):
                color = "white" if (i + j) % 2 == 0 else "gray"
                x1, y1 = j * 50, i * 50
                x2, y2 = x1 + 50, y1 + 50
                self.rectangles[i][j] = self.canvas.create_rectangle(x1, y1, x2, y2, fill=color)
    
    def get_start_position(self, event):
        if self.animation_id is not None:
            self.root.after_cancel(self.animation_id)
            self.animation_id = None
        self.solution_path = None
        self.start_x, self.start_y = None, None
        self.draw_board()
        self.text_output.delete("1.0", tk.END)  # Clear the text output

        x, y = event.x // 50, event.y // 50
        self.start_x, self.start_y = y, x
        self.highlight_start_position()

    def highlight_start_position(self):
        self.draw_board()
        if self.start_x is not None and self.start_y is not None:
            x1, y1 = self.start_y * 50, self.start_x * 50
            x2, y2 = x1 + 50, y1 + 50
            self.canvas.create_rectangle(x1, y1, x2, y2, outline="red", width=3)

    def start_tour(self):
        if self.start_x is None or self.start_y is None:
            messagebox.showerror("Error", "Please select a start position.")
            return

        if self.animation_id is not None:
            self.root.after_cancel(self.animation_id)
            self.animation_id = None
        
        self.text_output.delete("1.0", tk.END)
        
        def run_solver():
            start_time = time.time()
            solution_path = solve_knight_tour(self.start_x, self.start_y, self.update_text_output)
            end_time = time.time()
            
            execution_time = int((end_time - start_time) * 1000)  # Convert to milliseconds
            self.root.after(0, self.update_execution_time, execution_time)
            self.root.after(0, self.process_solution, solution_path)

        solver_thread = threading.Thread(target=run_solver)
        solver_thread.start()
    
    def process_solution(self, solution_path):
        if solution_path:
            self.solution_path = solution_path
            self.speed = self.speed_var.get()
            self.animate_solution(0)
        else:
            messagebox.showerror("Error", "No solution found.")

    def animate_solution(self, step):
        if step < len(self.solution_path):
            x, y = self.solution_path[step]
            self.highlight_square(x, y, step)
            self.animation_id = self.root.after(self.speed, self.animate_solution, step + 1)

    def highlight_square(self, x, y, step):
        x1, y1 = y * 50, x * 50
        x2, y2 = x1 + 50, y1 + 50
        self.canvas.create_rectangle(x1, y1, x2, y2, fill="green" if step == 0 else "yellow", outline="black")
        self.canvas.create_text(x1 + 25, y1 + 25, text=str(step + 1), fill="black")

    def update_speed(self, value):
        self.speed = int(value)
    
    def update_text_output(self, message):
        self.root.after(0, self.append_text_output, message)

    def append_text_output(self, message):
        self.text_output.insert(tk.END, message + "\n")
        self.text_output.see(tk.END)
    
    def update_execution_time(self, execution_time):
        self.time_label.config(text=f"Execution Time: {execution_time} ms")

if __name__ == "__main__":
    root = tk.Tk()
    app = KnightsTourApp(root)
    root.mainloop()
