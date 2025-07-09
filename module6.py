from tkinter import ttk
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import operator
from datetime import datetime
from module1 import run_account
from module3 import get_inventory, get_item_data
from module5 import load_data
from module6_1 import deduplicate_matches, data_treeview_format, dashboard_treeview_format, refresh_treeview, treeview_sort_column
from module6_2 import plot_graph, plot_stat_graphs
from module7 import get_champion_Square, get_champion_LS, get_champion_item
import os
import ast

# --- Main GUI Function ---

def start_gui():
 
    # --- Tkinter Setup ---
    root = tk.Tk()
    root.title("LoL Tracker")

    azure_path = os.path.join(os.path.dirname(__file__), "Azure-ttk-theme-main", "azure.tcl")
    root.tk.call("source", azure_path)
    root.tk.call("set_theme", "light")

    plot_canvas = None

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

    
    current_data_rows = []
    load_data()
    all_data = load_data()


    # --- Dashboard Widgets ---
    default_full_name = 'Game Name + #na1'
    entry_name = tk.Entry(dashboard_tab)
    entry_name.grid(row=0, column=0)
    entry_name.insert(0, default_full_name)
    entry_name.config(fg='grey')

    def on_entry_click(event):
        if entry_name.get() == default_full_name:
            entry_name.delete(0, "end")
            entry_name.config(fg='black')

    def on_focusout(event):
        if entry_name.get() == '':
            entry_name.insert(0, default_full_name)
            entry_name.config(fg='grey')

    entry_name.bind('<FocusIn>', on_entry_click)
    entry_name.bind('<FocusOut>', on_focusout)

    ttk.Label(dashboard_tab, text="Matches:").grid(row=0, column=1)
    entry_matches = ttk.Spinbox(dashboard_tab, from_=1, to=20, width=5)
    entry_matches.grid(row=0, column=2)

    graph_type_var = tk.StringVar(value="Line")
    graph_type_combo = ttk.Combobox(dashboard_tab, textvariable=graph_type_var, values=["Line", "Bar", "Scatter", "Step", "Area", "Stem", "Horizontal Bar", "Boxplot"], state="readonly", width=8)
    graph_type_combo.grid(row=3, column=0)

    stat_type_var = tk.StringVar(value="KDA")
    stat_type_combo = ttk.Combobox(dashboard_tab, textvariable=stat_type_var, values=["KDA", "CS", "KP", "Winrate"], state="readonly", width=8)
    stat_type_combo.grid(row=3, column=1)

    # --- Stats Labels ---
    stat_frame = ttk.Frame(dashboard_tab)
    stat_frame.grid(row=0, column=4, columnspan=4, sticky="nsew")
    lbl_kda = ttk.Label(stat_frame, text="KDA: --")
    lbl_kda.grid(row=0, column=0)
    lbl_cs = ttk.Label(stat_frame, text="CS: --")
    lbl_cs.grid(row=0, column=1)
    lbl_kp = ttk.Label(stat_frame, text="KP: --")
    lbl_kp.grid(row=0, column=2)
    lbl_winrate = ttk.Label(stat_frame, text="Winrate: --")
    lbl_winrate.grid(row=0, column=3)

    # --- Error Label ---
    error_label = tk.Label(root, text="", fg="red")
    error_label.grid(row=5, column=0, columnspan=4, sticky="w")

    # --- Graph/Stat Change Handler ---
    def on_graph_or_stat_change(*args):
        full_name = entry_name.get()
        if '#' in full_name:
            name, tag = full_name.split('#', 1)
        else:
            name = full_name
            tag = 'na1'
        # Always recompute recent using the current matches value
        recent, _ = dashboard_treeview_format(
            all_data, name, tag, entry_matches.get()
        )
        update_graph(name, tag, recent)

    graph_type_var.trace("w", on_graph_or_stat_change)
    stat_type_var.trace("w", on_graph_or_stat_change)
    stat_type_combo.bind("<<ComboboxSelected>>", on_graph_or_stat_change)
    graph_type_combo.bind("<<ComboboxSelected>>", on_graph_or_stat_change)

    # --- Dashboard Treeview ---
    dashboard_columns = ("champion", "kda", "cs", "kp", "win", "match_id", "match_date")
    recent, dashboard_row = dashboard_treeview_format(all_data, default_full_name.split('#')[0], default_full_name.split('#')[1], entry_matches.get())
    match_tree = ttk.Treeview(dashboard_tab, columns=dashboard_columns, show="headings", height=8, selectmode="browse")
    refresh_treeview(match_tree, dashboard_row, dashboard_columns)
    for col in dashboard_columns:
        match_tree.heading(col, text=col.capitalize(),
                        command=lambda _col=col: treeview_sort_column(match_tree, _col, False))
        match_tree.column(col, width=90, anchor="center")
    match_tree.grid(row=4, column=4, rowspan=1, sticky="nsew", padx=10)

    root.grid_columnconfigure(4, weight=1)
    root.grid_rowconfigure(4, weight=1)

    # --- Data Tab ---
    filter_var = tk.StringVar()
    filter_entry = ttk.Entry(data_tab, textvariable=filter_var, width=30)
    filter_entry.grid(row=0, column=0, sticky="w", padx=10, pady=5)
    filter_btn = ttk.Button(data_tab, text="Apply Filter")
    filter_btn.grid(row=0, column=1, sticky="w", padx=5, pady=5)

    column_data = (
        "user", "champion", "kda", "cs", "kp", "win", "duration", "damage", "level", "vision",
        "match_date", "game_type", "patch", "items"
    )
    data_row = data_treeview_format(all_data)
    data_tree = ttk.Treeview(data_tab, columns=column_data, show="headings", height=10)
    refresh_treeview(data_tree, data_row, column_data)
    for col in column_data:
        data_tree.heading(col, text=col.capitalize(),
                        command=lambda _col=col: treeview_sort_column(data_tree, _col, False))
        data_tree.column(col, width=100, anchor="center")
    data_tree.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

    # --- Event Handlers ---

    def pull_data():
        try:
            full_name = entry_name.get()
            if '#' in full_name:
                name, tag = full_name.split('#', 1)
            else:
                name = full_name
                tag = 'na1'
            summary, *_, = run_account(name, tag, entry_matches.get())
            load_data()
            data_row[:] = data_treeview_format(all_data)  # Update data_row with new all_data
            refresh_treeview(data_tree, data_row, column_data)
            recent, dashboard_row = dashboard_treeview_format(all_data, name, tag, entry_matches.get())
            refresh_treeview(match_tree, dashboard_row, dashboard_columns)
            update_graph(name, tag, recent)
            lbl_kda.config(text=f"KDA: {summary['avg_kda']:.2f}")
            lbl_cs.config(text=f"CS: {summary['avg_cs_per_min']:.2f}")
            lbl_kp.config(text=f"KP: {summary['avg_kp']:.2f}%")
            lbl_winrate.config(text=f"Winrate: {summary['win_rate']:.2%}")
        except Exception as e:
            error_label.config(text=f"Error: {e}")

    btn = ttk.Button(dashboard_tab, text="Pull Data", command=pull_data)
    btn.grid(row=0, column=3)

    def update_graph(name, tag, recent):
        stat_list = []
        stat_type = stat_type_var.get()
        if stat_type == "Winrate":
            wins = 0
            for i, row in enumerate(recent, 1):
                if row["win"] in [True, "True", "true", 1, "1"]:
                    wins += 1
                stat_list.append((wins / i) * 100)
        else:
            for row in recent:
                if stat_type == "KDA":
                    deaths = row["deaths"] if row["deaths"] > 0 else 1
                    value = (row["kills"] + row["assists"]) / deaths
                elif stat_type == "CS":
                    value = row["cs"]
                elif stat_type == "KP":
                    value = row["kill_participation"] * 100
                stat_list.append(value)
        plot_graph(stat_list, stat_type, graph_type_var.get(), dashboard_tab, plot_canvas)


    def on_match_select(event):
        selected = data_tree.selection()
        if not selected:
            return
        match_id = selected[0]
        full_row = next((row for row in all_data if str(row["match_id"]) == str(match_id)), None)
        if not full_row:
            error_label.config(text="Match not found in data.")
            return
        champion = full_row["champion"]
        kda = f"{full_row['kills']}/{full_row['deaths']}/{full_row['assists']} ({(full_row['kills']+full_row['assists'])/(full_row['deaths'] if full_row['deaths'] > 0 else 1):.2f})"
        cs = f"{full_row['cs']:.0f} ({full_row['cs_per_min']:.1f}/min)"
        kp = f"{full_row['kill_participation'] * 100:.0f}%"
        win = full_row["win"]
        duration_seconds = int(full_row['duration'])
        minutes = duration_seconds // 60
        seconds = duration_seconds % 60
        duration = f"{minutes}:{seconds:02d}"
        damage = full_row["damage"]
        level = full_row["level"]
        vision = full_row["vision"]
        match_date = full_row["match_date"]
        game_type = full_row["game_type"]
        patch = full_row["patch"]
        items = full_row["items"]

        popup = tk.Toplevel()
        popup.title("Match Details")
        popup.minsize(900, 600)
        popup.maxsize(1200, 900)
        notebook = ttk.Notebook(popup)
        notebook.pack(fill="both", expand=True)
        match_details_tab = ttk.Frame(notebook)
        notebook.add(match_details_tab, text="Final Build")
        timeline_tab = ttk.Frame(notebook)
        notebook.add(timeline_tab, text="Timeline")
        graph_info_tab = ttk.Frame(notebook)
        notebook.add(graph_info_tab, text="Graph Info")

        img_champion = get_champion_Square(champion)
        img_label = ttk.Label(match_details_tab, image=img_champion)
        img_label.image = img_champion
        img_label.pack(pady=5)
        ttk.Label(match_details_tab, text=f"Champion: {champion}", font=("bold")).pack(pady=5)
        ttk.Label(match_details_tab, text=f"KDA: {kda}").pack(pady=5)
        ttk.Label(match_details_tab, text=f"CS: {cs}").pack(pady=5)
        ttk.Label(match_details_tab, text=f"KP: {kp}").pack(pady=5)
        ttk.Label(match_details_tab, text=f"Win: {win}").pack(pady=5)
        ttk.Label(match_details_tab, text=f"Duration: {duration}").pack(pady=5)
        ttk.Label(match_details_tab, text=f"Damage: {damage}").pack(pady=5)
        ttk.Label(match_details_tab, text=f"Level: {level}").pack(pady=5)
        ttk.Label(match_details_tab, text=f"Vision Score: {vision}").pack(pady=5)
        ttk.Label(match_details_tab, text=f"Match Date: {match_date}").pack(pady=5)
        ttk.Label(match_details_tab, text=f"Game Type: {game_type}").pack(pady=5)
        ttk.Label(match_details_tab, text=f"Patch: {patch}").pack(pady=5)
        #ttk.Label(match_details_tab, text=f"Items: {items}").pack(pady=5)

        # Parse items
        if isinstance(items, str):
            try:
                items_list = ast.literal_eval(items)
            except Exception:
                items_list = []
        else:
            items_list = items

        if items_list and len(items_list[0]) == 2:
            items_list = [(ts, item_id, "PURCHASE") for ts, item_id in items_list]

        final_inventory = get_inventory(items_list)
        item_data = get_item_data()
        completed = []
        components = []
        for item_id in final_inventory:
            item = item_data.get(str(item_id))
            if not item:
                continue
            tags = item.get("tags", [])
            if not item.get("into") and item.get("gold", {}).get("purchasable", False) and \
               "Consumable" not in tags and "Trinket" not in tags:
                completed.append(item_id)
            elif "Consumable" not in tags and "Trinket" not in tags:
                components.append(item_id)
        final_display = completed[:6]
        if len(final_display) < 6:
            final_display += components[:6 - len(final_display)]

        ttk.Label(match_details_tab, text="Final Inventory:").pack(pady=5)
        item_frame = ttk.Frame(match_details_tab)
        item_frame.pack(pady=5)
        item_images = []
        for item_id in final_display:
            try:
                img = get_champion_item(str(item_id))
                item_images.append(img)
                lbl = ttk.Label(item_frame, image=img)
                lbl.pack(side="left", padx=2)
            except Exception as e:
                print(f"Failed to load art for {item_id}: {e}")
                lbl = ttk.Label(item_frame, text=str(item_id))
                lbl.pack(side="left", padx=2)
        popup.item_images = item_images

        ttk.Label(timeline_tab, text="Item Timeline:").pack()

        # --- Item Timeline Visualization ---
        # items_list is already parsed above and contains (timestamp, item_id, action)
        items_per_row = 10  # Number of items per row
        row_height = 125    # Increased for more space
        icon_size = 48
        spacing = 100

        if items_list:
            sorted_items = sorted(items_list, key=lambda x: x[0])
            num_rows = (len(sorted_items) + items_per_row - 1) // items_per_row
            canvas_width = max(800, items_per_row * spacing + 40)
            canvas_height = max(120, num_rows * row_height + 40)
            timeline_canvas = tk.Canvas(timeline_tab, bg="white", height=canvas_height, width=canvas_width)
            timeline_canvas.pack(fill="x", padx=10, pady=10)

            positions = []  # Store icon center positions for arrows

            for idx, (ts, item_id, action) in enumerate(sorted_items):
                if action not in ("PURCHASE", "SELL"):
                    continue
                row = idx // items_per_row
                col = idx % items_per_row
                x = 10 + col * spacing
                y = 10 + row * row_height
                # Get item art
                try:
                    img = get_champion_item(str(item_id))
                except Exception:
                    img = None
                # Draw item icon
                if img:
                    timeline_canvas.create_image(x, y, anchor="nw", image=img)
                    if not hasattr(timeline_canvas, "images"):
                        timeline_canvas.images = []
                    timeline_canvas.images.append(img)
                # Save center position for arrows
                positions.append((x + icon_size // 2, y + icon_size // 2, row, col, ts))
                # Draw timestamp below icon
                seconds = int(ts // 1000)
                minutes = seconds // 60
                sec = seconds % 60
                ts_str = f"{minutes}:{sec:02d}"
                timeline_canvas.create_text(
                    x + icon_size // 2, y + icon_size + 15,
                    text=ts_str, font=("Arial", 9, "bold"), anchor="n"
                )
                # Draw action below timestamp
                timeline_canvas.create_text(
                    x + icon_size // 2, y + icon_size + 28,
                    text=action, font=("Arial", 7), anchor="n"
                )

            # Draw arrows between icons in the same row
            for i in range(len(positions) - 1):
                x1, y1, row1, col1, ts1 = positions[i]
                x2, y2, row2, col2, ts2 = positions[i + 1]
                if row1 == row2 and ts1 != ts2:  # Only connect if not grouped
                    timeline_canvas.create_line(
                        x1 + icon_size // 2, y1, x2 - icon_size // 2, y2,
                        arrow=tk.LAST, width=2, fill="#888"
                    )

        # When creating the popup:
        graph_type_var = tk.StringVar(value="Bar")
        graph_type_combo = ttk.Combobox(graph_info_tab, textvariable=graph_type_var, values=["Bar", "Line", "Scatter"], state="readonly", width=10)
        graph_type_combo.pack(anchor="w", padx=10, pady=(0,10))

        stat_var = tk.StringVar(value="KDA")
        stat_combo = ttk.Combobox(graph_info_tab, textvariable=stat_var, values=["KDA", "CS", "KP", "Winrate", "Damage", "Vision/min"], state="readonly")
        stat_combo.pack(anchor="w", padx=10, pady=(10,0))

        def update_stat_graphs(*args):
            plot_stat_graphs(graph_info_tab, popup, full_row, all_data, stat_var.get(), graph_type_var.get())

        graph_type_combo.bind("<<ComboboxSelected>>", update_stat_graphs)
        stat_combo.bind("<<ComboboxSelected>>", update_stat_graphs)

        # Initial plot
        plot_stat_graphs(graph_info_tab, popup, full_row, all_data, stat_var.get(), graph_type_var.get())

    data_tree.bind("<<TreeviewSelect>>", on_match_select)

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
        f_data = deduplicate_matches(all_data)
        for op_str, op_func in ops.items():
            if op_str in query:
                try:
                    field, value = query.split(op_str, 1)
                    field = field.strip()
                    value = value.strip()
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
        else:
            filtered_data = []
            for row in f_data:
                for v in row.values():
                    if query.lower() in str(v).lower():
                        filtered_data.append(row)
                        break
        # Clear and repopulate the treeview
        # Clear and repopulate the treeview
        for row in data_tree.get_children():
            data_tree.delete(row)
        for row in filtered_data:
            user = f"{row['summoner_id']}#{row['tag_line']}" if row['tag_line'] else row['summoner_id']
            kda = f"{row['kills']}/{row['deaths']}/{row['assists']} ({(row['kills']+row['assists'])/(row['deaths'] if row['deaths'] > 0 else 1):.2f})"
            cs = f"{row['cs']:.0f} ({row['cs_per_min']:.1f}/min)"
            kp = f"{row['kill_participation'] * 100:.0f}%"
            duration_seconds = int(row['duration'])
            minutes = duration_seconds // 60
            seconds = duration_seconds % 60
            duration = f"{minutes}:{seconds:02d}"
            items = row.get("items", "No items")
            data_tree.insert("", "end", iid=row["match_id"], values=(
                user, row["champion"], kda, cs, kp, row["win"], duration, row["damage"], row["level"], row["vision"],
                row["match_date"], row["game_type"], row["patch"], items
            ))
    filter_btn.config(command=apply_filter)

    # --- Dark Mode ---
    def change_theme():
        if root.tk.call("ttk::style", "theme", "use") == "azure-dark":
            root.tk.call("set_theme", "light")
        else:
            root.tk.call("set_theme", "dark")

    theme_var = tk.BooleanVar()
    switch = ttk.Checkbutton(setting_tab, text='Dark mode', style='Switch.TCheckbutton', variable=theme_var, command=change_theme)
    switch.grid(row=0, column=0, columnspan=4, sticky="w")

    # --- Show a blank graph at startup ---
    #plot_graph([], stat_type_var.get(), graph_type_var.get(),None,dashboard_tab ,plot_canvas)

    root.mainloop()