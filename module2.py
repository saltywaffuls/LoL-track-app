import os  # Provides functions to interact with the operating system
import requests  # Allows you to make HTTP requests to APIs
from dotenv import load_dotenv  # Loads environment variables from a .env file

# Load environment variables from the .env file
load_dotenv()  # Reads the .env file and loads the variables into the environment

# Retrieve the Riot API key from the environment variables
API_KEY = os.getenv("RIOT_API_KEY")  # Fetches the value of RIOT_API_KEY from the environment

# Check if the API key is loaded successfully
if not API_KEY:  # If the API key is not found, raise an error
    raise ValueError("API key not found. Please set the RIOT_API_KEY environment variable.")


HEADERS = {"X-Riot-Token": API_KEY}  # The Riot API requires the API key to be passed in the headers

def get_riot_ID(safe_name, region):
    # Construct the base URL for the Riot API request
    base_url = f"https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{safe_name}/{region}"  # The base URL for the API request
    # The URL includes the region (na1 for North America) and the encoded summoner name

    # Make the API request to fetch summoner information
    # Send a GET request to the Riot API
    resp = requests.get(base_url, headers=HEADERS)
    resp.raise_for_status()  # Raise an exception for HTTP errors (4xx and 5xx status codes)

    data = resp.json()  # Parse the JSON response into a Python dictionary
    puuid = data.get("puuid")
    return puuid  # Return the puuid from the response data
        

def get_summoner_ID(puuid, region):
    # Construct the base URL for the Riot API request to fetch summoner ID
    base_url = f"https://{region}.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}"  # The base URL for the API request

        # Send a GET request to the Riot API
    resp = requests.get(base_url, headers=HEADERS)
    resp.raise_for_status()  # Raise an exception for HTTP errors (4xx and 5xx status codes)

    data = resp.json()
    return data  # Return the summoner ID from the response data
        



"""
Explanation of the script:

1. Obtain an API Key:
   - You need to generate an API key from the Riot Developer Portal and store it in a .env file.

2. Make Your First Request:
   - This script demonstrates how to make a GET request to the Riot API to fetch summoner information.

3. Error Handling & Rate Limits:
   - The script handles common errors like invalid API keys (403), summoner not found (404), and rate limits (429).

4. Parse JSON Safely:
   - The script uses `data.get("key")` to safely access JSON fields, avoiding errors if the key is missing.

5. Exercise:
   - Modify the `summoner_name` variable to query different summoners.
   - Experiment with different regions by changing the `base_url` (e.g., `euw1` for Europe West).
"""