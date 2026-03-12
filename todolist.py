import tkinter as tk
from tkinter import messagebox
import sqlite3

# ---------------- DATABASE SETUP ---------------- #

conn = sqlite3.connect("tasks.db")
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS tasks(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    title TEXT,
    priority TEXT,
    completed INTEGER
)
""")
conn.commit()

# ---------------- GLOBAL VARIABLE ---------------- #
current_user = None

# ---------------- LOGIN / REGISTER ---------------- #

def login(username, password):
    if username == "" or password == "":
        messagebox.showwarning("Warning", "Enter username and password")
        return

    cur.execute("SELECT id FROM users WHERE username=? AND password=?", (username, password))
    user = cur.fetchone()

    if user:
        global current_user
        current_user = user[0]
        login_frame.pack_forget()
        dashboard()
    else:
        messagebox.showerror("Error", "Invalid username or password")

def register(username, password):
    if username == "" or password == "":
        messagebox.showwarning("Warning", "Enter username and password")
        return

    cur.execute("SELECT * FROM users WHERE username=?", (username,))
    existing = cur.fetchone()

    if existing:
        messagebox.showerror("Error", "User already exists")
        return

    cur.execute("INSERT INTO users(username,password) VALUES(?,?)", (username, password))
    conn.commit()
    messagebox.showinfo("Success", "Registration successful. Now login.")

# ---------------- FRIENDLY LOGIN INTERFACE ---------------- #

def show_login_screen(root):
    global login_frame, user_entry, pass_entry

    login_frame = tk.Frame(root, bg="#1e1e1e")
    login_frame.pack(fill="both", expand=True)

    tk.Label(
        login_frame,
        text="📝 Welcome to Advanced To-Do Manager",
        fg="#00ffcc",
        bg="#1e1e1e",
        font=("Helvetica", 18, "bold")
    ).pack(pady=(20, 10))

    tk.Label(
        login_frame,
        text="Please login or register to continue",
        fg="white",
        bg="#1e1e1e",
        font=("Helvetica", 12)
    ).pack(pady=(0, 20))

    tk.Label(
        login_frame,
        text="Username:",
        fg="white",
        bg="#1e1e1e",
        font=("Helvetica", 12)
    ).pack(anchor="w", padx=50)
    user_entry = tk.Entry(login_frame, width=30, font=("Helvetica", 12))
    user_entry.pack(pady=(0, 10))

    tk.Label(
        login_frame,
        text="Password:",
        fg="white",
        bg="#1e1e1e",
        font=("Helvetica", 12)
    ).pack(anchor="w", padx=50)
    pass_entry = tk.Entry(login_frame, width=30, font=("Helvetica", 12), show="*")
    pass_entry.pack(pady=(0, 20))

    button_frame = tk.Frame(login_frame, bg="#1e1e1e")
    button_frame.pack(pady=10)

    # Login Button
    tk.Button(
        button_frame,
        text="Login",
        command=lambda: login(user_entry.get().strip(), pass_entry.get().strip()),
        bg="#00cc66",
        fg="white",
        activebackground="#009944",
        activeforeground="white",
        width=12,
        font=("Helvetica", 12),
        relief="flat",
        bd=0,
        highlightthickness=0
    ).grid(row=0, column=0, padx=10)

    # Register Button
    tk.Button(
        button_frame,
        text="Register",
        command=lambda: register(user_entry.get().strip(), pass_entry.get().strip()),
        bg="#0099ff",
        fg="white",
        activebackground="#0066cc",
        activeforeground="white",
        width=12,
        font=("Helvetica", 12),
        relief="flat",
        bd=0,
        highlightthickness=0
    ).grid(row=0, column=1, padx=10)

# ---------------- TASK FUNCTIONS ---------------- #

def add_task():
    title = task_entry.get().strip()
    priority = priority_var.get()

    if title == "":
        return

    cur.execute(
        "INSERT INTO tasks(user_id,title,priority,completed) VALUES(?,?,?,0)",
        (current_user, title, priority)
    )
    conn.commit()
    task_entry.delete(0, tk.END)
    load_tasks()

def delete_task():
    selected = task_list.curselection()
    if not selected:
        return

    task = task_list.get(selected[0])
    cur.execute(
        "DELETE FROM tasks WHERE title=? AND user_id=?",
        (task.split(" | ")[0], current_user)
    )
    conn.commit()
    load_tasks()

def complete_task():
    selected = task_list.curselection()
    if not selected:
        return

    task = task_list.get(selected[0])
    cur.execute(
        "UPDATE tasks SET completed=1 WHERE title=? AND user_id=?",
        (task.split(" | ")[0], current_user)
    )
    conn.commit()
    load_tasks()

def load_tasks():
    task_list.delete(0, tk.END)
    cur.execute(
        "SELECT title,priority,completed FROM tasks WHERE user_id=?",
        (current_user,)
    )
    rows = cur.fetchall()

    for r in rows:
        status = "✔" if r[2] else "✘"
        text = f"{r[0]} | {r[1]} | {status}"
        task_list.insert(tk.END, text)

    update_stats()

def search_task():
    keyword = search_entry.get().strip()
    task_list.delete(0, tk.END)
    cur.execute(
        "SELECT title,priority,completed FROM tasks WHERE user_id=? AND title LIKE ?",
        (current_user, "%" + keyword + "%")
    )
    rows = cur.fetchall()
    for r in rows:
        status = "✔" if r[2] else "✘"
        task_list.insert(tk.END, f"{r[0]} | {r[1]} | {status}")

# ---------------- STATS ---------------- #
def update_stats():
    cur.execute("SELECT COUNT(*) FROM tasks WHERE user_id=?", (current_user,))
    total = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM tasks WHERE user_id=? AND completed=1", (current_user,))
    completed = cur.fetchone()[0]
    pending = total - completed
    stats_label.config(text=f"Total: {total}    Completed: {completed}    Pending: {pending}")

# ---------------- DASHBOARD ---------------- #

def dashboard():
    global task_entry, task_list, priority_var, stats_label, search_entry

    dash = tk.Frame(root, bg="#1e1e1e")
    dash.pack(fill="both", expand=True)

    tk.Label(dash, text="Task Manager", fg="#00ffcc", bg="#1e1e1e", font=("Helvetica", 18, "bold")).pack(pady=10)

    # Task entry
    task_entry = tk.Entry(dash, width=40, font=("Helvetica", 12))
    task_entry.pack()

    priority_var = tk.StringVar(value="Medium")
    tk.OptionMenu(dash, priority_var, "Low", "Medium", "High").pack(pady=5)

    tk.Button(dash, text="Add Task", command=add_task, bg="#00cc66", fg="white", width=15).pack(pady=5)

    # Search
    tk.Label(dash, text="Search Tasks", fg="white", bg="#1e1e1e").pack(pady=(10,0))
    search_entry = tk.Entry(dash)
    search_entry.pack()
    tk.Button(dash, text="Search", command=search_task, bg="#0099ff", fg="white", width=15).pack(pady=5)

    # Task list
    task_list = tk.Listbox(dash, width=60)
    task_list.pack(pady=10)

    tk.Button(dash, text="Complete Task", command=complete_task, bg="#ffaa00", fg="white", width=15).pack(pady=2)
    tk.Button(dash, text="Delete Task", command=delete_task, bg="#ff4444", fg="white", width=15).pack(pady=2)

    # Stats
    stats_label = tk.Label(dash, text="Stats", fg="white", bg="#1e1e1e", font=("Helvetica", 12))
    stats_label.pack(pady=10)

    load_tasks()

# ---------------- MAIN WINDOW ---------------- #

root = tk.Tk()
root.title("Advanced To-Do Manager")
root.geometry("500x550")
root.configure(bg="#1e1e1e")

show_login_screen(root)

root.mainloop()

