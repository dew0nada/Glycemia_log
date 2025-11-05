import datetime # For date handling
from datetime import date, timedelta

import tkinter as tk # For UI
from tkinter import messagebox, ttk # For themed widgets
import json # For JSON file handling
import os # For file existence check

# =============================== CONFIG ===============================
FILENAME = "daily_log.json"
FIELDS = {
    "Morning": ["Morning Glycemia", "Morning Insulin", "Morning Glycemia After"],
    "Lunch": ["Glycemia Before Lunch", "Lunch Insulin", "Glycemia After Lunch"],
    "Dinner": ["Glycemia Before Dinner", "Dinner Insulin", "Glycemia After Dinner"],
    "Bedtime": ["Glycemia At Night", "Night Insulin"]
}
FIELD_RULES = {
    "Morning Glycemia": (40, 600, "Check your blood sugar!"),
    "Morning Insulin": (1, 60, "Insulin dose too high or low."),
    "Morning Glycemia After": (40, 600, "Check your blood sugar after breakfast."),
    "Glycemia Before Lunch": (40, 600, ""),
    "Lunch Insulin": (1, 60, ""),
    "Glycemia After Lunch": (40, 600, ""),
    "Glycemia Before Dinner": (40, 600, ""),
    "Dinner Insulin": (1, 60, ""),
    "Glycemia After Dinner": (40, 600, ""),
    "Glycemia At Night": (40, 600, ""),
    "Night Insulin": (1, 60, ""),
}


# Flatten all fields for Today page
ALL_FIELDS = []
for cat_fields in FIELDS.values():
    ALL_FIELDS.extend(cat_fields)

# =============================== FILE HANDLING ===============================
def save_partial_entry(category_fields):
    """Save only the fields the user filled for today, validate ranges."""
    today = str(date.today())
    data = load_data()
    entry = data.get(today, {})  # existing data or empty

    for field in category_fields:
        value_str = entries[field].get().strip()
        if not value_str:
            continue  # skip empty fields

        if not value_str.isdigit():
            messagebox.showerror("Invalid Input",
                                 f"{field} must be a number! You entered '{value_str}'")
            return

        value = int(value_str)
        if field in FIELD_RULES:
            min_val, max_val, msg = FIELD_RULES[field]
            if not (min_val <= value <= max_val):
                messagebox.showerror("Out of Range",
                                     f"{field} = {value}\nAllowed: {min_val} → {max_val}\n{msg}")
                return

        # Save only the filled value
        entry[field] = value

    data[today] = entry
    save_data(data)
    messagebox.showinfo("Saved ✅", f"Data saved for {today}!")

def load_data():
    """Load existing data from the JSON file."""
    if not os.path.exists(FILENAME):
        messagebox.showinfo("No Logs", "No logs written yet.")
        return {}
    with open(FILENAME, "r") as f:
        return json.load(f)

def save_data(data):
    with open(FILENAME, "w") as f:
        json.dump(data, f, indent=4)

# =============================== APP LOGIC ===============================
def show_log_for_entry(entry_widget):
    query = entry_widget.get().strip()
    data = load_data()
    if query in data:
        info = "\n".join(f"{k}: {v}" for k, v in data[query].items())
        messagebox.showinfo(f"Log for {query}", info)
    else:
        messagebox.showinfo("No log ❌", f"No data found for {query}.")

def save_today():
    """Save today’s entry from the input fields with detailed validation."""
    today = str(date.today())
    entry = {}

    for field in ALL_FIELDS:
        value_str = entries[field].get().strip()
        if not value_str.isdigit():
            messagebox.showerror(
                "Invalid Input",
                f"❌ {field} must be a number! You entered: '{value_str}'"
            )
            return
        
        value = int(value_str)
        
        # Check rules
        if field in FIELD_RULES:
            min_val, max_val, msg = FIELD_RULES[field]
            if not (min_val <= value <= max_val):
                messagebox.showerror(
                    "Out of Range",
                    f"❌ {field} is out of range!\n"
                    f"Entered: {value}\nAllowed: {min_val} → {max_val}\n\n{msg}"
                )
                return
        
        entry[field] = value

    # Save to JSON
    data = load_data()
    if today in data:
        overwrite = messagebox.askyesno(
            "Already Exists",
            f"Data for {today} already exists.\nOverwrite it?"
        )
        if not overwrite:
            return

    data[today] = entry
    save_data(data)
    messagebox.showinfo("Saved ✅", f"Data saved for {today}!")

