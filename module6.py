from tkinter import ttk
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import operator
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

notebook = ttk.Notebook(root)
notebook.grid(row=0, column=0, columnspan=4, sticky="nsew")

dashboard_tab = ttk.Frame(notebook)
data_tab = ttk.Frame(notebook)
graphs_tab = ttk.Frame(notebook)
setting_tab = ttk.Frame(notebook)

notebook.add(dashboard_tab, text="Dashboard")
notebook.add(data_tab, text="Data")
notebook.add(graphs_tab, text="Graphs")
notebook.add(setting_tab, text="Settings")

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
        lbl_kp.config(text=f"KP: {summary['avg_kp']:.2f}%")
        lbl_winrate.config(text=f"Winrate: {summary['win_rate']:.2%}")

        update_graph(name, tag)  # Pass name and tag

    except Exception as e:
        error_label.config(text=f"Error: {e}")

def update_graph(name, tag):
    all_matches = load_data()
    filtered = [row for row in all_matches if row["summoner_id"].lower() == name.lower() and row["tag_line"].lower() == tag.lower()]
    filtered.sort(key=lambda x: x["match_date"], reverse=True)

    # Remove duplicates by match_id, keeping the first occurrence (most recent)
    unique_filtered = deduplicate_matches(all_matches)

    num_matches = int(entry_matches.get())
    recent = unique_filtered[:num_matches]

    # Clear previous rows
    for row in match_tree.get_children():
        match_tree.delete(row)

    # Add new rows
    for row in recent:
        deaths = row["deaths"] if row["deaths"] > 0 else 1
        kda = f"{row['kills']}/{row['deaths']}/{row['assists']} ({(row['kills']+row['assists'])/deaths:.2f})"
        cs = f"{row['cs']:.0f} ({row['cs_per_min']:.1f}/min)"
        kp = f"{row['kill_participation']*100:.0f}%"
        win = "Win" if row["win"] else "Loss"
        match_tree.insert("", "end", values=(
            row["champion"], kda, cs, kp, win, row["match_id"], row["match_date"]
        ))

    stat_list = []
    stat_type = stat_type_var.get()
    if stat_type == "Winrate":
        # Calculate cumulative winrate after each game
        wins = 0
        for i, row in enumerate(recent, 1):
            if row["win"] in [True, "True", "true", 1, "1"]:
                wins += 1
            stat_list.append((wins / i) * 100)  # as percent
    else:
        for row in recent:
            if stat_type == "KDA":
                deaths = row["deaths"] if row["deaths"] > 0 else 1
                value = (row["kills"] + row["assists"]) / deaths
            elif stat_type == "CS":
                value = row["cs"]
            elif stat_type == "KP":
                value = row["kill_participation"] * 100  # percent
            stat_list.append(value)
    plot_graph(stat_list, stat_type, graph_type_var.get())

# Function to plot the graph based on the selected stat type and graph type
def plot_graph(stat_list, stat_type="KDA", graph_type="Line"):
    global plot_canvas
    if plot_canvas is not None:
        plot_canvas.get_tk_widget().destroy()
        plot_canvas = None

    fig, ax = plt.subplots(figsize=(7, 4), dpi=100)
    x = range(1, len(stat_list)+1)
    if graph_type == "Line":
        ax.plot(x, stat_list, marker="o", color="skyblue", linewidth=2, markersize=8)
    elif graph_type == "Bar":
        ax.bar(x, stat_list, color="skyblue")
    elif graph_type == "Scatter":
        ax.scatter(x, stat_list, color="skyblue", s=80)
    elif graph_type == "Step":
        ax.step(x, stat_list, where='mid', color="skyblue", linewidth=2)
    elif graph_type == "Area":
        ax.fill_between(x, stat_list, color="skyblue", alpha=0.4)
        ax.plot(x, stat_list, color="skyblue", linewidth=2)
    elif graph_type == "Stem":
        ax.stem(x, stat_list, linefmt='skyblue', markerfmt='bo', basefmt=" ")
    elif graph_type == "Horizontal Bar":
        ax.barh(x, stat_list, color="skyblue")
    elif graph_type == "Boxplot":
        ax.boxplot(stat_list, vert=True)
    ax.set_title(f"{stat_type} Over Recent Games")
    ax.set_xlabel("Game #", fontsize=12)
    ax.set_ylabel(
        "Winrate (%)" if stat_type == "Winrate"
        else "KP (%)" if stat_type == "KP"
        else stat_type,
        fontsize=12
    )
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.set_ylim(bottom=0)

    for i, v in enumerate(stat_list):
        ax.text(x[i], v + 0.1, f"{v:.2f}", ha='center', fontsize=9, color='blue')

    fig.tight_layout()
    plot_canvas = FigureCanvasTkAgg(fig, master=dashboard_tab)
    plot_canvas.get_tk_widget().grid(row=4, column=0, columnspan=4, pady=10)
    plot_canvas.draw()

