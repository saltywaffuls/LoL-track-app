from datetime import datetime
from module5 import load_data # Import all_data from module5


all_data = load_data()  # Load all data from the CSV file
# --- Utility Functions (do not depend on GUI widgets) ---

def deduplicate_matches(matches):
    """Remove duplicate matches by match_id, keeping the first occurrence."""
    seen_ids = set()
    unique_matches = []
    for row in matches:
        if row["match_id"] not in seen_ids:
            unique_matches.append(row)
            seen_ids.add(row["match_id"])
    return unique_matches

def data_treeview_format(all_data):
    f_data = deduplicate_matches(all_data)
    rows = []
    for row in f_data:
        user = f"{row['summoner_id']}#{row['tag_line']}" if row['tag_line'] else row['summoner_id']
        kda = f"{row['kills']}/{row['deaths']}/{row['assists']} ({(row['kills']+row['assists'])/(row['deaths'] if row['deaths'] > 0 else 1):.2f})"
        cs = f"{row['cs']:.0f} ({row['cs_per_min']:.1f}/min)"
        kp = f"{row['kill_participation'] * 100:.0f}%"
        duration_seconds = int(row['duration'])
        minutes = duration_seconds // 60
        seconds = duration_seconds % 60
        duration = f"{minutes}:{seconds:02d}"
        item_ids = [item[1] for item in row["items"][-6:]] if row["items"] else []
        item_str = " ".join(str(item_id) for item_id in item_ids) if item_ids else "No items"
        rows.append({
            "user": user,
            "champion": row["champion"],
            "kda": kda,
            "cs": cs,
            "kp": kp,
            "win": row["win"],
            "duration": duration,
            "damage": row["damage"],
            "level": row["level"],
            "vision": row["vision"],
            "match_date": row["match_date"],
            "game_type": row["game_type"],
            "patch": row["patch"],
            "items": item_str,
            "match_id": row["match_id"],
        })
    return rows

def dashboard_treeview_format(all_data, name, tag, num_matches):
    try:
        num_matches = int(num_matches)
        if num_matches <= 0:
            num_matches = 10
    except (ValueError, TypeError):
        num_matches = 10

    filtered = deduplicate_matches([
        row for row in all_data
        if row.get("summoner_id", "").lower() == name.lower() and row.get("tag_line", "").lower() == tag.lower()
    ])
    filtered.sort(key=lambda x: datetime.strptime(x.get("match_date", "01-01-1970 00:00:00"), "%m-%d-%Y %H:%M:%S"), reverse=True)
    recent = filtered[:num_matches]
    rows = []
    for row in recent:
        deaths = row.get("deaths", 1) or 1
        kda = f"{row.get('kills', 0)}/{row.get('deaths', 0)}/{row.get('assists', 0)} ({(row.get('kills', 0)+row.get('assists', 0))/deaths:.2f})"
        cs = f"{row.get('cs', 0):.0f} ({row.get('cs_per_min', 0):.1f}/min)"
        kp = f"{row.get('kill_participation', 0)*100:.0f}%"
        win = "Win" if row.get("win") else "Loss"
        rows.append({
            "champion": row.get("champion", ""),
            "kda": kda,
            "cs": cs,
            "kp": kp,
            "win": win,
            "match_id": row.get("match_id", ""),
            "match_date": row.get("match_date", ""),
        })
    return recent, rows

def refresh_treeview(tree, rows, columns):
    tree.delete(*tree.get_children())
    for row in rows:
        values = tuple(row.get(col, "") for col in columns)
        tree.insert("", "end", iid=row.get("match_id", ""), values=values)

def treeview_sort_column(tree, col, reverse):
    data = [(tree.set(k, col), k) for k in tree.get_children('')]
    try:
        data.sort(key=lambda t: float(t[0].replace('%','').replace(',','')), reverse=reverse)
    except ValueError:
        data.sort(key=lambda t: t[0], reverse=reverse)
    for index, (val, k) in enumerate(data):
        tree.move(k, '', index)
    tree.heading(col, command=lambda: treeview_sort_column(tree, col, not reverse))
