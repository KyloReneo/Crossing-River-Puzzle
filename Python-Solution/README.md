# River Crossing Puzzle solution in python

This project is a Python application that solves the classic **River Crossing Puzzle** using search algorithms (BFS, DFS, DLS) and provides a **graphical user interface (GUI)** for visualizing the process and solution.

## 🧠 Puzzle Overview

You must get a group of people across a river under the following constraints:

- Only **Police**, **Father**, or **Mother** can operate the boat.
- The **Thief** cannot be left with others without the **Police**.
- The **Father** cannot be alone with the **Daughters** without the **Mother**.
- The **Mother** cannot be alone with the **Sons** without the **Father**.
- The boat can carry 1 or 2 people at a time.

The goal is to move all characters from the **left bank** to the **right bank** safely.

## 🚀 Features

- Solve the puzzle using:
  - **BFS (Breadth-First Search)**
  - **DFS (Depth-First Search)**
  - **DLS (Depth-Limited Search)**
- Step-by-step solution visualization.
- Interactive GUI with controls to:
  - Choose algorithm and DLS depth.
  - Play/pause/reset animation.
  - Show all states explored or just the final solution path.
  - Adjust animation speed.

## 🛠 Technologies Used

- **Python 3.8+**
- **Tkinter** for GUI
- **Standard libraries**: `collections`, `typing`, `tkinter.ttk`

## 📦 Installation

1. Clone this repository:

   ```
   git clone https://github.com/KyloReneo/Crossing-River-Puzzle.git
   ```

   ```
   cd Python-Solution
   ```

2. (Optional) Create and activate a virtual environment:

   ```
   python -m venv venv
   ```

   ```
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

## ▶️ How to Run:

```
python main.py
```

## 📄 License

This project is licensed under the MIT License. Feel free to use it or modify it for any personal or educational purpose.