def show_log():
    query = date_entry.get().strip()
    data = load_data()
    if query in data:
        info = "\n".join(f"{k}: {v}" for k, v in data[query].items())
        messagebox.showinfo(f"Log for {query}", info)
    else:
        messagebox.showinfo("No log ❌", f"No data found for {query}.")

def show_week_log():
    data = load_data()
    if not data:
        messagebox.showinfo("No Data", "No logs found yet.")
        return

    today = datetime.date.today()
    current_sunday = today - datetime.timedelta(days=today.weekday() + 1 if today.weekday() != 6 else 0)
    current_category = tk.StringVar(value="Morning")

    win = tk.Toplevel(root)
    win.title("📅 Weekly Log")
    win.geometry("900x500")

    # --- Category buttons ---
    btn_frame = tk.Frame(win)
    btn_frame.pack(pady=10)
    for cat in FIELDS.keys():
        tk.Button(btn_frame, text=cat, width=12,
                  command=lambda c=cat: load_week(current_sunday, c)).pack(side="left", padx=5)

    week_label = tk.Label(win, font=("Arial", 12, "bold"))
    week_label.pack(pady=5)

    table_frame = tk.Frame(win)
    table_frame.pack(fill="both", expand=True)
    table = ttk.Treeview(table_frame, columns=["Date"] + FIELDS["Morning"], show="headings")
    vsb = ttk.Scrollbar(table_frame, orient="vertical", command=table.yview)
    table.configure(yscroll=vsb.set)
    vsb.pack(side="right", fill="y")
    table.pack(fill="both", expand=True)

    for col in table["columns"]:
        table.heading(col, text=col)
        table.column(col, width=130 if col != "Date" else 100, anchor="center")

    nav_frame = tk.Frame(win)
    nav_frame.pack(pady=10)

    def load_week(start_date, category):
        nonlocal current_sunday
        current_sunday = start_date
        current_category.set(category)
        fields = FIELDS[category]

        week_label.config(text=f"Week: {start_date.isoformat()} → {(start_date + timedelta(days=6)).isoformat()}")

        table["columns"] = ["Date"] + fields
        for col in table["columns"]:
            table.heading(col, text=col)
            table.column(col, width=130 if col != "Date" else 100, anchor="center")

        for row in table.get_children():
            table.delete(row)

        week_days = [(start_date + timedelta(days=i)).isoformat() for i in range(7)]
        for d in week_days:
            if d in data:
                values = [str(data[d].get(f, "—")) for f in fields]
                table.insert("", "end", values=(d, *values))
            else:
                table.insert("", "end", values=(d, *["—"] * len(fields)))

    def prev_week():
        load_week(current_sunday - timedelta(days=7), current_category.get())

    def next_week():
        load_week(current_sunday + timedelta(days=7), current_category.get())

    tk.Button(nav_frame, text="◀️ Previous Week", command=prev_week).pack(side="left", padx=10)
    tk.Button(nav_frame, text="Next Week ▶️", command=next_week).pack(side="right", padx=10)

    load_week(current_sunday, "Morning")

def has_today_entry():
    """Check if today's log already exists in the JSON file."""
    data = load_data()                 # get all stored data
    today = str(date.today())          # get today's date (e.g., '2025-11-05')
    return today in data               # True if today is in data, else False

# =============================== UI SETUP ===============================
root = tk.Tk()
root.title("📘 Daily Log App")
root.geometry("360x600")

home_page = tk.Frame(root)
today_log_page = tk.Frame(root)
show_logs_page = tk.Frame(root)
about_page = tk.Frame(root)

if has_today_entry():
    message = "dit"
else:
    message = "nter"


def show_page(page):
    """Hide all pages and show the selected one, and set page-specific geometry."""
    for frame in (home_page, today_log_page, show_logs_page, about_page):
        frame.pack_forget()
    page.pack(fill="both", expand=True)

    # Set different geometry per page
    if page == home_page:
        root.geometry("320x550")
    elif page == today_log_page:
        root.geometry("900x500")
    elif page == show_logs_page:
        root.geometry("850x500")
    elif page == about_page:
        root.geometry("400x400")


