from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from tkinter import ttk
from module6_1 import deduplicate_matches


def plot_graph(stat_list, stat_type, graph_type, dashboard_tab, plot_canvas=None):
    # Safely destroy the previous canvas if it exists
    if plot_canvas is not None:
        try:
            plot_canvas.get_tk_widget().destroy()
        except Exception:
            pass
        plot_canvas = None
    
    fig, ax = plt.subplots(figsize=(7, 4), dpi=100)
    
    # Handle empty data case
    if not stat_list:
        # Create empty plot with proper labels
        ax.set_title(f"{stat_type} Over Recent Games")
        ax.set_xlabel("Game #", fontsize=12)
        ax.set_ylabel(
            "Winrate (%)" if stat_type == "Winrate"
            else "KP (%)" if stat_type == "KP"
            else stat_type,
            fontsize=12
        )
        ax.grid(True, linestyle='--', alpha=0.6)
        ax.set_xlim(0, 10)  # Default x range
        ax.set_ylim(0, 10)  # Default y range
        ax.text(5, 5, "No data available", ha='center', va='center', fontsize=14, color='gray')
    else:
        # Normal plotting with data
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
        
        # Add value labels on data points
        for i, v in enumerate(stat_list):
            ax.text(x[i], v + 0.1, f"{v:.2f}", ha='center', fontsize=9, color='blue')
    
    fig.tight_layout()
    plot_canvas = FigureCanvasTkAgg(fig, master=dashboard_tab)
    plot_canvas.get_tk_widget().grid(row=4, column=0, columnspan=4, pady=10)
    plot_canvas.draw()
    
    return plot_canvas  # Return the canvas so it can be stored




# --- Stats Comparison Graphs in Match Details Popup ---
stats_to_plot = [
            ("KDA", lambda row: (row["kills"] + row["assists"]) / (row["deaths"] if row["deaths"] > 0 else 1)),
            ("CS", lambda row: row["cs"]),
            ("KP", lambda row: row["kill_participation"] * 100),
            ("Winrate", lambda row: 100 if row["win"] in [True, "True", "true", 1, "1"] else 0),
            ("Damage", lambda row: row["damage"]),
            ("Vision/min", lambda row: row.get("vision", 0) / (row["duration"] / 60) if row.get("duration", 0) else 0),
            # Add more stats as needed
        ]

def plot_stat_graphs(graph_info_tab, popup, full_row, all_data, selected_stat, graph_type):
            # Remove all widgets except the combobox and label
            for widget in graph_info_tab.winfo_children():
                if isinstance(widget, ttk.Combobox) or (isinstance(widget, ttk.Label) and widget.cget("text") == "Graph Type:"):
                    continue
                widget.destroy()

            champ = full_row["champion"]
            # Get all games for this champion, sorted by match_date (oldest to newest)
            champ_games = deduplicate_matches([row for row in all_data if row["champion"] == champ])
            champ_games.sort(key=lambda r: r.get("match_date", ""))

            # Find the index of the selected match
            selected_idx = next((i for i, row in enumerate(champ_games) if str(row["match_id"]) == str(full_row["match_id"])), None)

            for stat_name, stat_func in stats_to_plot:
                if stat_name != selected_stat:
                    continue
                stat_values = [stat_func(row) for row in champ_games]
                x = list(range(1, len(stat_values) + 1))
                # graph_type = graph_type_var.get()

                avg_value = sum(stat_values) / len(stat_values) if stat_values else 0

                fig, ax = plt.subplots(figsize=(max(4, len(stat_values)), 3), dpi=100)

                # Plot all games
                if graph_type == "Bar":
                    bars = ax.bar(x, stat_values, color=["#F5A623" if i == selected_idx else "#4A90E2" for i in range(len(stat_values))])
                elif graph_type == "Line":
                    ax.plot(x, stat_values, color="#4A90E2", marker="o")
                    ax.plot([x[selected_idx]], [stat_values[selected_idx]], marker="o", color="#F44336", markersize=12)  # Highlight selected
                elif graph_type == "Scatter":
                    ax.scatter(x, stat_values, color=["#F44336" if i == selected_idx else "#4A90E2" for i in range(len(stat_values))], s=80)
                else:
                    ax.plot(x, stat_values, color="#4A90E2", marker="o")
                    ax.plot([x[selected_idx]], [stat_values[selected_idx]], marker="o", color="#F44336", markersize=12)

                # Calculate account-wide average for the selected stat
                account_stat_values = [stat_func(row) for row in deduplicate_matches(all_data)]
                account_avg = sum(account_stat_values) / len(account_stat_values) if account_stat_values else 0

                # Plot average line
                if stat_name == "CS":
                    cs_per_min_values = [row.get("cs_per_min", 0) for row in champ_games]
                    avg_cspm = sum(cs_per_min_values) / len(cs_per_min_values) if cs_per_min_values else 0
                    # Champion average
                    ax.axhline(avg_value, color="green", linestyle="--", linewidth=2, label=f"Avg: {avg_value:.2f} ({avg_cspm:.2f}/min)")
                    # Account-wide average
                    # Calculate account-wide cs_per_min
                    all_cs_per_min = [row.get("cs_per_min", 0) for row in deduplicate_matches(all_data)]
                    account_avg_cspm = sum(all_cs_per_min) / len(all_cs_per_min) if all_cs_per_min else 0
                    ax.axhline(account_avg, color="orange", linestyle=":", linewidth=2, label=f"Account Avg: {account_avg:.2f} ({account_avg_cspm:.2f}/min)")
                else:
                    ax.axhline(avg_value, color="green", linestyle="--", linewidth=2, label=f"Avg: {avg_value:.2f}")
                    ax.axhline(account_avg, color="orange", linestyle=":", linewidth=2, label=f"Account Avg: {account_avg:.2f}")
                ax.legend(loc="upper right", fontsize=9)

                # Annotate values
                for i, v in enumerate(stat_values):
                    if stat_name == "CS":
                        cs = int(champ_games[i].get("cs", 0))
                        cspm = champ_games[i].get("cs_per_min", 0)
                        label = f"{cs} ({cspm:.1f})"
                    elif stat_name == "KDA":
                        kills = champ_games[i].get("kills", 0)
                        deaths = champ_games[i].get("deaths", 0)
                        assists = champ_games[i].get("assists", 0)
                        kda_val = (kills + assists) / (deaths if deaths > 0 else 1)
                        label = f"{kills}/{deaths}/{assists} ({kda_val:.2f})"
                    else:
                        label = f"{v:.2f}"
                    ax.text(x[i], v, label, ha='center', va='bottom', fontsize=9, color="#F44336" if i == selected_idx else "blue")

                ax.set_title(f"{stat_name} for {champ} ({len(stat_values)} games)")
                ax.set_xlabel("Game # (oldest to newest)")
                ax.set_ylabel(stat_name)
                ax.set_ylim(bottom=0)
                ax.grid(True, linestyle='--', alpha=0.5)
                fig.tight_layout()
                canvas = FigureCanvasTkAgg(fig, master=graph_info_tab)
                canvas.get_tk_widget().pack(side="top", fill="both", expand=True, padx=10, pady=10)
                canvas.draw()
                # plt.close(fig)  # Removed to prevent issues if the figure is accessed again
