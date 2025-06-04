from tkinter import ttk
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from main import run_account
import os

root = tk.Tk()
root.title("LoL Tracker")

azure_path = os.path.join(os.path.dirname(__file__), "Azure-ttk-theme-main", "azure.tcl")
root.tk.call("source", azure_path)

# Set the initial theme
root.tk.call("set_theme", "light")

def pull_data():
    full_name = entry_name.get()
    if '#' in full_name:
        name, tag = full_name.split('#', 1)
    else:
        name = full_name
        tag = 'na1'  # default

    summary, level, icon, stats = run_account(name, tag, entry_matches.get())
    lbl_kda.config(text=f"KDA: {summary['avg_kda']:.2f}")
    lbl_cs.config(text=f"CS: {summary['avg_cs_per_min']:.2f}")
    lbl_kp.config(text=f"KP: {summary['avg_kp']:.2%}")
    lbl_winrate.config(text=f"Winrate: {summary['win_rate']:.2%}")

    # Get KDA for each match
    kda_list = [s.get("kda", 0) for s in stats]
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

ttk.Label(root, text="Matches:").grid(row=0, column=1)
entry_matches = ttk.Spinbox(root, from_=1, to=20, width=5)
entry_matches.grid(row=0, column=2)

# Pull Data Button
btn = ttk.Button(root, text="Pull Data", command=pull_data)
btn.grid(row=0, column=3)

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


def plot_kda(kda_list):
    fig, ax = plt.subplots(figsize=(4, 2), dpi=100)
    ax.plot(kda_list, marker="o", color="skyblue")
    ax.set_title("KDA Over Recent Games")
    ax.set_xlabel("Game #")
    ax.set_ylabel("KDA")
    ax.grid(True)

    # Embed the plot in Tkinter
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.get_tk_widget().grid(row=3, column=0, columnspan=4, pady=10)
    canvas.draw()

root.mainloop()
