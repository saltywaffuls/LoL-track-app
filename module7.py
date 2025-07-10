from PIL import Image, ImageTk
import requests
import io

def get_champion_data(champion_name: str, patch_version: str = "15.13.1"):
    """

    """
    # Construct the URL for the champion's image
    url = f"https://ddragon.leagueoflegends.com/cdn/{patch_version}/data/en_US/champion/{champion_name}.json"
    
    # Make the request to fetch the image
    resp = requests.get(url)
    resp.raise_for_status()  # Raise an error for bad responses
    
    data = resp.json()  # Parse the JSON response

    return data  # Return the champion data

def get_champion_Square(champion_name: str, patch_version: str = "15.13.1"):
    #gets champion square art

    # Construct the URL for the champion's image
    url = f"https://ddragon.leagueoflegends.com/cdn/{patch_version}/img/champion/{champion_name}.png"
    
    # Make the request to fetch the image
    resp = requests.get(url)
    resp.raise_for_status()  # Raise an error for bad responses
    
    asset = Image.open(io.BytesIO(resp.content))  # Open the image from the response content
    asset_img = ImageTk.PhotoImage(asset)  # Convert the image to a format suitable for Tkinter
    return asset_img  # Return the image object

def get_champion_LS(champion_name: str, patch_version: str = "15.13.1"):
    #gets loading screen art

    # Construct the URL for the champion's image
    url = f"https://ddragon.leagueoflegends.com/cdn/img/champion/loading/{champion_name}_0.jpg"
    
    # Make the request to fetch the image
    resp = requests.get(url)
    resp.raise_for_status()  # Raise an error for bad responses
    
    asset = Image.open(io.BytesIO(resp.content))  # Open the image from the response content
    asset_img = ImageTk.PhotoImage(asset)  # Convert the image to a format suitable for Tkinter
    return asset_img  # Return the image object

def get_champion_item(item_id: str, patch_version: str = "15.13.1"):

    url = f"https://ddragon.leagueoflegends.com/cdn/{patch_version}/img/item/{item_id}.png"

    resp = requests.get(url)
    resp.raise_for_status()  # Raise an error for bad responses
    
    asset = Image.open(io.BytesIO(resp.content))  # Open the image from the response content
    asset_img = ImageTk.PhotoImage(asset)  # Convert the image to a format suitable for Tkinter
    return asset_img  # Return the image object

def get_runes_data(patch_version: str = "15.13.1"):
    """
    Fetch rune data from Data Dragon API.
    Returns a dictionary mapping rune IDs to rune information.
    """
    rune_data_url = "https://ddragon.leagueoflegends.com/cdn/{patch_version}/data/en_US/runesReforged.json"
    
    try:
        response = requests.get(rune_data_url)
        response.raise_for_status()
        rune_trees = response.json()
        
        # Create a flat dictionary mapping rune IDs to rune info
        rune_dict = {}
        
        for tree in rune_trees:
            # Add the tree itself
            rune_dict[tree['id']] = {
                'name': tree['name'],
                'key': tree['key'],
                'icon': tree['icon'],
                'type': 'tree'
            }
            
            # Add all runes in the tree
            for slot in tree['slots']:
                for rune in slot['runes']:
                    rune_dict[rune['id']] = {
                        'name': rune['name'],
                        'key': rune['key'],
                        'shortDesc': rune['shortDesc'],
                        'longDesc': rune['longDesc'],
                        'icon': rune['icon'],
                        'tree': tree['name'],
                        'type': 'rune'
                    }
        
        return rune_dict
    except Exception as e:
        print(f"Error fetching rune data: {e}")
        return {}
    

def get_rune_icon(rune_id: str, patch_version: str = "15.13.1"):
    """
    Get rune icon image from Data Dragon API.
    Returns a PhotoImage object suitable for Tkinter.
    """
    # First get the rune data to find the icon path
    rune_data = get_runes_data(patch_version)
    rune_info = rune_data.get(int(rune_id), {})
    
    if not rune_info or 'icon' not in rune_info:
        # Return a placeholder or raise an error
        raise ValueError(f"Rune {rune_id} not found or has no icon")
    
    # Construct the URL for the rune's icon
    icon_path = rune_info['icon']
    url = f"https://ddragon.leagueoflegends.com/cdn/img/{icon_path}"
    
    # Make the request to fetch the image
    resp = requests.get(url)
    resp.raise_for_status()
    
    asset = Image.open(io.BytesIO(resp.content))
    # Resize rune icons to a consistent size (32x32 or 48x48)
    asset = asset.resize((32, 32), Image.Resampling.LANCZOS)
    asset_img = ImageTk.PhotoImage(asset)
    return asset_img

def get_stat_perk_icon(stat_perk_id: int, patch_version: str = "15.13.1"):
    """
    Get stat perk icon. These are the small stat runes at the bottom of the rune page.
    """
    # Mapping of stat perk IDs to their icon filenames
    stat_perk_icons = {
        5005: "perk-images/StatMods/StatModsAdaptiveForceIcon.png",
        5007: "perk-images/StatMods/StatModsAttackDamageIcon.png", 
        5008: "perk-images/StatMods/StatModsAbilityPowerIcon.png",
        5001: "perk-images/StatMods/StatModsHealthIcon.png",
        5002: "perk-images/StatMods/StatModsArmorIcon.png",
        5003: "perk-images/StatMods/StatModsMagicResIcon.png",
        5011: "perk-images/StatMods/StatModsAdaptiveForceIcon.png",
        5013: "perk-images/StatMods/StatModsAttackDamageIcon.png",
        5014: "perk-images/StatMods/StatModsAbilityPowerIcon.png"
    }
    
    icon_path = stat_perk_icons.get(stat_perk_id)
    if not icon_path:
        raise ValueError(f"Stat perk {stat_perk_id} not found")
    
    url = f"https://ddragon.leagueoflegends.com/cdn/{patch_version}/img/{icon_path}"
    
    resp = requests.get(url)
    resp.raise_for_status()
    
    asset = Image.open(io.BytesIO(resp.content))
    asset = asset.resize((24, 24), Image.Resampling.LANCZOS)  # Smaller for stat perks
    asset_img = ImageTk.PhotoImage(asset)
    return asset_img
    
"""
https://developer.riotgames.com/docs/lol#data-dragon

linkl to documentation
"""