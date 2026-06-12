import tkinter as tk
from tkinter import messagebox
import sqlite3
import os
import datetime
import time

# Use winsound on Windows for non-blocking notification alerts
try:
    import winsound
    HAS_WINSOUND = True
except ImportError:
    HAS_WINSOUND = False

# Determine database location
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(SCRIPT_DIR, "focus_tracker.db")

def init_db():
    """Initializes the SQLite database to track focus sessions."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS focus_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_name TEXT NOT NULL,
            category TEXT NOT NULL,
            duration_minutes INTEGER NOT NULL,
            date TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def log_session(task_name, category, duration):
    """Logs a completed focus session to the database."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    date_str = datetime.date.today().isoformat()
    cursor.execute(
        "INSERT INTO focus_sessions (task_name, category, duration_minutes, date) VALUES (?, ?, ?, ?)",
        (task_name, category, duration, date_str)
    )
    conn.commit()
    conn.close()

def get_stats_last_7_days():
    """Retrieves focus duration (minutes) for the last 7 days, sorted chronologically."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Calculate date range
    today = datetime.date.today()
    dates = [today - datetime.timedelta(days=i) for i in range(6, -1, -1)]
    date_strs = [d.isoformat() for d in dates]
    
    stats = {d: 0 for d in date_strs}
    
    cursor.execute(
        "SELECT date, SUM(duration_minutes) FROM focus_sessions WHERE date >= ? GROUP BY date",
        (date_strs[0],)
    )
    rows = cursor.fetchall()
    conn.close()
    
    for row in rows:
        db_date, mins = row
        if db_date in stats:
            stats[db_date] = int(mins)
            
    return [(dates[i], stats[date_strs[i]]) for i in range(7)]

def get_today_summary():
    """Retrieves today's total focus minutes and completed session counts."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    date_str = datetime.date.today().isoformat()
    
    cursor.execute(
        "SELECT COUNT(*), SUM(duration_minutes) FROM focus_sessions WHERE date = ?",
        (date_str,)
    )
    row = cursor.fetchone()
    conn.close()
    
    count = row[0] if row[0] is not None else 0
    duration = row[1] if row[1] is not None else 0
    return count, duration

