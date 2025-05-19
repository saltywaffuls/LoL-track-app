import requests
from module2 import HEADERS  # reuse the same headers dict


def get_lol_match_ID(puuid: str, start: int = 0, count: int = 20,) -> list:
    # Construct the base URL for the Riot API request
    base_url = f"https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start=0&count=20"
    
    resp = requests.get(base_url, headers=HEADERS)  # Send the GET request with headers
    resp.raise_for_status()  # Raise an exception for HTTP errors (4xx and 5xx status codes)

    match_ids = resp.json()  # Parse the JSON response into a Python list
            
    return match_ids  # Return the list of match IDs
        
def get_match_data(match_id: str, region: str = "americas") -> dict:

    base_url = f"https://{region}.api.riotgames.com/lol/match/v5/matches/{match_id}"
    
    resp = requests.get(base_url, headers=HEADERS)  # Send the GET request with headers
    resp.raise_for_status()
  
    match_data = resp.json()  # Parse the JSON response into a Python dictionary
            
    return match_data  # Return the match data as a dictionary
        

def extract_my_stats(match_json: dict, my_puuid: str) -> dict:
    
    duration_min = match_json["info"]["gameDuration"] / 60  # Extract and convert game duration to minutes

    for P in match_json["info"]["participants"]:
        if P["puuid"] == my_puuid:  # Check if the participant's PUUID matches the provided PUUID
            stats = {
                "match_id": match_json["metadata"]["matchId"],  # Extract match ID
                "champion": P["championName"],  # Extract champion name
                "kills": P["kills"],  # Extract kills
                "deaths": P["deaths"],  # Extract deaths
                "assists": P["assists"],  # Extract assists
                "cs": P["totalMinionsKilled"] + P["neutralMinionsKilled"],  # Calculate total CS
                "win": P["win"],  # Extract win status
                "duration": duration_min  # Add game duration in minutes
            }
            return stats  # Return the extracted stats as a dictionary

    return None  # Return None if no matching participant is found

def compute_summary(stats: list[dict]) -> dict:
    
    total_kills = sum(stat["kills"] for stat in stats)  # Sum of kills from all games
    total_assists = sum(stat["assists"] for stat in stats)  # Sum of assists from all games
    total_deaths = sum(stat["deaths"] for stat in stats)  # Sum of deaths from all games
    total_cs = sum(stat["cs"] for stat in stats)  # Sum of CS from all games
    total_wins = sum(1 for stat in stats if stat["win"])  # Count of wins

    avg_kda = (total_kills + total_assists) / total_deaths if total_deaths > 0 else float('inf')  # Calculate average KDA
    avg_cs_per_min = total_cs / sum(stat["duration"] for stat in stats)  # Calculate average CS per minute
    win_rate = total_wins / len(stats) if len(stats) > 0 else 0.0  # Calculate win rate

    return {
        "avg_kda": avg_kda,
        "avg_cs_per_min": avg_cs_per_min,
        "win_rate": win_rate
    }  # Return the computed summary as a dictionary






"""
Goal: Retrieve match history and compute simple improvement metrics.

Match List Retrieval

Call the Match-V5 endpoint to fetch recent match IDs.

Iterate over match IDs and pull match data (participants, KDA, CS, etc.).

Compute Metrics

Average KDA, CS per minute, win rate over last 20 games.

Store results in a Python dict or small pandas DataFrame (optional).

CLI Prototype

In main.py, allow the user to type python main.py stats YourSummonerName and display metrics neatly.

Exercise:

Extend your Summoner class to include methods like .fetch_match_ids() and .compute_summary().
"""