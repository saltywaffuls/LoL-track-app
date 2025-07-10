from tkinter import ttk
import tkinter as tk
import ast
from module7 import get_rune_icon, get_stat_perk_icon, get_champion_item  # Add get_champion_item to imports
from module3 import get_inventory, get_item_data

def display_rune_page(parent_frame, rune_info):
    """
    Display a visual rune page in the given frame.
    rune_info should contain the rune data for a specific match.
    """
    rune_frame = ttk.LabelFrame(parent_frame, text="Runes", padding=10)
    rune_frame.pack(fill="x", pady=5)
    
    # Create a horizontal layout for runes
    rune_content = ttk.Frame(rune_frame)
    rune_content.pack(fill="x")
    
    # Primary tree section
    primary_frame = ttk.Frame(rune_content)
    primary_frame.pack(side="left", fill="both", expand=True, padx=5)
    
    ttk.Label(primary_frame, text=f"Primary: {rune_info.get('primary_tree', 'Unknown')}", 
              font=("Arial", 10, "bold")).pack(anchor="w")
    
    # Display primary runes with icons
    primary_runes_frame = ttk.Frame(primary_frame)
    primary_runes_frame.pack(fill="x", pady=2)
    
    # Get the first 4 runes (primary tree runes)
    all_runes = rune_info.get('all_runes', [])
    primary_runes = all_runes[:4] if len(all_runes) >= 4 else all_runes
    
    rune_images = []  # Keep references to prevent garbage collection
    
    for i, rune_name in enumerate(primary_runes):
        rune_row = ttk.Frame(primary_runes_frame)
        rune_row.pack(fill="x", pady=1)
        
        # Try to get rune icon by finding the rune ID
        try:
            from module7 import get_runes_data
            rune_data = get_runes_data()
            rune_id = None
            for rid, rdata in rune_data.items():
                if rdata.get('name') == rune_name:
                    rune_id = rid
                    break
            
            if rune_id:
                rune_icon = get_rune_icon(str(rune_id))
                rune_images.append(rune_icon)
                icon_label = ttk.Label(rune_row, image=rune_icon)
                icon_label.pack(side="left", padx=2)
            
        except Exception as e:
            print(f"Could not load icon for rune {rune_name}: {e}")
        
        # Rune name
        name_label = ttk.Label(rune_row, text=rune_name, font=("Arial", 8))
        name_label.pack(side="left", padx=5)
        
        # Highlight keystone (first rune)
        if i == 0:
            name_label.config(font=("Arial", 9, "bold"))
    
    # Secondary tree section
    secondary_frame = ttk.Frame(rune_content)
    secondary_frame.pack(side="left", fill="both", expand=True, padx=5)
    
    ttk.Label(secondary_frame, text=f"Secondary: {rune_info.get('secondary_tree', 'Unknown')}", 
              font=("Arial", 10, "bold")).pack(anchor="w")
    
    # Display secondary runes (typically 2 runes)
    secondary_runes_frame = ttk.Frame(secondary_frame)
    secondary_runes_frame.pack(fill="x", pady=2)
    
    secondary_runes = all_runes[4:6] if len(all_runes) >= 6 else all_runes[4:]
    
    for rune_name in secondary_runes:
        rune_row = ttk.Frame(secondary_runes_frame)
        rune_row.pack(fill="x", pady=1)
        
        try:
            from module7 import get_runes_data
            rune_data = get_runes_data()
            rune_id = None
            for rid, rdata in rune_data.items():
                if rdata.get('name') == rune_name:
                    rune_id = rid
                    break
            
            if rune_id:
                rune_icon = get_rune_icon(str(rune_id))
                rune_images.append(rune_icon)
                icon_label = ttk.Label(rune_row, image=rune_icon)
                icon_label.pack(side="left", padx=2)
            
        except Exception as e:
            print(f"Could not load icon for rune {rune_name}: {e}")
        
        name_label = ttk.Label(rune_row, text=rune_name, font=("Arial", 8))
        name_label.pack(side="left", padx=5)
    
    # Stat perks section
    stat_frame = ttk.Frame(rune_content)
    stat_frame.pack(side="right", fill="both", padx=5)
    
    ttk.Label(stat_frame, text="Stat Perks", font=("Arial", 10, "bold")).pack(anchor="w")
    
    stat_perks_frame = ttk.Frame(stat_frame)
    stat_perks_frame.pack(fill="x", pady=2)
    
    stat_perks = rune_info.get('stat_perks', {})
    for perk_type, perk_desc in stat_perks.items():
        perk_row = ttk.Frame(stat_perks_frame)
        perk_row.pack(fill="x", pady=1)
        
        # Try to get the stat perk icon
        try:
            # Map the description back to the perk ID
            perk_id_map = {
                "+9 Adaptive Force": 5005,
                "+10.5 Attack Damage": 5007,
                "+9 Ability Power": 5008,
                "+15-140 Health (based on level)": 5001,
                "+6 Armor": 5002,
                "+8 Magic Resist": 5003
            }
            
            perk_id = perk_id_map.get(perk_desc)
            if perk_id:
                perk_icon = get_stat_perk_icon(perk_id)
                rune_images.append(perk_icon)
                icon_label = ttk.Label(perk_row, image=perk_icon)
                icon_label.pack(side="left", padx=2)
            
        except Exception as e:
            print(f"Could not load icon for stat perk {perk_desc}: {e}")
        
        desc_label = ttk.Label(perk_row, text=perk_desc, font=("Arial", 7))
        desc_label.pack(side="left", padx=2)
    
    # Store image references to prevent garbage collection
    rune_frame.rune_images = rune_images
    
    return rune_frame

def display_final_inventory(parent_frame, items):
    """
    Display the final inventory items in the given frame.
    items should be the raw items data from the match.
    """
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

    ttk.Label(parent_frame, text="Final Inventory:").pack(pady=5)
    item_frame = ttk.Frame(parent_frame)
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
    
    # Store image references to prevent garbage collection
    item_frame.item_images = item_images
    
    return item_frame


def display_item_timeline(parent_frame, items):
    """
    Display the item timeline visualization in the given frame.
    items should be the raw items data from the match.
    """
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

    ttk.Label(parent_frame, text="Item Timeline:").pack()

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
        timeline_canvas = tk.Canvas(parent_frame, bg="white", height=canvas_height, width=canvas_width)
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
    
    return timeline_canvas