class FocusFlowApp:
    def __init__(self, root):
        self.root = root
        self.root.title("FocusFlow - Pomodoro & Focus Tracker")
        self.root.geometry("450x690")
        self.root.configure(bg="#1e1e2e")  # Catppuccin Mocha base
        self.root.resizable(False, False)

        # Style colors
        self.bg_color = "#1e1e2e"
        self.card_color = "#252538"
        self.text_color = "#cdd6f4"
        self.text_muted = "#7f849c"
        self.entry_bg = "#313244"
        self.border_color = "#45475a"
        
        # Mode-specific colors
        self.color_focus = "#f38ba8"       # Pastel Pink/Red
        self.color_short = "#a6e3a1"       # Pastel Green
        self.color_long = "#74c7ec"        # Pastel Blue
        
        # Categories mapping
        self.categories = ["Coding", "Reading", "Writing", "Learning", "General"]

        # Timer states
        self.current_mode = "Focus"  # Focus, Short Break, Long Break
        self.timer_seconds = 25 * 60
        self.timer_running = False
        self.after_id = None
        self.timer_max_seconds = 25 * 60

        # Build UI Components
        self.create_widgets()
        
        # Load initial stats
        self.update_stats_display()

    def create_widgets(self):
        # 1. Header Frame
        header_frame = tk.Frame(self.root, bg=self.bg_color)
        header_frame.pack(fill="x", padx=20, pady=(15, 5))

        title_label = tk.Label(
            header_frame, 
            text="FocusFlow", 
            font=("Segoe UI", 18, "bold"), 
            bg=self.bg_color, 
            fg=self.text_color
        )
        title_label.pack(side="left")

        subtitle_label = tk.Label(
            header_frame, 
            text="Timer", 
            font=("Segoe UI", 11, "bold"), 
            bg=self.bg_color, 
            fg=self.color_focus
        )
        self.subtitle_label = subtitle_label
        subtitle_label.pack(side="left", padx=5, pady=(5, 0))

        # 2. Main Timer Display Card
        timer_card = tk.Frame(self.root, bg=self.card_color, padx=15, pady=15)
        timer_card.pack(fill="x", padx=20, pady=10)

        # Mode Tab Buttons inside Timer Card
        mode_btn_frame = tk.Frame(timer_card, bg=self.card_color)
        mode_btn_frame.pack(fill="x", pady=(0, 10))

        self.btn_focus = tk.Button(
            mode_btn_frame, text="Focus (25m)", font=("Segoe UI", 9, "bold"),
            bg=self.entry_bg, fg=self.color_focus, activebackground=self.border_color,
            activeforeground=self.color_focus, bd=0, cursor="hand2", padx=8, pady=3,
            command=lambda: self.switch_mode("Focus", 25 * 60)
        )
        self.btn_focus.pack(side="left", expand=True, fill="x", padx=2)

        self.btn_short = tk.Button(
            mode_btn_frame, text="Short Break (5m)", font=("Segoe UI", 9, "bold"),
            bg=self.card_color, fg=self.text_muted, activebackground=self.border_color,
            activeforeground=self.color_short, bd=0, cursor="hand2", padx=8, pady=3,
            command=lambda: self.switch_mode("Short Break", 5 * 60)
        )
        self.btn_short.pack(side="left", expand=True, fill="x", padx=2)

        self.btn_long = tk.Button(
            mode_btn_frame, text="Long Break (15m)", font=("Segoe UI", 9, "bold"),
            bg=self.card_color, fg=self.text_muted, activebackground=self.border_color,
            activeforeground=self.color_long, bd=0, cursor="hand2", padx=8, pady=3,
            command=lambda: self.switch_mode("Long Break", 15 * 60)
        )
        self.btn_long.pack(side="left", expand=True, fill="x", padx=2)

        # Radial Timer Canvas
        self.canvas_timer = tk.Canvas(
            timer_card, width=190, height=190, bg=self.card_color, bd=0, highlightthickness=0
        )
        self.canvas_timer.pack(pady=10)
        self.draw_timer_arc()

        # Timer Controls Frame
        controls_frame = tk.Frame(timer_card, bg=self.card_color)
        controls_frame.pack(pady=5)

        self.btn_play = tk.Button(
            controls_frame, text="▶ Start", font=("Segoe UI", 10, "bold"),
            bg=self.color_focus, fg=self.bg_color, activebackground="#f5e0dc",
            activeforeground=self.bg_color, bd=0, cursor="hand2", padx=15, pady=6,
            command=self.toggle_timer
        )
        self.btn_play.pack(side="left", padx=5)

        self.btn_reset = tk.Button(
            controls_frame, text="↺ Reset", font=("Segoe UI", 10, "bold"),
            bg=self.entry_bg, fg=self.text_color, activebackground=self.border_color,
            activeforeground=self.text_color, bd=0, cursor="hand2", padx=12, pady=6,
            command=self.reset_timer
        )
        self.btn_reset.pack(side="left", padx=5)

        self.btn_skip = tk.Button(
            controls_frame, text="⏭ Skip", font=("Segoe UI", 10, "bold"),
            bg=self.entry_bg, fg=self.text_color, activebackground=self.border_color,
            activeforeground=self.text_color, bd=0, cursor="hand2", padx=12, pady=6,
            command=self.skip_session
        )
        self.btn_skip.pack(side="left", padx=5)

        # 3. Log Task Entry Card
        self.task_card = tk.Frame(self.root, bg=self.card_color, padx=15, pady=12)
        self.task_card.pack(fill="x", padx=20, pady=5)

        task_title = tk.Label(
            self.task_card, text="Session Task Log", font=("Segoe UI", 11, "bold"),
            bg=self.card_color, fg=self.text_color
        )
        task_title.pack(anchor="w", pady=(0, 6))

        task_row = tk.Frame(self.task_card, bg=self.card_color)
        task_row.pack(fill="x")

        self.task_var = tk.StringVar()
        self.task_entry = tk.Entry(
            task_row, textvariable=self.task_var, font=("Segoe UI", 10),
            bg=self.entry_bg, fg=self.text_color, insertbackground=self.text_color,
            bd=0, highlightthickness=1, highlightbackground=self.border_color,
            highlightcolor=self.color_focus
        )
        self.task_entry.pack(side="left", fill="x", expand=True, ipady=5, padx=(0, 5))
        self.setup_placeholder(self.task_entry, "Task (e.g. Code feature X)")

        self.cat_var = tk.StringVar(value="Coding")
        self.cat_menu = tk.OptionMenu(task_row, self.cat_var, *self.categories)
        self.cat_menu.config(
            font=("Segoe UI", 9, "bold"), bg=self.entry_bg, fg=self.text_color,
            activebackground=self.border_color, activeforeground=self.text_color,
            bd=0, highlightthickness=1, highlightbackground=self.border_color,
            indicatoron=False, direction="below", cursor="hand2"
        )
        self.cat_menu["menu"].config(
            bg=self.entry_bg, fg=self.text_color, activebackground=self.color_focus,
            activeforeground=self.bg_color, font=("Segoe UI", 9)
        )
        self.cat_menu.pack(side="right", ipady=3, ipadx=10, padx=(5, 0))

        # 4. Statistics Dashboard Card
        stats_card = tk.Frame(self.root, bg=self.card_color, padx=15, pady=12)
        stats_card.pack(fill="both", expand=True, padx=20, pady=(10, 15))

        stats_header = tk.Frame(stats_card, bg=self.card_color)
        stats_header.pack(fill="x", pady=(0, 5))

        stats_title = tk.Label(
            stats_header, text="Focus Statistics", font=("Segoe UI", 11, "bold"),
            bg=self.card_color, fg=self.text_color
        )
        stats_title.pack(side="left")

        self.lbl_stats_summary = tk.Label(
            stats_header, text="Today: 0 sessions (0m)", font=("Segoe UI", 9, "bold"),
            bg=self.card_color, fg=self.color_focus
        )
        self.lbl_stats_summary.pack(side="right")

        # Custom Bar Chart Canvas
        self.canvas_chart = tk.Canvas(
            stats_card, bg=self.card_color, bd=0, highlightthickness=0
        )
        self.canvas_chart.pack(fill="both", expand=True, pady=5)
        self.canvas_chart.bind("<Configure>", lambda e: self.draw_stats_chart())

    # Helper function for placeholders
    def setup_placeholder(self, entry, text):
        entry.insert(0, text)
        entry.config(fg=self.text_muted)
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

    # Visual Drawing: Arc-Based Clock Timer
    def draw_timer_arc(self):
        self.canvas_timer.delete("all")
        
        # Geometry constants
        cx, cy = 95, 95
        r = 80
        
        # Color mapping depending on mode
        color = self.color_focus
        if self.current_mode == "Short Break":
            color = self.color_short
        elif self.current_mode == "Long Break":
            color = self.color_long
            
        # Draw background ring (thin muted gray circular path)
        self.canvas_timer.create_oval(
            cx - r, cy - r, cx + r, cy + r,
            outline=self.border_color, width=8
        )
        
        # Draw active progress arc (starts at top, decreases clockwise)
        if self.timer_max_seconds > 0:
            ratio = self.timer_seconds / self.timer_max_seconds
            extent = int(-360 * ratio)
            if extent == 0 and ratio > 0:
                extent = -1 # Small visual nudge
                
            self.canvas_timer.create_arc(
                cx - r, cy - r, cx + r, cy + r,
                start=90, extent=extent, outline=color, width=8, style="arc"
            )
            
        # Format time to display (MM:SS)
        mins = self.timer_seconds // 60
        secs = self.timer_seconds % 60
        time_str = f"{mins:02d}:{secs:02d}"
        
        self.canvas_timer.create_text(
            cx, cy, text=time_str, font=("Segoe UI", 28, "bold"), fill=self.text_color
        )
        
        # Display current status in text
        status_text = self.current_mode.upper()
        if not self.timer_running and self.timer_seconds == self.timer_max_seconds:
            status_text += " (READY)"
        elif not self.timer_running:
            status_text += " (PAUSED)"
            
        self.canvas_timer.create_text(
            cx, cy + 28, text=status_text, font=("Segoe UI", 9, "bold"), fill=self.text_muted
        )

    # Visual Drawing: Bar Chart of focus sessions
    def draw_stats_chart(self):
        self.canvas_chart.delete("all")
        
        w = self.canvas_chart.winfo_width()
        h = self.canvas_chart.winfo_height()
        
        # Default sizing if window configure has not completed
        if w <= 1 or h <= 1:
            w = 380
            h = 130
            
        # Get data
        data_points = get_stats_last_7_days()
        max_mins = max([item[1] for item in data_points] + [60])  # Normalize to at least 60m height
        
        # Dimensions and margins
        left_margin = 35
        right_margin = 15
        top_margin = 20
        bottom_margin = 25
        
        chart_w = w - left_margin - right_margin
        chart_h = h - top_margin - bottom_margin
        
        # Draw gridlines (0%, 50%, 100% heights)
        for val in [0.0, 0.5, 1.0]:
            y_pos = top_margin + chart_h * (1.0 - val)
            self.canvas_chart.create_line(
                left_margin, y_pos, w - right_margin, y_pos,
                fill=self.border_color, dash=(2, 2)
            )
            
            # Label gridlines
            lbl_val = int(max_mins * val)
            self.canvas_chart.create_text(
                left_margin - 8, y_pos, text=f"{lbl_val}m",
                font=("Segoe UI", 8), fill=self.text_muted, anchor="e"
            )
            
        # Draw columns
        col_width = chart_w / 7
        for idx, (day_date, mins) in enumerate(data_points):
            # Column boundaries
            x1 = left_margin + idx * col_width + 8
            x2 = left_margin + (idx + 1) * col_width - 8
            
            # Prevent column from rendering backward if mins is 0
            height_ratio = mins / max_mins
            y1 = top_margin + chart_h * (1.0 - height_ratio)
            y2 = top_margin + chart_h
            
            # Select bar color
            color = self.color_focus if idx == 6 else self.border_color
            if mins > 0 and idx < 6:
                color = "#89b4fa"  # Pastel blue for past active days
                
            # Draw rounded bar (approximated via small polygon or rect)
            if mins > 0:
                self.canvas_chart.create_rectangle(
                    x1, y1, x2, y2, fill=color, outline=""
                )
                # Display minute label above the bar
                self.canvas_chart.create_text(
                    (x1 + x2)/2, y1 - 8, text=f"{mins}m",
                    font=("Segoe UI", 8, "bold"), fill=self.text_color
                )
                
            # Weekday label below the bar
            weekday_name = day_date.strftime("%a")
            self.canvas_chart.create_text(
                (x1 + x2)/2, y2 + 10, text=weekday_name,
                font=("Segoe UI", 9), fill=self.text_color if idx == 6 else self.text_muted
            )

    # Core Timer Handlers
    def switch_mode(self, mode, seconds):
        if self.timer_running:
            if not messagebox.askyesno("Switch Timer?", f"An active {self.current_mode} timer is currently running. Switch modes anyway?", parent=self.root):
                return
                
        self.stop_ticker()
        self.current_mode = mode
        self.timer_seconds = seconds
        self.timer_max_seconds = seconds
        
        # Style adjustments
        self.update_mode_styling()
        self.draw_timer_arc()

    def update_mode_styling(self):
        # Determine theme color
        if self.current_mode == "Focus":
            color = self.color_focus
            self.btn_focus.config(bg=self.entry_bg, fg=self.color_focus)
            self.btn_short.config(bg=self.card_color, fg=self.text_muted)
            self.btn_long.config(bg=self.card_color, fg=self.text_muted)
            self.task_card.pack(fill="x", padx=20, pady=5)  # Show task entry card
        elif self.current_mode == "Short Break":
            color = self.color_short
            self.btn_focus.config(bg=self.card_color, fg=self.text_muted)
            self.btn_short.config(bg=self.entry_bg, fg=self.color_short)
            self.btn_long.config(bg=self.card_color, fg=self.text_muted)
            self.task_card.pack_forget()                    # Hide task logging on break
        else:
            color = self.color_long
            self.btn_focus.config(bg=self.card_color, fg=self.text_muted)
            self.btn_short.config(bg=self.card_color, fg=self.text_muted)
            self.btn_long.config(bg=self.entry_bg, fg=self.color_long)
            self.task_card.pack_forget()                    # Hide task logging on break
            
        self.subtitle_label.config(text=self.current_mode, fg=color)
        self.btn_play.config(bg=color, text="▶ Start")
        self.task_entry.config(highlightcolor=color)

    def toggle_timer(self):
        if self.timer_running:
            self.stop_ticker()
            self.btn_play.config(text="▶ Start")
        else:
            self.timer_running = True
            self.btn_play.config(text="⏸ Pause")
            self.tick()
        self.draw_timer_arc()

    def stop_ticker(self):
        self.timer_running = False
        if self.after_id:
            self.root.after_cancel(self.after_id)
            self.after_id = None

    def tick(self):
        if not self.timer_running:
            return
            
        if self.timer_seconds > 0:
            self.timer_seconds -= 1
            self.draw_timer_arc()
            self.after_id = self.root.after(1000, self.tick)
        else:
            self.stop_ticker()
            self.handle_timer_completion()

    def reset_timer(self):
        self.stop_ticker()
        self.timer_seconds = self.timer_max_seconds
        self.update_mode_styling()
        self.draw_timer_arc()

    def skip_session(self):
        if messagebox.askyesno("Skip Session?", f"Skip this {self.current_mode} session?", parent=self.root):
            self.stop_ticker()
            self.advance_session(log_skipped=False)

    def handle_timer_completion(self):
        # Alert sound
        if HAS_WINSOUND:
            try:
                # Play pleasant system chime (non-blocking)
                winsound.MessageBeep(winsound.MB_ICONASTERISK)
            except Exception:
                pass
        else:
            self.root.bell()
            
        # If it was a focus session, save progress
        if self.current_mode == "Focus":
            task_desc = self.task_var.get().strip()
            if getattr(self.task_entry, "is_placeholder", False) or not task_desc:
                task_desc = "Quick Focus Session"
                
            category = self.cat_var.get()
            duration_mins = self.timer_max_seconds // 60
            
            # Write to database
            log_session(task_desc, category, duration_mins)
            
            # Reset task entry input box
            self.task_entry.delete(0, tk.END)
            self.restore_placeholder(self.task_entry)
            
            messagebox.showinfo("Session Finished!", f"Excellent work! You completed a {duration_mins} minute focus session on '{task_desc}'.", parent=self.root)
        else:
            messagebox.showinfo("Break Finished!", "Ready to focus? Let's get back to work!", parent=self.root)
            
        # Update dashboard widgets
        self.update_stats_display()
        
        # Progress timer states automatically
        self.advance_session(log_skipped=True)

    def advance_session(self, log_skipped=False):
        # Switch timer modes automatically
        if self.current_mode == "Focus":
            # Auto switch focus to short break
            self.switch_mode("Short Break", 5 * 60)
        else:
            # Auto switch break to focus
            self.switch_mode("Focus", 25 * 60)
            
        self.draw_timer_arc()

    def update_stats_display(self):
        # Today counts
        count, duration = get_today_summary()
        self.lbl_stats_summary.config(
            text=f"Today: {count} session{'s' if count != 1 else ''} ({duration}m)"
        )
        
        # Redraw chart
        self.draw_stats_chart()

if __name__ == "__main__":
    init_db()
    root = tk.Tk()
    app = FocusFlowApp(root)
    root.mainloop()
