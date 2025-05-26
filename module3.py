import requests
from module2 import HEADERS, get_riot_ID  # reuse the same headers dict



def get_lol_match_ID(puuid: str, start: int = 0, count: int = 20,) -> list:
    # Construct the base URL for the Riot API request
    base_url = f"https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start={start}&count={count}"  # The base URL for the API request
    
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
    # Defensive: Ensure match_json is a dict and has the expected keys
    if not isinstance(match_json, dict) or "info" not in match_json or "participants" not in match_json["info"]:
        print("DEBUG: Bad match_json received:", match_json)
        return None

    for P in match_json["info"]["participants"]:
        if P["puuid"] == my_puuid:  # Check if the participant's PUUID matches the provided PUUID

            stats = {
                "match_id": match_json["metadata"]["matchId"],  # Extract match ID
                "patch": match_json["info"]["gameVersion"],  # Extract game version
                "duration":  match_json["info"]["gameDuration"] / 60,
                "champion": P["championName"],  # Extract champion name
                "kills": P["kills"],  # Extract kills
                "deaths": P["deaths"],  # Extract deaths
                "assists": P["assists"],  # Extract assists
                "kill_participation": kill_participation(P, match_json),  # Calculate kill participation
                "cs": P["totalMinionsKilled"] + P["neutralMinionsKilled"],  # Calculate total CS
                "damage": P["totalDamageDealtToChampions"],  # Extract total damage dealt to champions
                "gold": P["goldEarned"],  # Extract gold earned
                "vision": P["visionScore"],  # Extract vision score
                "win": P["win"],  # Extract win status
            }

            timeline_json = get_match_timeline(match_json["metadata"]["matchId"])  # Fetch timeline data once

            stats_timeline = {
                "gold_per_min": gold_at_time(P, timeline_json, stats["duration"]),  # Calculate gold at end of game
                "cs_per_min": cs_per_min(P, match_json),  # Calculate CS per minute
                "xp_per_min": xp_per_min(P, timeline_json, stats["duration"]),  # Calculate XP per minute
                "level": level_at_time(P, timeline_json, stats["duration"]),  # Extract level at the end of the game
                "items": extract_item_timeline(P, timeline_json),  # Extract item timeline
            }

            return { **stats, **stats_timeline }  # Return the extracted stats as a dictionary

    return None  # Return None if no matching participant is found

def kill_participation(participant: dict, match_json: dict) -> float:
    team_kills = sum(p["kills"] + p["assists"] for p in match_json["info"]["participants"]
                     if p["teamId"] == participant["teamId"])  # Calculate total team kills
    
    return (participant["kills"] + participant["assists"]) / team_kills if team_kills > 0 else 0.0  # Calculate kill participation

def gold_at_time(p: dict, timeline_json: dict, game_time: int) -> int:

    ts_cutoff = game_time * 60_000  # Convert game time to milliseconds
    pid = p["participantId"]  # Extract participant ID
    for frame in timeline_json["info"]["frames"]:
        if frame["timestamp"] > ts_cutoff:  # Check if the timestamp is greater than the cutoff
            break
        # participantFrames is a dict id_str → stats
        for pdata in frame["participantFrames"].values():
            if pdata["participantId"] == pid:
                return pdata["totalGold"]
    return 0  # Return 0 if not found

def cs_per_min(p: dict, match_json: dict) -> float:
    total_cs = p["totalMinionsKilled"] + p["neutralMinionsKilled"]  # Calculate total CS
    game_duration = match_json["info"]["gameDuration"] / 60  # Convert game duration to minutes
    return total_cs / game_duration if game_duration > 0 else 0.0  # Calculate CS per minute

def xp_per_min(p: dict, timeline_json: dict, game_time: int) -> float:
    ts_cutoff = game_time * 60_000  # Convert game time to ms
    pid = p["participantId"]
    last_xp = 0
    for frame in timeline_json["info"]["frames"]:
        if frame["timestamp"] > ts_cutoff:
            break
        for pdata in frame["participantFrames"].values():
            if pdata["participantId"] == pid:
                last_xp = pdata.get("xp", 0)
    return last_xp / game_time if game_time > 0 else 0.0  # Calculate XP per minute

def level_at_time(p: dict, timeline_json: dict, game_time: int) -> int:
    ts_cutoff = game_time * 60_000  # Convert game time to milliseconds
    pid = p["participantId"]  # Extract participant ID
    for frame in timeline_json["info"]["frames"]:
        if frame["timestamp"] > ts_cutoff:  # Check if the timestamp is greater than the cutoff
            break
        for participant in frame["participantFrames"].values():
            if participant["participantId"] == pid:  # Check if the participant ID matches
                return participant["level"]  # Return the level at the specified game time


def get_match_timeline(match_id: str, region: str = "americas") -> dict:
    base_url = f"https://{region}.api.riotgames.com/lol/match/v5/matches/{match_id}/timeline"
    
    resp = requests.get(base_url, headers=HEADERS)  # Send the GET request with headers
    resp.raise_for_status()  # Raise an exception for HTTP errors (4xx and 5xx status codes)

    match_timeline = resp.json()  # Parse the JSON response into a Python dictionary
            
    return match_timeline  # Return the match timeline as a dictionary

def extract_item_timeline(p:dict, timeline_json:dict) -> list[tuple[int,int]]:
    items = []  # Initialize an empty list to store item timelines
    pid = p["participantId"]  # Extract participant ID

    for frame in timeline_json["info"]["frames"]:
        ts = frame["timestamp"]  # Extract timestamp
        for ev in frame.get("events", []):
            if ev["type"] == "ITEM_PURCHASED" and ev.get("participantId") == pid:
                items.append((ts, ev["itemId"]))
            elif ev["type"] == "ITEM_SOLD" and ev.get("participantId") == pid:
                items.append((ts, ev["itemId"]))

    return items  # Return the list of item timelines


def compute_summary(stats: list[dict]) -> dict:
    
    total_kills = sum(stat["kills"] for stat in stats)  # Sum of kills from all games
    total_assists = sum(stat["assists"] for stat in stats)  # Sum of assists from all games
    total_deaths = sum(stat["deaths"] for stat in stats)  # Sum of deaths from all games
    total_cs = sum(stat["cs"] for stat in stats)  # Sum of CS from all games
    total_wins = sum(1 for stat in stats if stat["win"])  # Count of wins
    total_duration = sum(stat["duration"] for stat in stats)  # Calculate total duration

    if total_kills == 0 and total_assists == 0:
        avg_kda = 0.0
    else:
        avg_kda = (total_kills + total_assists) / total_deaths if total_deaths > 0 else float('inf')  # Calculate average KDA

    avg_cs_per_min = total_cs / total_duration if total_duration > 0 else 0.0  # Calculate average CS per minute
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