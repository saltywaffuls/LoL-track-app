from tkinter import ttk
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from main import run_account
from module5 import load_data
import os

root = tk.Tk()
root.title("LoL Tracker")

azure_path = os.path.join(os.path.dirname(__file__), "Azure-ttk-theme-main", "azure.tcl")
root.tk.call("source", azure_path)

# Set the initial theme
root.tk.call("set_theme", "light")

plot_canvas = None  # Global reference to the plot canvas

def pull_data():
    try:
        full_name = entry_name.get()
        if '#' in full_name:
            name, tag = full_name.split('#', 1)
        else:
            name = full_name
            tag = 'na1'  # default

        summary, _, _, _ = run_account(name, tag, entry_matches.get())
        lbl_kda.config(text=f"KDA: {summary['avg_kda']:.2f}")
        lbl_cs.config(text=f"CS: {summary['avg_cs_per_min']:.2f}")
        lbl_kp.config(text=f"KP: {summary['avg_kp']:.2%}")
        lbl_winrate.config(text=f"Winrate: {summary['win_rate']:.2%}")

        update_kda_graph(name, tag)  # Pass name and tag

    except Exception as e:
        error_label.config(text=f"Error: {e}")

def update_kda_graph(name, tag):
    all_matches = load_data()
    filtered = [row for row in all_matches if row["summoner_id"].lower() == name.lower() and row["tag_line"].lower() == tag.lower()]
    filtered.sort(key=lambda x: x["match_date"], reverse=True)
    num_matches = int(entry_matches.get())
    recent = filtered[:num_matches]
    kda_list = []
    for row in recent:
        deaths = row["deaths"] if row["deaths"] > 0 else 1
        kda = (row["kills"] + row["assists"]) / deaths
        kda_list.append(kda)
    plot_kda(kda_list)

def on_entry_click(event):
    if entry_name.get() == 'Game Name + #na1':
        entry_name.delete(0, "end")
        entry_name.config(fg='black')

def on_focusout(event):
    if entry_name.get() == '':
        entry_name.insert(0, 'Game Name + #na1')
        entry_name.config(fg='grey')

entry_name = tk.Entry(root)
entry_name.grid(row=0, column=0)
entry_name.insert(0, 'Game Name + #na1')
entry_name.config(fg='grey')
entry_name.bind('<FocusIn>', on_entry_click)
entry_name.bind('<FocusOut>', on_focusout)

full_name = entry_name.get()
if '#' in full_name:
    name, tag = full_name.split('#', 1)
else:
    name = full_name
    tag = 'na1'  # default

# Matches input
ttk.Label(root, text="Matches:").grid(row=0, column=1)
entry_matches = ttk.Spinbox(root, from_=1, to=20, width=5)
entry_matches.grid(row=0, column=2)

# Pull Data Button
btn = ttk.Button(root, text="Pull Data", command=pull_data)
btn.grid(row=0, column=3)

# dark mode feture
 #Pack a big frame so, it behaves like the window background
big_frame = ttk.Frame(root)
big_frame.grid(row=0, column=4, columnspan=4, sticky="nsew")


def change_theme():
    # NOTE: The theme's real name is azure-<mode>
    if root.tk.call("ttk::style", "theme", "use") == "azure-dark":
        # Set light theme
        root.tk.call("set_theme", "light")
    else:
        # Set dark theme
        root.tk.call("set_theme", "dark")

# Create a BooleanVar for the switch
theme_var = tk.BooleanVar()
# Remember, you have to use ttk widgets
switch = ttk.Checkbutton(big_frame, text='Dark mode', style='Switch.TCheckbutton', variable=theme_var, command=change_theme)
switch.grid(row=0, column=0, columnspan=4, sticky="w")

stat_frame = ttk.Frame(root)
stat_frame.grid(row=2, column=0, columnspan=4, sticky="nsew")

# Placeholder for stats labels
lbl_kda = ttk.Label(stat_frame, text="KDA: --")
lbl_kda.grid(row=0, column=0)

lbl_cs = ttk.Label(stat_frame, text="CS: --")
lbl_cs.grid(row=0, column=1)

lbl_kp = ttk.Label(stat_frame, text="KP: --")
lbl_kp.grid(row=0, column=2)

lbl_winrate = ttk.Label(stat_frame, text="Winrate: --")
lbl_winrate.grid(row=0, column=3)

# Function to plot KDA over recent games
def plot_kda(kda_list):
    global plot_canvas
    if plot_canvas is not None:
        plot_canvas.get_tk_widget().destroy()
        plot_canvas = None

    fig, ax = plt.subplots(figsize=(7, 4), dpi=100)
    x = range(1, len(kda_list)+1)
    ax.plot(x, kda_list, marker="o", color="skyblue", linewidth=2, markersize=8)
    ax.set_title("KDA Over Recent Games")
    ax.set_xlabel("Game #", fontsize=12)
    ax.set_ylabel("KDA", fontsize=12)
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.set_ylim(bottom=0)  # Start y-axis at 0

    # Show KDA values as labels on each point
    for i, v in enumerate(kda_list):
        ax.text(x[i], v + 0.1, f"{v:.2f}", ha='center', fontsize=9, color='blue')

    fig.tight_layout()

    plot_canvas = FigureCanvasTkAgg(fig, master=root)
    plot_canvas.get_tk_widget().grid(row=3, column=0, columnspan=4, pady=10)
    plot_canvas.draw()


error_label = tk.Label(root, text="", fg="red")
error_label.grid(row=5, column=0, columnspan=4, sticky="w")


root.mainloop()