# --- HOME PAGE ---
tk.Label(home_page, text="🏠 Home Page", font=("Arial", 16)).pack(pady=15)
tk.Button(home_page, text="📝 E" + message + " Today Log", width=22, command=lambda: show_page(today_log_page)).pack(pady=5)
tk.Button(home_page, text="📂 Show Logs", width=22, command=lambda: show_page(show_logs_page)).pack(pady=5)
tk.Button(home_page, text="ℹ️ About", width=22, command=lambda: show_page(about_page)).pack(pady=5)
tk.Button(home_page, text="❌ Exit", width=22, command=root.quit).pack(pady=5)


# --- TODAY LOG PAGE ---
# =============================== TODAY LOG PAGE ===============================
tk.Label(today_log_page, text="☀️ Enter Logs for Today", font=("Arial", 15)).pack(pady=10)
tk.Label(today_log_page, text="u can e" + message +" all of logs or just for a single period \nuse save 'period' to save em separatly 😊", wraplength=300).pack(pady=10)

# Scrollable frame for all entries
canvas = tk.Canvas(today_log_page, width=300, height=350)
scrollbar = tk.Scrollbar(today_log_page, orient="vertical", command=canvas.yview)
scrollable_frame = tk.Frame(canvas)

scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(
        scrollregion=canvas.bbox("all")
    )
)

canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

# Flatten all fields and create entries
ALL_FIELDS = []
for cat_fields in FIELDS.values():
    ALL_FIELDS.extend(cat_fields)

entries = {}
for field in ALL_FIELDS:
    frame = tk.Frame(scrollable_frame)
    frame.pack(pady=2, fill="x")
    tk.Label(frame, text=field + ":", width=20, anchor="w").pack(side="left", padx=5)
    e = tk.Entry(frame, width=10)
    e.pack(side="right", padx=5)
    entries[field] = e

# --- Buttons per category ---
btn_frame = tk.Frame(today_log_page)
btn_frame.pack(pady=10)

for cat in FIELDS.keys():
    tk.Button(
        btn_frame, text=f"💾 Save {cat}", width=12,
        command=lambda c=cat: save_partial_entry(FIELDS[c])  # call function from App Logic
    ).pack(side="left", padx=5)

tk.Button(today_log_page, text="← Back to Home", command=lambda: show_page(home_page)).pack(pady=15)

# =============================== SHOW LOGS PAGE ===============================
show_logs_page = tk.Frame(root)

tk.Label(show_logs_page, text="📂 Show Logs", font=("Arial", 15)).pack(pady=10)

# --- Button to show weekly logs ---
tk.Button(show_logs_page, text="📅 Show Weekly Logs", width=22, command=show_week_log).pack(pady=5)

# --- Daily log by date ---
tk.Label(show_logs_page, text="📅 Show log for date (YYYY-MM-DD):").pack(pady=5)
date_entry_logs = tk.Entry(show_logs_page, width=18)
date_entry_logs.pack(pady=5)
tk.Button(show_logs_page, text="🔍 Show Log", width=15, command=lambda: show_log_for_entry(date_entry_logs)).pack(pady=5)

# --- Back button ---
tk.Button(show_logs_page, text="← Back to Home", width=15, command=lambda: show_page(home_page)).pack(pady=15)


tk.Button(today_log_page, text="💾 Save Today", width=15, command=save_today).pack(pady=10)
tk.Label(today_log_page, text="📅 Show log for date (YYYY-MM-DD):").pack()
date_entry = tk.Entry(today_log_page, width=18)
date_entry.pack(pady=5)
tk.Button(today_log_page, text="🔍 Show Log", width=15, command=show_log).pack(pady=5)
tk.Button(today_log_page, text="← Back to Home", command=lambda: show_page(home_page)).pack(pady=15)

# --- ABOUT PAGE ---
tk.Label(about_page, text="ℹ️ About This App", font=("Arial", 15)).pack(pady=15)
tk.Label(about_page, text="Bits and bytes with a wink and a cheer, \n \t\tKeeps your daily logs crystal clear!" , wraplength=300).pack(pady=10)
tk.Label(about_page, text="by: SABRI Nada (Dew) \nMade with 💕 Python & Tkinter.\n\nStores daily logs into JSON.\nIncludes weekly summary view!", wraplength=300).pack(pady=10)
tk.Button(about_page, text="← Back to Home", command=lambda: show_page(home_page)).pack(pady=15)

# =============================== START APP ===============================
show_page(home_page)
root.mainloop()
