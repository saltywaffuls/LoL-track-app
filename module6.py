import tkinter as tk
from main import run_account

def pull_data():
    
    info = run_account(entry_name.get(), entry_tag_line.get(), entry_matches.get())  # Replace "NA1" with the appropriate tag line or region if needed

    lbl_kda.config(text=f"KDA: {info[0]['avg_kda']:.2f}")
    lbl_cs.config(text=f"CS: {info[0]['avg_cs_per_min']:.2f}")
    lbl_winrate.config(text=f"Winrate: {info[0]['win_rate']:.2%}")


root = tk.Tk()
root.title("LoL Tracker")

# Summoner Name Input
tk.Label(root, text="Summoner Name:").grid(row=0, column=0)
entry_name = tk.Entry(root)
entry_name.grid(row=1, column=0)

tk.Label(root, text="Tag Line:").grid(row=0, column=1)
entry_tag_line = tk.Entry(root) 
entry_tag_line.grid(row=1, column=1)

tk.Label(root, text="Matches:").grid(row=0, column=2)
entry_matches = tk.Entry(root) 
entry_matches.grid(row=1, column=2)

# Pull Data Button
btn = tk.Button(root, text="Pull Data", command=pull_data)
btn.grid(row=0, column=3)

# Placeholder for stats labels
lbl_kda = tk.Label(root, text="KDA: --")
lbl_kda.grid(row=2, column=0)

lbl_cs = tk.Label(root, text="CS: --")
lbl_cs.grid(row=2, column=1)

lbl_winrate = tk.Label(root, text="Winrate: --")
lbl_winrate.grid(row=2, column=2)

root.mainloop()
