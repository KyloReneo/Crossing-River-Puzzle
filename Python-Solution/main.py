import tkinter as tk
from tkinter import ttk, messagebox
from collections import deque, namedtuple
from typing import List, Dict, Set, Tuple, Optional

class RiverCrossingSolver:
    """Solves the river crossing puzzle with multiple constraints using BFS, DFS, or DLS."""
    
    ROLES = ["Police", "Father", "Mom", "Thief", 
             "Son1", "Son2", "Daughter1", "Daughter2"]
    OPERATORS = {0, 1, 2}  # Indices of Police, Father, Mom
    State = namedtuple('State', ['police', 'father', 'mom', 'thief', 
                               'son1', 'son2', 'daughter1', 'daughter2', 'boat'])

    def __init__(self):
        self.reset()

    def reset(self):
        """Reset solver state."""
        self.visited = set()
        self.parents = {}
        self.solution_path = []
        self.all_states = []
        self.max_depth = 0
        self.current_animation = None

    def is_goal(self, state: str) -> bool:
        """Check if all have crossed to the right bank."""
        return all(side == 'R' for side in state[:-1])

    def is_valid(self, state: str) -> bool:
        """Validate constraints for a given state."""
        left_bank = {role for role, side in zip(self.ROLES, state) if side == 'L'}
        right_bank = {role for role, side in zip(self.ROLES, state) if side == 'R'}
        
        return (self._is_bank_safe(left_bank) and self._is_bank_safe(right_bank))

    def _is_bank_safe(self, bank: Set[str]) -> bool:
        """Check safety constraints for one bank."""
        has_police = 'Police' in bank
        has_father = 'Father' in bank
        has_mother = 'Mom' in bank
        
        # Thief cannot be with others without police
        if 'Thief' in bank and not has_police and len(bank) > 1:
            return False
            
        # Father cannot be with daughters without mother
        if has_father and not has_mother:
            if any(d in bank for d in ['Daughter1', 'Daughter2']):
                return False
                
        # Mother cannot be with sons without father
        if has_mother and not has_father:
            if any(s in bank for s in ['Son1', 'Son2']):
                return False
                
        return True

    def get_valid_moves(self, state: str) -> List[Tuple[int, Optional[int]]]:
        """Generate all possible valid moves from current state."""
        moves = []
        boat_side = state[-1]
        operator_indices = [i for i in self.OPERATORS if state[i] == boat_side]
        
        # Single-person crossings (only operators)
        for op_idx in operator_indices:
            moves.append((op_idx, None))
        
        # Two-person crossings (operator + any)
        for i, op_idx in enumerate(operator_indices):
            for passenger_idx in range(len(state)-1):
                if passenger_idx != op_idx and state[passenger_idx] == boat_side:
                    moves.append((op_idx, passenger_idx))
        
        return moves

    def apply_move(self, state: str, move: Tuple[int, Optional[int]]) -> str:
        """Apply a move to the current state."""
        op_idx, passenger_idx = move
        new_state = list(state)
        boat_side = new_state[-1]
        
        # Switch sides for the operator
        new_state[op_idx] = 'R' if boat_side == 'L' else 'L'
        
        # Switch side for passenger if exists
        if passenger_idx is not None:
            new_state[passenger_idx] = 'R' if boat_side == 'L' else 'L'
        
        # Switch boat side
        new_state[-1] = 'R' if boat_side == 'L' else 'L'
        
        return ''.join(new_state)

    def solve_bfs(self) -> bool:
        """Find solution using Breadth-First Search."""
        self.reset()
        queue = deque()
        initial_state = 'L' * 9  # All on left bank, boat on left
        queue.append(initial_state)
        self.visited.add(initial_state)
        
        while queue:
            current_state = queue.popleft()
            self.all_states.append(current_state)
            
            if self.is_goal(current_state):
                self._reconstruct_path(current_state)
                return True
            
            for move in self.get_valid_moves(current_state):
                new_state = self.apply_move(current_state, move)
                
                if new_state not in self.visited and self.is_valid(new_state):
                    self.visited.add(new_state)
                    self.parents[new_state] = current_state
                    queue.append(new_state)
        
        return False

    def solve_dfs(self) -> bool:
        """Find solution using Depth-First Search."""
        self.reset()
        stack = []
        initial_state = 'L' * 9
        stack.append(initial_state)
        
        while stack:
            current_state = stack.pop()
            
            if current_state in self.visited:
                continue
                
            self.visited.add(current_state)
            self.all_states.append(current_state)
            
            if self.is_goal(current_state):
                self._reconstruct_path(current_state)
                return True
                
            # Generate children in reverse order to maintain left-to-right exploration
            moves = self.get_valid_moves(current_state)
            for move in reversed(moves):
                new_state = self.apply_move(current_state, move)
                if new_state not in self.visited and self.is_valid(new_state):
                    self.parents[new_state] = current_state
                    stack.append(new_state)
        
        return False

    def solve_dls(self, limit: int = 20) -> bool:
        """Find solution using Depth-Limited Search."""
        self.reset()
        initial_state = 'L' * 9
        self.max_depth = 0
        return self._dls_helper(initial_state, limit)

    def _dls_helper(self, state: str, limit: int) -> bool:
        """Recursive helper for DLS."""
        if self.is_goal(state):
            self.all_states.append(state)
            self._reconstruct_path(state)
            return True
            
        if limit <= 0:
            return False
            
        self.visited.add(state)
        self.all_states.append(state)
        
        for move in self.get_valid_moves(state):
            new_state = self.apply_move(state, move)
            
            if new_state not in self.visited and self.is_valid(new_state):
                self.parents[new_state] = state
                if self._dls_helper(new_state, limit - 1):
                    return True
                
        return False

    def _reconstruct_path(self, goal_state: str) -> None:
        """Reconstruct path from goal to initial state."""
        path = []
        current = goal_state
        
        while current in self.parents:
            path.append(current)
            current = self.parents[current]
        
        path.append(current)  # Add initial state
        self.solution_path = path[::-1]  # Reverse to get from start to goal

    def visualize_state(self, state: str) -> Tuple[List[str], List[str]]:
        """Convert state string to left/right bank lists."""
        left = [role for role, side in zip(self.ROLES, state) if side == 'L']
        right = [role for role, side in zip(self.ROLES, state) if side == 'R']
        return left, right

    def reset(self):
        """Reset solver state."""
        self.visited = set()
        self.parents = {}
        self.solution_path = []
        self.all_states = []
        self.max_depth = 0


