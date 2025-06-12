import requests
from module2 import HEADERS  # reuse the same headers dict
from module5 import load_data
from datetime import datetime  # For handling timestamps



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

def get_ranked_data(puuid: str, region: str = "na1") -> dict: # league-v4 | /lol/league/v4/entries/by-puuid/{encryptedPUUID}
    """
    Fetches ranked data for a given PUUID.
    This function is a placeholder and does not currently implement the actual API call.
    """
    base_url = f"https://{region}.api.riotgames.com/lol/league/v4/entries/by-puuid/{puuid}"  # Construct the base URL for the API request
    resp = requests.get(base_url, headers=HEADERS)  # Send the GET request with headers
    resp.raise_for_status()  # Raise an exception for HTTP errors (4xx and 5xx status codes)

    ranked_data = resp.json()  # Parse the JSON response into a Python dictionary

    return ranked_data  # Return the ranked data as a dictionary

#/lol/match/v5/matches/{matchId}/timeline
def get_match_timeline(match_id: str, region: str = "americas") -> dict:
    base_url = f"https://{region}.api.riotgames.com/lol/match/v5/matches/{match_id}/timeline"
    
    resp = requests.get(base_url, headers=HEADERS)  # Send the GET request with headers
    resp.raise_for_status()  # Raise an exception for HTTP errors (4xx and 5xx status codes)

    match_timeline = resp.json()  # Parse the JSON response into a Python dictionary
            
    return match_timeline  # Return the match timeline as a dictionary

def game_type(match_json: dict) -> str:
    queue_id = match_json["info"].get("queueId", 0)  # Extract queue ID from match JSON
    if queue_id == 420:
        return "Ranked Solo/Duo"
    elif queue_id == 440:
        return "Ranked Flex"
    elif queue_id in [400, 410, 420, 430, 440]:
        return "Normal Game"
    else:
        return "Other"  # Return 'Other' for any other queue ID