def on_entry_click(event):
    if entry_name.get() == 'Game Name + #na1':
        entry_name.delete(0, "end")
        entry_name.config(fg='black')


def on_tab_changed(event):
    selected_tab = event.widget.select()
    tab_text = event.widget.tab(selected_tab, "text")
    if tab_text == "Data":
        data_tab_load()

notebook.bind("<<NotebookTabChanged>>", on_tab_changed)

def on_focusout(event):
    if entry_name.get() == '':
        entry_name.insert(0, 'Game Name + #na1')
        entry_name.config(fg='grey')

def on_match_select(event):
    selected = data_tree.selection()
    if not selected:
        return
    values = data_tree.item(selected[0])['values']
    # Adjust indices if needed based on your column order
    items = values[column_data.index("items")]
    timestamp = values[column_data.index("timestamp")]
    tk.messagebox.showinfo("Match Details", f"Items: {items}\nTimestamp: {timestamp}")

# Function to handle changes in graph or stat type
def on_graph_or_stat_change(*args):
    full_name = entry_name.get()
    if '#' in full_name:
        name, tag = full_name.split('#', 1)
    else:
        name = full_name
        tag = 'na1'
    update_graph(name, tag)


def data_tab_load():
    """
    Load data into the data tab Treeview.
    This function can be called when the data tab is selected.
    """
    data = load_data()

   #filter by match_id
    f_data = deduplicate_matches(data)

    for row in data_tree.get_children():
        data_tree.delete(row)

    for row in f_data:
        user = f"{row['summoner_id']}#{row['tag_line']}" if row['tag_line'] else row['summoner_id']
        kda = f"{row['kills']}/{row['deaths']}/{row['assists']} ({(row['kills']+row['assists'])/(row['deaths'] if row['deaths'] > 0 else 1):.2f})"
        cs = f"{row['cs']:.0f} ({row['cs_per_min']:.1f}/min)"
        kp = f"{row["kill_participation"] * 100:.0f}%"
        duration = f"{int(row['duration']) // 60}:{int(row['duration']) % 60:02d}"
        items = row.get("items", "No items")
        data_tree.insert("", "end", values=(
            user, row["champion"], kda, cs, kp, row["win"], duration, row["damage"], row["level"], row["vision"],
            row["match_date"], row["game_type"], row["patch"], items
        ))

def treeview_sort_column(tree, col, reverse):
    data = [(tree.set(k, col), k) for k in tree.get_children('')]
    # Try to convert to float for numeric columns, else sort as string
    try:
        data.sort(key=lambda t: float(t[0].replace('%','').replace(',','')), reverse=reverse)
    except ValueError:
        data.sort(key=lambda t: t[0], reverse=reverse)
    for index, (val, k) in enumerate(data):
        tree.move(k, '', index)
    # Reverse sort next time
    tree.heading(col, command=lambda: treeview_sort_column(tree, col, not reverse))

def apply_filter():
    query = filter_var.get().strip()
    ops = {
        "<": operator.lt,
        "<=": operator.le,
        ">": operator.gt,
        ">=": operator.ge,
        "=": operator.eq,
        "!=": operator.ne,
    }

    #filter by match_id
    f_data= deduplicate_matches(load_data())

    # Advanced filter: cs < 7, kills > 10, etc.
    for op_str, op_func in ops.items():
        if op_str in query:
            try:
                # Split the query into field and value
                field, value = query.split(op_str, 1)
                field = field.strip()
                value = value.strip()
                  # Convert value to float if possible
                try:
                    value = float(value)
                except ValueError:
                    pass
                filtered_data = []
                for row in f_data:
                    row_value = row.get(field)
                    if row_value is None:
                        continue
                    try:
                        if isinstance(value, float):
                            row_value = float(row_value)
                    except Exception:
                        pass
                    if op_func(row_value, value):
                        filtered_data.append(row)
                break
            except Exception:
                error_label.config(text=f"Invalid filter query: {query}")
                return
    # Simple search: look for the query in any field (case-insensitive)
    else:
        filtered_data = []
        for row in f_data:
            for v in row.values():
                if query.lower() in str(v).lower():
                    filtered_data.append(row)
                    break

    # Update the data_tree with filtered results
    for row in data_tree.get_children():
        data_tree.delete(row)
    for row in filtered_data:
        user = f"{row['summoner_id']}#{row['tag_line']}" if row['tag_line'] else row['summoner_id']
        kda = f"{row['kills']}/{row['deaths']}/{row['assists']} ({(row['kills']+row['assists'])/(row['deaths'] if row['deaths'] > 0 else 1):.2f})"
        cs = f"{row['cs']:.0f} ({row['cs_per_min']:.1f}/min)"
        kp = f"{row["kill_participation"] * 100:.0f}%"
        duration = f"{int(row['duration']) // 60}:{int(row['duration']) % 60:02d}"
        items = row.get("items", "No items")
        data_tree.insert("", "end", values=(
            user, row["champion"], kda, cs, kp, row["win"], duration, row["damage"], row["level"], row["vision"],
            row["match_date"], row["game_type"], row["patch"], items
        ))
    