class RiverCrossingGUI:
    """GUI for the River Crossing Puzzle with enhanced controls."""
    
    def __init__(self, solver: RiverCrossingSolver):
        self.solver = solver
        self.window = tk.Tk()
        self.window.title("River Crossing Puzzle")
        self.window.geometry("900x800")
        
        self.animation_running = False
        self.current_step = 0
        self.total_steps = 0
        self.path_to_show = []
        self.transition_state = None
        
        self._setup_ui()
        
    def _setup_ui(self):
        """Initialize all UI components."""
        # Top frame for title
        self.top_frame = tk.Frame(master=self.window)
        self.title_label = tk.Label(
            master=self.top_frame, 
            text="River Crossing Puzzle", 
            font=("Arial", 16)
        )
        self.title_label.pack(pady=10)
        self.top_frame.pack()
        
        # Algorithm selection frame
        self.algorithm_frame = tk.Frame(master=self.window)
        
        self.algorithm_label = tk.Label(
            master=self.algorithm_frame,
            text="Select Algorithm:",
            font=("Arial", 10)
        )
        self.algorithm_label.pack(side=tk.LEFT, padx=5)
        
        self.algorithm_var = tk.StringVar(value="BFS")
        self.algorithm_menu = ttk.Combobox(
            master=self.algorithm_frame,
            textvariable=self.algorithm_var,
            values=["BFS", "DFS", "DLS"],
            state="readonly",
            width=10
        )
        self.algorithm_menu.pack(side=tk.LEFT, padx=5)
        
        self.dls_depth_label = tk.Label(
            master=self.algorithm_frame,
            text="DLS Depth Limit:",
            font=("Arial", 10)
        )
        self.dls_depth_label.pack(side=tk.LEFT, padx=5)
        
        self.dls_depth_var = tk.StringVar(value="20")
        self.dls_depth_entry = tk.Entry(
            master=self.algorithm_frame,
            textvariable=self.dls_depth_var,
            width=5
        )
        self.dls_depth_entry.pack(side=tk.LEFT, padx=5)
        
        self.algorithm_frame.pack(pady=5)
        
        # Control buttons frame
        self.control_frame = tk.Frame(master=self.window)
        
        self.solve_button = tk.Button(
            master=self.control_frame, 
            text="Solve Puzzle", 
            command=self.solve_puzzle,
            width=15
        )
        self.solve_button.pack(side=tk.LEFT, padx=5)
        
        self.solution_button = tk.Button(
            master=self.control_frame, 
            text="Show Solution", 
            command=lambda: self.show_path(self.solver.solution_path),
            width=15,
            state=tk.DISABLED
        )
        self.solution_button.pack(side=tk.LEFT, padx=5)
        
        self.all_moves_button = tk.Button(
            master=self.control_frame, 
            text="Show All Moves", 
            command=lambda: self.show_path(self.solver.all_states),
            width=15,
            state=tk.DISABLED
        )
        self.all_moves_button.pack(side=tk.LEFT, padx=5)
        
        self.control_frame.pack(pady=5)
        
        # Animation control frame
        self.anim_control_frame = tk.Frame(master=self.window)
        
        self.start_button = tk.Button(
            master=self.anim_control_frame,
            text="▶ Start",
            command=self.start_animation,
            width=10,
            state=tk.DISABLED
        )
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = tk.Button(
            master=self.anim_control_frame,
            text="⏹ Stop",
            command=self.stop_animation,
            width=10,
            state=tk.DISABLED
        )
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        self.reset_button = tk.Button(
            master=self.anim_control_frame,
            text="🔄 Reset",
            command=self.reset_animation,
            width=10
        )
        self.reset_button.pack(side=tk.LEFT, padx=5)
        
        self.anim_control_frame.pack(pady=5)
        
        # Status and stats frame
        self.status_frame = tk.Frame(master=self.window)
        
        self.status_label = tk.Label(
            master=self.status_frame,
            text="Ready to solve...",
            font=("Arial", 10),
            width=60,
            anchor=tk.W
        )
        self.status_label.pack(side=tk.LEFT, padx=10)
        
        self.steps_label = tk.Label(
            master=self.status_frame,
            text="Step: 0/0",
            font=("Arial", 10)
        )
        self.steps_label.pack(side=tk.LEFT, padx=10)
        
        self.states_label = tk.Label(
            master=self.status_frame,
            text="Total States: 0",
            font=("Arial", 10)
        )
        self.states_label.pack(side=tk.LEFT, padx=10)
        
        self.status_frame.pack(pady=5)
        
        # Main visualization frame
        self.visualization_frame = tk.Frame(
            master=self.window, 
            width=800, 
            height=500,
            bg="white"
        )
        
        # Left bank (green)
        self.left_bank_frame = tk.Frame(
            master=self.visualization_frame, 
            width=300, 
            height=500, 
            bg="lightgreen",
            relief=tk.RAISED,
            borderwidth=2
        )
        
        # River (blue)
        self.river_frame = tk.Frame(
            master=self.visualization_frame, 
            width=200, 
            height=500, 
            bg="lightblue",
            relief=tk.SUNKEN,
            borderwidth=2
        )
        
        # Right bank (green)
        self.right_bank_frame = tk.Frame(
            master=self.visualization_frame, 
            width=300, 
            height=500, 
            bg="lightgreen",
            relief=tk.RAISED,
            borderwidth=2
        )
        
        # Pack frames
        self.left_bank_frame.pack(fill=tk.Y, side=tk.LEFT)
        self.river_frame.pack(fill=tk.Y, side=tk.LEFT)
        self.right_bank_frame.pack(fill=tk.Y, side=tk.LEFT)
        self.visualization_frame.pack(pady=10)
        
        # Speed control
        self.speed_frame = tk.Frame(master=self.window)
        self.speed_label = tk.Label(
            master=self.speed_frame,
            text="Animation Speed:",
            font=("Arial", 10)
        )
        self.speed_label.pack(side=tk.LEFT, padx=5)
        
        self.speed_var = tk.DoubleVar(value=1.0)
        self.speed_scale = tk.Scale(
            master=self.speed_frame,
            from_=0.1,
            to=2.0,
            resolution=0.1,
            orient=tk.HORIZONTAL,
            variable=self.speed_var,
            length=200
        )
        self.speed_scale.pack(side=tk.LEFT)
        self.speed_frame.pack()
    
    def solve_puzzle(self):
        """Solve the puzzle using the selected algorithm."""
        self.reset_animation()
        algorithm = self.algorithm_var.get()
        
        try:
            if algorithm == "BFS":
                success = self.solver.solve_bfs()
            elif algorithm == "DFS":
                success = self.solver.solve_dfs()
            elif algorithm == "DLS":
                depth = int(self.dls_depth_var.get())
                success = self.solver.solve_dls(depth)
            else:
                messagebox.showerror("Error", "Invalid algorithm selected")
                return
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number for DLS depth")
            return
            
        if success:
            messagebox.showinfo("Success", "Solution found!")
            self.solution_button.config(state=tk.NORMAL)
            self.all_moves_button.config(state=tk.NORMAL)
            self.states_label.config(text=f"Total States: {len(self.solver.all_states)}")
        else:
            messagebox.showinfo("No Solution", "No solution found with current parameters")
    
    def show_path(self, path: List[str]):
        """Prepare to show a path (solution or all moves)."""
        if not path:
            messagebox.showwarning("No Path", "No path to display!")
            return
            
        self.path_to_show = path
        self.current_step = 0
        self.total_steps = len(path)
        self.steps_label.config(text=f"Step: 0/{self.total_steps}")
        
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.NORMAL)
        self._update_visualization(self.path_to_show[0], 0, self.total_steps)
    
    def start_animation(self):
        """Start the animation of the path."""
        if self.animation_running:
            return
            
        self.animation_running = True
        self._animate_next_step()
    
    def stop_animation(self):
        """Stop the current animation."""
        self.animation_running = False
        if hasattr(self, 'after_id'):
            self.window.after_cancel(self.after_id)
    
    def reset_animation(self):
        """Reset the animation to initial state."""
        self.stop_animation()
        self.current_step = 0
        self.total_steps = 0
        self.path_to_show = []
        self.transition_state = None
        self._clear_visualization()
        self.status_label.config(text="Ready to solve...")
        self.steps_label.config(text="Step: 0/0")
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.DISABLED)
    
    def _animate_next_step(self):
        """Animate the next step in the path."""
        if not self.animation_running or self.current_step >= self.total_steps - 1:
            self.animation_running = False
            return
            
        # Calculate delay based on speed (2000ms base delay for 1.0 speed)
        base_delay = 2000  # 2 seconds at speed 1.0
        delay = int(base_delay / self.speed_var.get())
        
        # First show transition (half the time)
        self.current_step += 1
        self._show_transition_state(self.path_to_show[self.current_step-1], 
                                  self.path_to_show[self.current_step])
        
        # Then show the final state after half delay
        self.after_id = self.window.after(delay // 2, lambda: 
            self._update_visualization(
                self.path_to_show[self.current_step],
                self.current_step,
                self.total_steps
            )
        )
        
        # Schedule next step
        self.after_id = self.window.after(delay, self._animate_next_step)
    
    def _show_transition_state(self, from_state: str, to_state: str):
        """Show the transition between two states."""
        self.transition_state = (from_state, to_state)
        
        # Highlight who is moving
        moving = []
        for i in range(len(from_state)-1):
            if from_state[i] != to_state[i]:
                moving.append(self.solver.ROLES[i])
        
        boat_dir = "➡️" if from_state[-1] == 'L' else "⬅️"
        transition_text = f"Moving: {', '.join(moving)} {boat_dir}"
        
        self._clear_visualization()
        
        # Show transition message in the river frame
        transition_label = tk.Label(
            master=self.river_frame,
            text=transition_text,
            font=("Arial", 14, "bold"),
            bg="lightblue"
        )
        transition_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # Update status
        self.status_label.config(text=f"Transition: {transition_text}")
        self.steps_label.config(text=f"Step: {self.current_step}/{self.total_steps}")
    
    def _update_visualization(self, state: str, step: int, total_steps: int):
        """Update the visualization for a given state."""
        self._clear_visualization()
        
        left_bank, right_bank = self.solver.visualize_state(state)
        boat_side = "left" if state[-1] == 'L' else "right"
        
        # Update status
        self.status_label.config(
            text=f"Step {step + 1}/{total_steps} - Boat is on {boat_side} side"
        )
        
        # Display left bank
        left_label = tk.Label(
            master=self.left_bank_frame,
            text="Left Bank",
            font=("Arial", 12, "bold"),
            bg="lightgreen"
        )
        left_label.pack(pady=5)
        
        for role in left_bank:
            label = tk.Label(
                master=self.left_bank_frame,
                text=role,
                font=("Arial", 12),
                bg="lightgreen"
            )
            label.pack(pady=2)
        
        # Display right bank
        right_label = tk.Label(
            master=self.right_bank_frame,
            text="Right Bank",
            font=("Arial", 12, "bold"),
            bg="lightgreen"
        )
        right_label.pack(pady=5)
        
        for role in right_bank:
            label = tk.Label(
                master=self.right_bank_frame,
                text=role,
                font=("Arial", 12),
                bg="lightgreen"
            )
            label.pack(pady=2)
        
        # Display boat
        boat_text = "🛶 ➡️" if state[-1] == 'R' else "⬅️ 🛶"
        boat_label = tk.Label(
            master=self.river_frame,
            text=f"{boat_text}\nBoat is on\n{boat_side} side",
            font=("Arial", 14),
            bg="lightblue"
        )
        boat_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
    
    def _clear_visualization(self):
        """Clear all widgets from visualization frames."""
        for frame in [self.left_bank_frame, self.river_frame, self.right_bank_frame]:
            for widget in frame.winfo_children():
                widget.destroy()
    
    def run(self):
        """Run the main application loop."""
        self.window.mainloop()


def main():
    solver = RiverCrossingSolver()
    app = RiverCrossingGUI(solver)
    app.run()


if __name__ == "__main__":
    main()