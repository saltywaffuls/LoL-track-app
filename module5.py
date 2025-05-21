import os  # Import the os module for file and path operations
import csv  # Import the csv module for reading and writing CSV files
from datetime import datetime, timedelta  # Import datetime for handling date and time

# Define the path to the CSV file where match history will be stored.
# os.path.join ensures the path works on any operating system.
CSV_path = os.path.join("data", "history.csv")

# Define the column headers for the CSV file.
FIELDS = ["match_id", "date", "kills", "deaths", "assists", "cs", "win", "duration", "champion"]

def init_storage():
    """
    Initialize the CSV file for storing historical stats.
    This function checks if the CSV file exists.
    If it does not exist, it creates the file and writes the header row.
    """
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
            row["kills"] = int(row["kills"])
            row["deaths"] = int(row["deaths"])
            row["assists"] = int(row["assists"])
            row["cs"] = int(row["cs"])
            row["win"] = row["win"] == "True"
            row["champion"] = row["champion"]
            row["duration"] = int(row["duration"])
            row["date"] = datetime.strptime(row["date"], "%Y-%m-%d %H:%M:%S")
            if cutoff is None or row["date"] >= cutoff:
                out.append(row)
    return out
           


"""
Persist your historical stats

 Build a “progress” subcommand in the CLI

 Trend visualization

 Scheduled snapshots

Dashboard or report export
"""