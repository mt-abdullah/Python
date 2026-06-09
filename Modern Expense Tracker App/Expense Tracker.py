import tkinter as tk
from tkinter import messagebox, simpledialog
import sqlite3
import os
import datetime

# Determine the directory where this script is located for DB storage
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(SCRIPT_DIR, "expenses.db")

def init_db():
    """Initializes the SQLite database with expenses and settings tables."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            description TEXT NOT NULL,
            date TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    ''')
    # Set default budget if not set
    cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('budget', '1000.0')")
    conn.commit()
    conn.close()

def get_budget():
    """Retrieves the current budget from the database."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM settings WHERE key = 'budget'")
    row = cursor.fetchone()
    conn.close()
    return float(row[0]) if row else 1000.0

def set_budget(new_budget):
    """Updates the budget in the database."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('budget', ?)", (str(new_budget),))
    conn.commit()
    conn.close()

def add_expense(amount, category, description, date):
    """Adds a new expense to the database."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO expenses (amount, category, description, date) VALUES (?, ?, ?, ?)",
        (amount, category, description, date)
    )
    conn.commit()
    conn.close()

def delete_expense(expense_id):
    """Deletes an expense from the database by ID."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
    conn.commit()
    conn.close()

def get_expenses(category_filter="All"):
    """Fetches expenses, optionally filtered by category, sorted by date descending."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    if category_filter == "All":
        cursor.execute("SELECT id, amount, category, description, date FROM expenses ORDER BY date DESC, id DESC")
    else:
        cursor.execute(
            "SELECT id, amount, category, description, date FROM expenses WHERE category = ? ORDER BY date DESC, id DESC",
            (category_filter,)
        )
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_total_spent():
    """Calculates the sum of all expenses."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(amount) FROM expenses")
    row = cursor.fetchone()
    conn.close()
    return float(row[0]) if row[0] is not None else 0.0

class ExpenseTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Modern Expense Tracker")
        self.root.geometry("460x680")
        self.root.configure(bg="#1e1e2e")  # Catppuccin Mocha base
        self.root.resizable(False, False)

        # Style colors
        self.bg_color = "#1e1e2e"
        self.card_color = "#252538"
        self.accent_color = "#89b4fa"  # Blue
        self.accent_hover = "#b4befe"  # Light lavender
        self.text_color = "#cdd6f4"    # Light text
        self.text_muted = "#7f849c"    # Muted text
        self.entry_bg = "#313244"
        self.border_color = "#45475a"
        
        # Category colors map (for visual indicator dots/badges)
        self.category_colors = {
            "Food": "#f9e2af",          # Peach / Yellow
            "Bills": "#74c7ec",         # Sapphire / Light Blue
            "Shopping": "#cba6f7",      # Mauve / Purple
            "Entertainment": "#f5c2e7", # Pink
            "Travel": "#a6e3a1",        # Green
            "Other": "#94e2d5"          # Teal
        }
        self.categories = list(self.category_colors.keys())

        # Main scrollable tasks
        self.expense_rows = {}

        # Initialize UI Components
        self.create_widgets()
        
        # Load initial data
        self.update_budget_card()
        self.load_expenses_list()

    def create_widgets(self):
        # 1. Header Frame
        header_frame = tk.Frame(self.root, bg=self.bg_color)
        header_frame.pack(fill="x", padx=20, pady=(15, 10))

        title_label = tk.Label(
            header_frame, 
            text="Expense Tracker", 
            font=("Segoe UI", 18, "bold"), 
            bg=self.bg_color, 
            fg=self.text_color
        )
        title_label.pack(side="left")

        # 2. Budget Summary Card
        self.budget_card = tk.Frame(self.root, bg=self.card_color, padx=15, pady=12, bd=0)
        self.budget_card.pack(fill="x", padx=20, pady=(0, 10))

        # Upper row of budget card (Budget & Remaining)
        budget_info_frame = tk.Frame(self.budget_card, bg=self.card_color)
        budget_info_frame.pack(fill="x")

        self.lbl_budget = tk.Label(
            budget_info_frame, 
            text="Budget: $0.00", 
            font=("Segoe UI", 11, "bold"), 
            bg=self.card_color, 
            fg=self.accent_color
        )
        self.lbl_budget.pack(side="left")

        btn_edit_budget = tk.Button(
            budget_info_frame,
            text="Edit ⚙",
            font=("Segoe UI", 9, "bold"),
            bg=self.entry_bg,
            fg=self.text_color,
            activebackground=self.border_color,
            activeforeground=self.text_color,
            bd=0,
            cursor="hand2",
            padx=8,
            pady=2,
            command=self.edit_budget_dialog
        )
        btn_edit_budget.pack(side="right")

        # Spent & Remaining labels
        labels_frame = tk.Frame(self.budget_card, bg=self.card_color)
        labels_frame.pack(fill="x", pady=(8, 4))

        self.lbl_spent = tk.Label(
            labels_frame, 
            text="Spent: $0.00", 
            font=("Segoe UI", 10), 
            bg=self.card_color, 
            fg=self.text_color
        )
        self.lbl_spent.pack(side="left")

        self.lbl_remaining = tk.Label(
            labels_frame, 
            text="Remaining: $0.00", 
            font=("Segoe UI", 10), 
            bg=self.card_color, 
            fg=self.text_color
        )
        self.lbl_remaining.pack(side="right")

        # Canvas for Custom Progress Bar
        self.progress_canvas = tk.Canvas(
            self.budget_card,
            height=12,
            bg=self.card_color,
            bd=0,
            highlightthickness=0
        )
        self.progress_canvas.pack(fill="x", pady=(6, 2))
        self.progress_canvas.bind("<Configure>", lambda e: self.update_budget_card())

        # 3. Add Expense Card
        add_card = tk.Frame(self.root, bg=self.card_color, padx=15, pady=12)
        add_card.pack(fill="x", padx=20, pady=(0, 10))

        add_title = tk.Label(
            add_card,
            text="Log New Expense",
            font=("Segoe UI", 11, "bold"),
            bg=self.card_color,
            fg=self.text_color
        )
        add_title.pack(anchor="w", pady=(0, 8))

        # Inputs layout: Row 1 (Amount & Category)
        row1 = tk.Frame(add_card, bg=self.card_color)
        row1.pack(fill="x", pady=2)

        # Amount Entry
        self.amount_var = tk.StringVar()
        self.amount_entry = tk.Entry(
            row1,
            textvariable=self.amount_var,
            font=("Segoe UI", 10),
            bg=self.entry_bg,
            fg=self.text_color,
            insertbackground=self.text_color,
            bd=0,
            highlightthickness=1,
            highlightbackground=self.border_color,
            highlightcolor=self.accent_color
        )
        self.amount_entry.pack(side="left", fill="x", expand=True, ipady=5, padx=(0, 5))
        
        # Setup Amount Placeholder
        self.setup_placeholder(self.amount_entry, "Amount ($)")

        # Category Menu
        self.category_var = tk.StringVar(value="Food")
        self.category_menu = tk.OptionMenu(
            row1,
            self.category_var,
            *self.categories
        )
        self.category_menu.config(
            font=("Segoe UI", 9, "bold"),
            bg=self.entry_bg,
            fg=self.text_color,
            activebackground=self.border_color,
            activeforeground=self.text_color,
            bd=0,
            highlightthickness=1,
            highlightbackground=self.border_color,
            indicatoron=False,
            direction="below",
            cursor="hand2"
        )
        self.category_menu["menu"].config(
            bg=self.entry_bg,
            fg=self.text_color,
            activebackground=self.accent_color,
            activeforeground=self.bg_color,
            font=("Segoe UI", 9)
        )
        self.category_menu.pack(side="right", ipady=3, ipadx=10, padx=(5, 0))

        # Inputs layout: Row 2 (Description)
        row2 = tk.Frame(add_card, bg=self.card_color)
        row2.pack(fill="x", pady=6)

        self.desc_var = tk.StringVar()
        self.desc_entry = tk.Entry(
            row2,
            textvariable=self.desc_var,
            font=("Segoe UI", 10),
            bg=self.entry_bg,
            fg=self.text_color,
            insertbackground=self.text_color,
            bd=0,
            highlightthickness=1,
            highlightbackground=self.border_color,
            highlightcolor=self.accent_color
        )
        self.desc_entry.pack(fill="x", ipady=5)
        self.setup_placeholder(self.desc_entry, "Description (e.g. Lunch)")

        # Inputs layout: Row 3 (Date & Add Button)
        row3 = tk.Frame(add_card, bg=self.card_color)
        row3.pack(fill="x", pady=(2, 0))

        self.date_var = tk.StringVar()
        self.date_entry = tk.Entry(
            row3,
            textvariable=self.date_var,
            font=("Segoe UI", 10),
            bg=self.entry_bg,
            fg=self.text_color,
            insertbackground=self.text_color,
            bd=0,
            highlightthickness=1,
            highlightbackground=self.border_color,
            highlightcolor=self.accent_color
        )
        self.date_entry.pack(side="left", fill="x", expand=True, ipady=5, padx=(0, 5))
        self.setup_placeholder(self.date_entry, "Date (YYYY-MM-DD or empty)")

        btn_add = tk.Button(
            row3,
            text="+ Add Expense",
            font=("Segoe UI", 9, "bold"),
            bg=self.accent_color,
            fg=self.bg_color,
            activebackground=self.accent_hover,
            activeforeground=self.bg_color,
            bd=0,
            cursor="hand2",
            padx=12,
            command=self.submit_expense
        )
        btn_add.pack(side="right", ipady=4, padx=(5, 0))

        # 4. History Header & Filter
        history_header = tk.Frame(self.root, bg=self.bg_color)
        history_header.pack(fill="x", padx=20, pady=(5, 5))

        lbl_history = tk.Label(
            history_header,
            text="Expense History",
            font=("Segoe UI", 12, "bold"),
            bg=self.bg_color,
            fg=self.text_color
        )
        lbl_history.pack(side="left")

        # Category Filter Dropdown
        self.filter_var = tk.StringVar(value="All")
        filter_options = ["All"] + self.categories
        self.filter_menu = tk.OptionMenu(
            history_header,
            self.filter_var,
            *filter_options,
            command=lambda val: self.load_expenses_list()
        )
        self.filter_menu.config(
            font=("Segoe UI", 8, "bold"),
            bg=self.card_color,
            fg=self.text_color,
            activebackground=self.border_color,
            activeforeground=self.text_color,
            bd=0,
            highlightthickness=0,
            indicatoron=False,
            cursor="hand2"
        )
        self.filter_menu["menu"].config(
            bg=self.entry_bg,
            fg=self.text_color,
            activebackground=self.accent_color,
            activeforeground=self.bg_color,
            font=("Segoe UI", 9)
        )
        self.filter_menu.pack(side="right", ipadx=10, ipady=2)

        # 5. History List Box (Scrollable Frame)
        self.list_container = tk.Frame(self.root, bg=self.bg_color)
        self.list_container.pack(fill="both", expand=True, padx=20, pady=(0, 15))

        # Canvas for scrollable list
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
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw", width=400)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Keep internal window width synced with Canvas width
        self.canvas.bind('<Configure>', lambda event: self.canvas.itemconfigure(self.canvas_window, width=event.width))

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Mousewheel scrolling
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    # Placeholder utility functions
    def setup_placeholder(self, entry, text):
        entry.insert(0, text)
        entry.config(fg=self.text_muted)
        
        # Keep track of active state using dynamic attribute
        entry.is_placeholder = True
        entry.placeholder_text = text

        entry.bind("<FocusIn>", lambda e: self.clear_placeholder(entry))
        entry.bind("<FocusOut>", lambda e: self.restore_placeholder(entry))

    def clear_placeholder(self, entry):
        if getattr(entry, "is_placeholder", False):
            entry.delete(0, tk.END)
            entry.config(fg=self.text_color)
            entry.is_placeholder = False

    def restore_placeholder(self, entry):
        if not entry.get().strip():
            entry.insert(0, entry.placeholder_text)
            entry.config(fg=self.text_muted)
            entry.is_placeholder = True

    # Custom smooth polygon rounded rect drawing
    def draw_rounded_rect(self, canvas, x1, y1, x2, y2, radius=8, **kwargs):
        points = [
            x1+radius, y1,
            x1+radius, y1,
            x2-radius, y1,
            x2-radius, y1,
            x2, y1,
            x2, y1+radius,
            x2, y1+radius,
            x2, y2-radius,
            x2, y2-radius,
            x2, y2,
            x2-radius, y2,
            x2-radius, y2,
            x1+radius, y2,
            x1+radius, y2,
            x1, y2,
            x1, y2-radius,
            x1, y2-radius,
            x1, y1+radius,
            x1, y1+radius,
            x1, y1
        ]
        return canvas.create_polygon(points, **kwargs, smooth=True)

    def update_budget_card(self):
        """Calculates spending statistics and updates budget details and canvas progress bar."""
        budget = get_budget()
        spent = get_total_spent()
        remaining = budget - spent

        self.lbl_budget.config(text=f"Budget: ${budget:,.2f}")
        self.lbl_spent.config(text=f"Spent: ${spent:,.2f}")
        
        if remaining < 0:
            self.lbl_remaining.config(text=f"Over Budget: ${abs(remaining):,.2f}", fg=self.category_colors["Food"]) # Reddish/Warning alert text
        else:
            self.lbl_remaining.config(text=f"Remaining: ${remaining:,.2f}", fg=self.text_color)

        # Draw progress bar on canvas
        self.progress_canvas.delete("all")
        w = self.progress_canvas.winfo_width()
        h = self.progress_canvas.winfo_height()
        if w <= 1 or h <= 1:
            w = 390
            h = 12

        # Draw base background track
        self.draw_rounded_rect(self.progress_canvas, 1, 1, w-1, h-1, radius=5, fill=self.entry_bg, outline="")

        if budget > 0:
            ratio = spent / budget
            fill_width = int((w - 2) * min(ratio, 1.0))

            if ratio >= 0.9:
                color = "#f38ba8"  # Pastel red (danger)
            elif ratio >= 0.75:
                color = "#f9e2af"  # Pastel yellow (warning)
            else:
                color = "#a6e3a1"  # Pastel green (safe)

            if fill_width > 6:
                self.draw_rounded_rect(self.progress_canvas, 1, 1, fill_width, h-1, radius=5, fill=color, outline="")
            elif fill_width > 0:
                self.progress_canvas.create_rectangle(1, 1, fill_width, h-1, fill=color, outline="")

    def edit_budget_dialog(self):
        """Opens a simple dialog to set a new budget limit."""
        current_budget = get_budget()
        new_val = simpledialog.askfloat(
            "Set Monthly Budget",
            f"Enter new monthly budget target ($):\n(Current: ${current_budget:,.2f})",
            initialvalue=current_budget,
            minvalue=0.01,
            parent=self.root
        )
        if new_val is not None:
            set_budget(new_val)
            self.update_budget_card()

    def submit_expense(self):
        """Validates inputs and saves a new expense transaction."""
        # 1. Read Amount
        amount_str = self.amount_var.get().strip()
        if getattr(self.amount_entry, "is_placeholder", False) or not amount_str:
            messagebox.showerror("Validation Error", "Please enter a valid expense amount.", parent=self.root)
            return

        try:
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError()
        except ValueError:
            messagebox.showerror("Validation Error", "Amount must be a positive number.", parent=self.root)
            return

        # 2. Read Category
        category = self.category_var.get()

        # 3. Read Description
        description = self.desc_var.get().strip()
        if getattr(self.desc_entry, "is_placeholder", False) or not description:
            description = f"{category} Expense"

        # 4. Read Date
        date_str = self.date_var.get().strip()
        if getattr(self.date_entry, "is_placeholder", False) or not date_str:
            date_str = datetime.date.today().isoformat()
        else:
            try:
                # Validate date format YYYY-MM-DD
                datetime.date.fromisoformat(date_str)
            except ValueError:
                messagebox.showerror(
                    "Validation Error", 
                    "Date must be in YYYY-MM-DD format (or leave blank for today).", 
                    parent=self.root
                )
                return

        # Write to SQLite
        add_expense(amount, category, description, date_str)

        # Clear inputs
        self.amount_entry.delete(0, tk.END)
        self.restore_placeholder(self.amount_entry)
        
        self.desc_entry.delete(0, tk.END)
        self.restore_placeholder(self.desc_entry)
        
        self.date_entry.delete(0, tk.END)
        self.restore_placeholder(self.date_entry)

        # Update displays
        self.update_budget_card()
        self.load_expenses_list()

    def load_expenses_list(self):
        """Clears current list and rebuilds expense rows based on current filter selection."""
        # Clear existing rows in GUI
        for child in self.scrollable_frame.winfo_children():
            child.destroy()
        self.expense_rows.clear()

        filter_category = self.filter_var.get()
        records = get_expenses(filter_category)

        if not records:
            lbl_empty = tk.Label(
                self.scrollable_frame,
                text="No expenses found matching filter.",
                font=("Segoe UI", 10, "italic"),
                bg=self.bg_color,
                fg=self.text_muted,
                pady=20
            )
            lbl_empty.pack(fill="x")
            return

        for record in records:
            rec_id, amount, category, desc, date_str = record
            self.create_expense_row(rec_id, amount, category, desc, date_str)

    def create_expense_row(self, rec_id, amount, category, desc, date_str):
        row_frame = tk.Frame(self.scrollable_frame, bg=self.card_color, padx=12, pady=10)
        row_frame.pack(fill="x", pady=4, padx=2)

        # Left visual category dot indicator
        indicator_color = self.category_colors.get(category, self.accent_color)
        canvas_dot = tk.Canvas(row_frame, width=12, height=12, bg=self.card_color, bd=0, highlightthickness=0)
        canvas_dot.pack(side="left", padx=(0, 10))
        canvas_dot.create_oval(2, 2, 10, 10, fill=indicator_color, outline="")

        # Text Frame (Description + Date/Category)
        text_frame = tk.Frame(row_frame, bg=self.card_color)
        text_frame.pack(side="left", fill="both", expand=True)

        lbl_desc = tk.Label(
            text_frame, 
            text=desc,
            font=("Segoe UI", 11, "bold"),
            bg=self.card_color,
            fg=self.text_color,
            anchor="w",
            wraplength=200,
            justify="left"
        )
        lbl_desc.pack(anchor="w")

        lbl_sub = tk.Label(
            text_frame,
            text=f"{category} • {date_str}",
            font=("Segoe UI", 9),
            bg=self.card_color,
            fg=self.text_muted,
            anchor="w"
        )
        lbl_sub.pack(anchor="w", pady=(2, 0))

        # Amount Frame (Amount + Delete Button)
        right_frame = tk.Frame(row_frame, bg=self.card_color)
        right_frame.pack(side="right")

        lbl_amount = tk.Label(
            right_frame,
            text=f"-${amount:,.2f}",
            font=("Segoe UI", 11, "bold"),
            bg=self.card_color,
            fg="#f38ba8"  # Danger/Red
        )
        lbl_amount.pack(side="left", padx=8)

        # Trash icon delete button
        btn_del = tk.Button(
            right_frame,
            text="🗑",
            font=("Segoe UI", 11),
            bg=self.card_color,
            fg=self.text_muted,
            activebackground=self.card_color,
            activeforeground="#f38ba8",
            bd=0,
            cursor="hand2",
            command=lambda: self.trigger_delete(rec_id)
        )
        btn_del.pack(side="right")

        # Hover states
        btn_del.bind("<Enter>", lambda e: btn_del.config(fg="#f38ba8"))
        btn_del.bind("<Leave>", lambda e: btn_del.config(fg=self.text_muted))

        self.expense_rows[rec_id] = row_frame

    def trigger_delete(self, rec_id):
        """Deletes the expense from DB and updates interface."""
        delete_expense(rec_id)
        # Update view
        self.update_budget_card()
        self.load_expenses_list()

if __name__ == "__main__":
    init_db()
    root = tk.Tk()
    app = ExpenseTrackerApp(root)
    root.mainloop()
