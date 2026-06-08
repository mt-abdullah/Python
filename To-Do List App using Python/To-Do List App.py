import tkinter as tk
from tkinter import messagebox

class TodoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Modern To-Do List")
        self.root.geometry("420x550")
        self.root.configure(bg="#1e1e2e") # Dark Slate / Catppuccin Mocha base
        self.root.resizable(False, False)

        # Style colors
        self.bg_color = "#1e1e2e"
        self.card_color = "#252538"
        self.accent_color = "#89b4fa" # Lavender/Blue accent
        self.text_color = "#cdd6f4"
        self.text_completed = "#585b70" # Muted text for completed tasks
        self.danger_color = "#f38ba8" # Pastel Red
        self.text_muted = "#7f849c"
        self.entry_bg = "#313244"

        # Tasks list to keep track of tasks: dictionary with task_id -> (frame, checkbutton, label, delete_button, var)
        self.tasks = {}
        self.task_counter = 0

        # Header Frame
        self.header_frame = tk.Frame(self.root, bg=self.bg_color)
        self.header_frame.pack(fill="x", padx=20, pady=(20, 10))

        self.title_label = tk.Label(
            self.header_frame, 
            text="My Tasks", 
            font=("Segoe UI", 20, "bold"), 
            bg=self.bg_color, 
            fg=self.text_color
        )
        self.title_label.pack(side="left")

        # Task counter label
        self.counter_label = tk.Label(
            self.header_frame,
            text="0 tasks",
            font=("Segoe UI", 10, "bold"),
            bg=self.accent_color,
            fg=self.bg_color,
            padx=8,
            pady=2
        )
        self.counter_label.pack(side="right")

        # Input Frame
        self.input_frame = tk.Frame(self.root, bg=self.bg_color)
        self.input_frame.pack(fill="x", padx=20, pady=(0, 15))

        self.entry_var = tk.StringVar()
        self.entry = tk.Entry(
            self.input_frame, 
            textvariable=self.entry_var,
            font=("Segoe UI", 12),
            bg=self.entry_bg,
            fg=self.text_color,
            insertbackground=self.text_color, # Cursor color
            bd=0,
            highlightthickness=1,
            highlightbackground="#45475a",
            highlightcolor=self.accent_color
        )
        self.entry.pack(side="left", fill="x", expand=True, ipady=8, padx=(0, 10))
        self.entry.bind("<Return>", lambda event: self.add_task())

        # Placeholder functionality
        self.placeholder_text = "Add a new task..."
        self.entry.insert(0, self.placeholder_text)
        self.entry.config(fg=self.text_muted)
        self.placeholder_active = True
        self.entry.bind("<FocusIn>", self.clear_placeholder)
        self.entry.bind("<FocusOut>", self.restore_placeholder)

        self.add_btn = tk.Button(
            self.input_frame,
            text="+ Add",
            font=("Segoe UI", 11, "bold"),
            bg=self.accent_color,
            fg=self.bg_color,
            activebackground="#b4befe",
            activeforeground=self.bg_color,
            bd=0,
            cursor="hand2",
            command=self.add_task,
            padx=15
        )
        self.add_btn.pack(side="right", ipady=6)

        # List Container
        self.list_container = tk.Frame(self.root, bg=self.bg_color)
        self.list_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Canvas for scrollable tasks
        self.canvas = tk.Canvas(
            self.list_container, 
            bg=self.bg_color, 
            bd=0, 
            highlightthickness=0
        )
        self.scrollbar = tk.Scrollbar(
            self.list_container, 
            orient="vertical", 
            command=self.canvas.yview
        )
        self.scrollable_frame = tk.Frame(self.canvas, bg=self.bg_color)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw", width=360)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Mousewheel scrolling
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def clear_placeholder(self, event):
        if self.placeholder_active:
            self.entry.delete(0, tk.END)
            self.entry.config(fg=self.text_color)
            self.placeholder_active = False

    def restore_placeholder(self, event):
        if not self.entry.get().strip():
            self.entry.insert(0, self.placeholder_text)
            self.entry.config(fg=self.text_muted)
            self.placeholder_active = True

    def add_task(self):
        task_text = self.entry_var.get().strip()
        if self.placeholder_active or not task_text or task_text == self.placeholder_text:
            return

        # Add the task layout
        self.create_task_row(task_text)
        
        # Reset input
        self.entry.delete(0, tk.END)
        self.entry.focus_set() # Keep focus to allow typing next task quickly
        self.placeholder_active = False # Reset so typing starts clean
        self.update_counter()

    def create_task_row(self, text):
        task_id = self.task_counter
        self.task_counter += 1

        # Main row frame
        row_frame = tk.Frame(self.scrollable_frame, bg=self.card_color, padx=10, pady=8)
        row_frame.pack(fill="x", pady=4)

        # Var for checkbox
        checked_var = tk.BooleanVar(value=False)

        # Style function for checking/unchecking
        def toggle_task():
            if checked_var.get():
                task_label.config(fg=self.text_completed, font=("Segoe UI", 11, "overstrike"))
            else:
                task_label.config(fg=self.text_color, font=("Segoe UI", 11))

        # Checkbutton
        chk = tk.Checkbutton(
            row_frame,
            variable=checked_var,
            command=toggle_task,
            bg=self.card_color,
            activebackground=self.card_color,
            selectcolor=self.bg_color,
            bd=0,
            highlightthickness=0
        )
        chk.pack(side="left")

        # Task label
        task_label = tk.Label(
            row_frame,
            text=text,
            font=("Segoe UI", 11),
            bg=self.card_color,
            fg=self.text_color,
            anchor="w",
            wraplength=260,
            justify="left"
        )
        task_label.pack(side="left", fill="x", expand=True, padx=8)

        # Delete button (using unicode trash bin symbol)
        del_btn = tk.Button(
            row_frame,
            text="🗑",
            font=("Segoe UI", 11),
            bg=self.card_color,
            fg=self.text_muted,
            activebackground=self.card_color,
            activeforeground=self.danger_color,
            bd=0,
            cursor="hand2",
            command=lambda: self.delete_task(task_id)
        )
        del_btn.pack(side="right")
        
        # Hover effect for delete button
        del_btn.bind("<Enter>", lambda e: del_btn.config(fg=self.danger_color))
        del_btn.bind("<Leave>", lambda e: del_btn.config(fg=self.text_muted))

        self.tasks[task_id] = (row_frame, chk, task_label, del_btn, checked_var)

    def delete_task(self, task_id):
        if task_id in self.tasks:
            row_frame = self.tasks[task_id][0]
            row_frame.destroy()
            del self.tasks[task_id]
            self.update_counter()

    def update_counter(self):
        count = len(self.tasks)
        if count == 1:
            self.counter_label.config(text="1 task")
        else:
            self.counter_label.config(text=f"{count} tasks")

if __name__ == "__main__":
    root = tk.Tk()
    app = TodoApp(root)
    root.mainloop()
