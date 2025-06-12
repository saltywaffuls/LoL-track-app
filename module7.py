from PIL import Image, ImageTk
import requests
import io

def get_champion_data(champion_name: str, patch_version: str = "15.12.1"):
    """

    """
    # Construct the URL for the champion's image
    url = f"https://ddragon.leagueoflegends.com/cdn/{patch_version}/data/en_US/champion/{champion_name.capitalize()}.json"
    
    # Make the request to fetch the image
    resp = requests.get(url)
    resp.raise_for_status()  # Raise an error for bad responses
    
    data = resp.json()  # Parse the JSON response

    return data  # Return the champion data

def get_champion_Square(champion_name: str, patch_version: str = "15.12.1"):
    #gets champion square art

    # Construct the URL for the champion's image
    url = f"https://ddragon.leagueoflegends.com/cdn/{patch_version}/img/champion/{champion_name.capitalize()}.png"
    
    # Make the request to fetch the image
    resp = requests.get(url)
    resp.raise_for_status()  # Raise an error for bad responses
    
    asset = Image.open(io.BytesIO(resp.content))  # Open the image from the response content
    asset_img = ImageTk.PhotoImage(asset)  # Convert the image to a format suitable for Tkinter
    return asset_img  # Return the image object

def get_champion_LS(champion_name: str, patch_version: str = "15.12.1"):
    #gets loading screen art

    # Construct the URL for the champion's image
    url = f"https://ddragon.leagueoflegends.com/cdn/img/champion/loading/{champion_name.capitalize()}_0.jpg"
    
    # Make the request to fetch the image
    resp = requests.get(url)
    resp.raise_for_status()  # Raise an error for bad responses
    
    asset = Image.open(io.BytesIO(resp.content))  # Open the image from the response content
    asset_img = ImageTk.PhotoImage(asset)  # Convert the image to a format suitable for Tkinter
    return asset_img  # Return the image object

def get_champion_item(item_id: str, patch_version: str = "15.12.1"):

    url = f"https://ddragon.leagueoflegends.com/cdn/{patch_version}/img/item/{item_id}.png"

    resp = requests.get(url)
    resp.raise_for_status()  # Raise an error for bad responses
    
    asset = Image.open(io.BytesIO(resp.content))  # Open the image from the response content
    asset_img = ImageTk.PhotoImage(asset)  # Convert the image to a format suitable for Tkinter
    return asset_img  # Return the image object



"""
https://developer.riotgames.com/docs/lol#data-dragon

linkl to documentation
"""