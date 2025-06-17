import os  # Import the os module for file and path operations
import csv  # Import the csv module for reading and writing CSV files
import ast  # Import ast for safely evaluating strings to Python objects
from datetime import datetime, timedelta  # Import datetime for handling date and time
import json  # Import json for handling items field if it's in JSON format

# Define the path to the CSV file where match history will be stored.
# os.path.join ensures the path works on any operating system.
CSV_path = os.path.join("data", "history.csv")

# Define the column headers for the CSV file.
FIELDS = ["summoner_id", "tag_line", "match_id", "patch", "match_date", "game_type", "duration", "win", "champion", "kills", "deaths", "assists", "cs", "damage", "kill_participation", "gold", "vision",
           "xp_per_min", "cs_per_min", "gold_per_min", "level", "items", "tier", "rank", "leaguePoints", "wins", "losses", "win_rate_ranked", "ingest_date"]

def init_storage():
    """
    Initialize the CSV file for storing historical stats.
    This function checks if the CSV file exists.
    If it does not exist, it creates the file and writes the header row.
    """
    os.makedirs(os.path.dirname(CSV_path), exist_ok=True) # Create the directory if it doesn't exist.

    # Check if the CSV file already exists at the specified path.
    if not os.path.exists(CSV_path):
        # If the file does not exist, open it in write mode.
        # 'newline=""' prevents extra blank lines on Windows.
        with open(CSV_path, "w", newline="") as f:
            # Create a DictWriter object, which allows writing dictionaries as rows.
            writer = csv.DictWriter(f, fieldnames=FIELDS)
            # Write the header row to the CSV file.
            writer.writeheader()


def save_match_data(data: dict):
    """
    Save match data to the CSV file.
    This function appends a new row to the CSV file with the provided match data.
    """
    existing = set()  # Initialize an empty set to store existing match IDs.
    
    # Open the CSV file in append mode.
    if os.path.exists(CSV_path): # If the file exists, read the existing match IDs to check for duplicates.
        with open(CSV_path, newline="") as f:
            reader = csv.DictReader(f)
            existing = {row["match_id"] for row in reader}
        # Check if the match ID already exists in the CSV file.

    if data["match_id"] in existing:
        return # If the match ID already exists, do not write it again.
        
    with open(CSV_path, "a", newline="") as f:
        # Create a DictWriter object for appending data.
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        # Write the match data as a new row in the CSV file.
        writer.writerow(data)

def load_data(day: int = None) -> list[dict]:
    """
    If days is given, only return games from the last X days.
    Otherwise return all.
    """
    cutoff = None
    if day is not None:
        cutoff = datetime.now() - timedelta(days=day)

    out = []
    with open(CSV_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["summoner_name"] = row.get("summonerID", "")
            row["patch"] = row.get("patch", "")
            row["kills"] = int(row["kills"])
            row["deaths"] = int(row["deaths"])
            row["assists"] = int(row["assists"])
            row["cs"] = float(row["cs"])
            row["win"] = row["win"] == "True"
            row["champion"] = row["champion"]
            row["duration"] = float(row["duration"])
            row["match_date"] = row["match_date"]
            row["tag_line"] = row.get("tag_line", "na1")
            row["gold"] = float(row.get("gold", 0))
            row["vision"] = float(row["vision"])
            row["xp_per_min"]   = float(row.get("xp_per_min", 0))
            row["cs_per_min"]   = float(row.get("cs_per_min", 0))
            row["gold_per_min"] = float(row.get("gold_per_min", 0))
            row["level"] = int(row.get("level", 0))
            row["kill_participation"] = float(row.get("kill_participation", 0))
            row["damage"] = float(row.get("damage", 0))
            row["game_type"] = row.get("game_type", "normal")
            row["tier"] = row.get("tier", "")
            row["rank"] = row.get("rank", "")
            row["leaguePoints"] = int(row.get("leaguePoints", 0))
            row["wins"] = int(row.get("wins", 0))
            row["losses"] = int(row.get("losses", 0))
            row["win_rate_ranked"] = float(row.get("win_rate_ranked", 0.0))
            
            items_str = row.get("items", "")
            try:
                if items_str and items_str != "No items":
                    row["items"] = ast.literal_eval(items_str)
                else:
                    row["items"] = []
            except Exception:
                row["items"] = []

            # Convert match_date string to datetime for comparison
            try:
                match_date_dt = datetime.strptime(row["match_date"], "%Y-%m-%d %H:%M:%S")
            except Exception:
                match_date_dt = None
            if cutoff is None or (match_date_dt and match_date_dt >= cutoff):
                out.append(row)
            # Convert ingest_date string to datetime for comparison
            try:
                ingest_date_dt = datetime.strptime(row["ingest_date"], "%m-%d-%Y %H:%M:%S")
            except Exception:
                ingest_date_dt = None
            if cutoff is None or (ingest_date_dt and ingest_date_dt >= cutoff):
                out.append(row)
    return out
    
           


"""
Persist your historical stats

 Build a “progress” subcommand in the CLI

 Trend visualization

 Scheduled snapshots

Dashboard or report export
"""