def deduplicate_matches(matches):
    """Remove duplicate matches by match_id, keeping the first occurrence."""
    seen_ids = set()
    unique_matches = []
    for row in matches:
        if row["match_id"] not in seen_ids:
            unique_matches.append(row)
            seen_ids.add(row["match_id"])
    return unique_matches

entry_name = tk.Entry(dashboard_tab)
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
ttk.Label(dashboard_tab, text="Matches:").grid(row=0, column=1)
entry_matches = ttk.Spinbox(dashboard_tab, from_=1, to=20, width=5)
entry_matches.grid(row=0, column=2)

# Graph and Stat Type inputs
graph_type_var = tk.StringVar(value="Line")
graph_type_combo = ttk.Combobox(dashboard_tab, textvariable=graph_type_var, values=["Line", "Bar", "Scatter", "Step", "Area", "Stem", "Horizontal Bar", "Boxplot"], state="readonly", width=8)
graph_type_combo.grid(row=3, column=0)

stat_type_var = tk.StringVar(value="KDA")
stat_type_combo = ttk.Combobox(dashboard_tab, textvariable=stat_type_var, values=["KDA", "CS", "KP", "Winrate"], state="readonly", width=8)
stat_type_combo.grid(row=3, column=1)

# Pull Data Button
btn = ttk.Button(dashboard_tab, text="Pull Data", command=pull_data)
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
switch = ttk.Checkbutton(setting_tab, text='Dark mode', style='Switch.TCheckbutton', variable=theme_var, command=change_theme)
switch.grid(row=0, column=0, columnspan=4, sticky="w")

stat_frame = ttk.Frame(dashboard_tab)
stat_frame.grid(row=0, column=4, columnspan=4, sticky="nsew")

# Placeholder for stats labels
lbl_kda = ttk.Label(stat_frame, text="KDA: --")
lbl_kda.grid(row=0, column=0)

lbl_cs = ttk.Label(stat_frame, text="CS: --")
lbl_cs.grid(row=0, column=1)

lbl_kp = ttk.Label(stat_frame, text="KP: --")
lbl_kp.grid(row=0, column=2)

lbl_winrate = ttk.Label(stat_frame, text="Winrate: --")
lbl_winrate.grid(row=0, column=3)

# Error label for displaying errors
error_label = tk.Label(root, text="", fg="red")
error_label.grid(row=5, column=0, columnspan=4, sticky="w")

graph_type_var.trace("w", on_graph_or_stat_change)
stat_type_var.trace("w", on_graph_or_stat_change)
stat_type_combo.bind("<<ComboboxSelected>>", on_graph_or_stat_change)
graph_type_combo.bind("<<ComboboxSelected>>", on_graph_or_stat_change)

# Create a Treeview to display match data
columns = ("champion", "kda", "cs", "kp", "win", "match_id", "match_date")
match_tree = ttk.Treeview(dashboard_tab, columns=columns, show="headings", height=8, selectmode="browse")
for col in columns:
    match_tree.heading(col, text=col.capitalize(),
                      command=lambda _col=col: treeview_sort_column(match_tree, _col, False))
    match_tree.column(col, width=90, anchor="center")
match_tree.grid(row=4, column=4, rowspan=1, sticky="nsew", padx=10)

root.grid_columnconfigure(4, weight=1)
root.grid_rowconfigure(4, weight=1)

filter_var = tk.StringVar()
filter_entry = ttk.Entry(data_tab, textvariable=filter_var, width=30)
filter_entry.grid(row=0, column=0, sticky="w", padx=10, pady=5)

filter_btn = ttk.Button(data_tab, text="Apply Filter", command=apply_filter)
filter_btn.grid(row=0, column=1, sticky="w", padx=5, pady=5)

# data tab Treeview
column_data = (
    "user", "champion", "kda", "cs", "kp", "win", "duration", "damage", "level", "vision",
    "match_date", "game_type", "patch", "items"
)
data_tree = ttk.Treeview(data_tab, columns=column_data, show="headings", height=10)
for col in column_data:
    data_tree.heading(col, text=col.capitalize(),
                      command=lambda _col=col: treeview_sort_column(data_tree, _col, False))
    data_tree.column(col, width=100, anchor="center")
data_tree.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

data_tree.bind("<<TreeviewSelect>>", on_match_select)

# Show a blank graph at startup
plot_graph([], stat_type_var.get(), graph_type_var.get())

root.mainloop()