def extract_my_stats(match_json: dict, my_puuid: str) -> dict:
    # Defensive: Ensure match_json is a dict and has the expected keys
    if not isinstance(match_json, dict) or "info" not in match_json or "participants" not in match_json["info"]:
        print("DEBUG: Bad match_json received:", match_json)
        return None

    for P in match_json["info"]["participants"]:
        if P["puuid"] == my_puuid:  # Check if the participant's PUUID matches the provided PUUID

            game_creation = match_json["info"].get("gameCreation", 0)  # Extract game creation time
            match_date = datetime.fromtimestamp(game_creation // 1000).strftime("%m-%d-%Y %H:%M:%S")
            
            stats = {
                "summoner_id": P["summonerId"],  # Extract summoner ID
                "match_id": match_json["metadata"]["matchId"],  # Extract match ID
                "match_date": match_date,  # Format the game creation time as a string
                "patch": match_json["info"]["gameVersion"],  # Extract game version
                "game_type": game_type(match_json),  # Determine the game type
                "duration":  match_json["info"]["gameDuration"] / 60,
                "champion": P["championName"],  # Extract champion name
                "kills": P["kills"],  # Extract kills
                "deaths": P["deaths"],  # Extract deaths
                "assists": P["assists"],  # Extract assists
                "kill_participation": kill_participation(P, match_json),  # Calculate kill participation
                "cs": P["totalMinionsKilled"] + P["neutralMinionsKilled"],  # Calculate total CS
                "level": P["champLevel"],  # Extract champion level
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
                "items": extract_item_timeline(P, timeline_json),  # Extract item timeline
            }

            ranked_json_list = get_ranked_data(my_puuid)  # Fetch ranked data
            # Riot API returns a list of ranked queues, pick solo/duo if available, else first or empty dict
            if isinstance(ranked_json_list, list) and ranked_json_list:
                ranked_json = next((q for q in ranked_json_list if q.get("queueType") == "RANKED_SOLO_5x5"), ranked_json_list[0])
            else:
                ranked_json = {}

            stats_ranked = {
                "tier": ranked_json.get("tier", "Unranked"),  # Extract tier, default to 'Unranked'
                "rank": ranked_json.get("rank", "I"),  # Extract rank, default to 'I'
                "leaguePoints": ranked_json.get("leaguePoints", 0),  # Extract league points
                "wins": ranked_json.get("wins", 0),  # Extract wins
                "losses": ranked_json.get("losses", 0),  # Extract losses
                "win_rate_ranked": (
                    ranked_json.get("wins", 0) / (ranked_json.get("wins", 0) + ranked_json.get("losses", 0))
                    if (ranked_json.get("wins", 0) + ranked_json.get("losses", 0)) > 0 else 0.0
                ),  # Calculate win rate
            }

            return { **stats, **stats_timeline, **stats_ranked }  # Return the extracted stats as a dictionary

    return None  # Return None if no matching participant is found


def kill_participation(p: dict, match_json: dict) -> float:
    your = p["kills"] + p["assists"]
    team_kills = sum(x["kills"] for x in match_json["info"]["participants"]
                     if x["teamId"] == p["teamId"])
    return your / team_kills if team_kills else 0.0

def gold_at_time(p: dict, timeline_json: dict, game_time: int) -> int: # thiss may not be working as the data alwasy returns 500 invetigate

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
    total_kp = sum(s.get("kill_participation", 0) for s in stats)  # Sum of kill participation
    total_dmg = sum(s.get("damage", 0) for s in stats)  # Sum of damage dealt to champions
    total_gold = sum(s.get("gold", 0) for s in stats)  # Sum of gold earned
    total_gpm = sum(s.get("gold_per_min", 0) for s in stats)  # Sum of gold per minute
    total_vis = sum(s.get("vision", 0) for s in stats)  # Sum of vision score

    

    if total_kills == 0 and total_assists == 0:
        avg_kda = 0.0
    else:
        avg_kda = (total_kills + total_assists) / total_deaths if total_deaths > 0 else float('inf')  # Calculate average KDA

    avg_cs_per_min = total_cs / total_duration if total_duration > 0 else 0.0  # Calculate average CS per minute
    win_rate = total_wins / len(stats) if len(stats) > 0 else 0.0  # Calculate win rate
    avg_kp = total_kp   / len(stats) if len(stats) > 0 else 0.0  # Calculate average kill participation
    avg_dmg = total_dmg / len(stats) if len(stats) > 0 else 0.0  # Calculate average damage dealt
    avg_gpm = total_gpm / len(stats) if len(stats) > 0 else 0.0  # Calculate average gold per minute
    avg_vis = total_vis / len(stats) if len(stats) > 0 else 0.0  # Calculate average vision score
    avg_gold = total_gold / len(stats) if len(stats) > 0 else 0.0  # Calculate average gold earned


    return {
        "avg_kda": avg_kda,
        "avg_cs_per_min": avg_cs_per_min,
        "win_rate": win_rate,
        "avg_kp": avg_kp,
        "avg_damage": avg_dmg,
        "avg_gold_per_min": avg_gpm,
        "avg_vision": avg_vis,
        "avg_gold": avg_gold,
    }  # Return the computed summary as a dictionary

def compute_champion_summary(champion_name: str, queue_type: str) -> dict:
    """
    Computes summary stats for a specific champion and queue type.
    """
    champion_stats = load_data()  # Load all match data from CSV

    # Filter for the specified champion and queue type
    filtered = [
        s for s in champion_stats
        if s.get("champion") == champion_name and s.get("game_type") == queue_type
    ]

    if not filtered:
        return {
            "avg_kda": 0.0,
            "avg_cs_per_min": 0.0,
            "win_rate": 0.0,
            "avg_kp": 0.0,
            "avg_damage": 0.0,
            "avg_gold_per_min": 0.0,
            "avg_vision": 0.0,
            "avg_gold": 0.0,
            "avg_league_points": 0.0,
        }

    return compute_summary(filtered)



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