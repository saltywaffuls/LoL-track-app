from module2 import get_riot_ID, get_summoner_ID  # Import necessary functions and constants
from module3 import get_lol_match_ID, get_match_data,  extract_my_stats, compute_summary, compute_champion_summary
from module5 import init_storage, save_match_data, load_data  # Import functions for data storage and retrieval
import argparse, requests
from urllib.parse import quote  # For URL encoding of summoner names
from datetime import datetime, timedelta

def run_account(summoner_name, tag_line = "na1", matches=20):
        name = quote(summoner_name)
        puuid = get_riot_ID(name, tag_line)  # Fetch the PUUID using the provided summoner name and region
        summ = get_summoner_ID(puuid, tag_line)  # Fetch the summoner data using the PUUID

        match_ids = get_lol_match_ID(puuid, start=0, count= matches)  # Fetch the match IDs for the provided PUUID

        stats = [extract_my_stats(get_match_data(mid), puuid)
                  for mid in match_ids 
                  if extract_my_stats(get_match_data(mid), puuid)]  # Extract stats for each match ID
        init_storage()  # Initialize the CSV file for storing historical stats
        for s in stats:
            s["summoner_id"] = summoner_name  # Add the summoner name to the data
            s["tag_line"] = tag_line               # Add the tag_line to the data
            s["ingest_date"] = datetime.now().strftime("%m-%d-%Y %H:%M:%S")  # (optional: overwrite date with save time)
            save_match_data(s)  # Save the match data to the CSV file

        summary = compute_summary(stats)  # Compute the summary statistics from the list of stats
        return summary, summ["summonerLevel"], summ["profileIconId"], stats  # Return the summary and summoner details


def run_progress(args):
    init_storage()  # Initialize the CSV file for storing historical stats

    hist = load_data(day=args.days)  # Load historical data from the CSV file
    if not hist:
        print(f"No data for the last {args.days} days.")
        return

    summary = compute_summary(hist)  # Compute the summary statistics from the list of stats
    print(f"Avg KDA: {summary['avg_kda']:.2f}")
    print(f"Avg CS/min: {summary['avg_cs_per_min']:.2f}")
    print(f"Win rate: {summary['win_rate']:.2%}")

def champion_summary(args):
    init_storage()
    # Prompt for queue type if not provided
    queue_type = getattr(args, "queue_type", None) or input("Enter queue type (e.g. Ranked Solo/Duo): ")
    champ_summary = compute_champion_summary(args.champion, queue_type)
    print(f"Champion: {args.champion} ({queue_type})")
    print(f"Avg KDA: {champ_summary['avg_kda']:.2f}")
    print(f"Avg CS/min: {champ_summary['avg_cs_per_min']:.2f}")
    print(f"Win rate: {champ_summary['win_rate']:.2%}")









"""

champion_list = ["Syndra", "Syalas", "viktor", "LeBlanc", "Orrianna"]

def check_KDA(kda):

   if kda <= 1.0:
       return "Needs Work"
   elif kda <= 2.0:
       return "Okay"
   else:
         return "Good"

def game_duration():

    gameTime = [15,25,35,45,60]

    for i in gameTime:
        if i > 30:
            print(f"Game time is {i} minutes")
        else:
            print("Game time is less than 30 minutes")

            
class PerformanceAnalyzer:
    def __init__(self, kda):
        self.kda = kda

    def analyzerKDA(self):
        return check_KDA(self.kda)

"""


"""
Core Concepts in Practice

Variables & Data Types: write a script that stores your top 5 ranked champions in a list and prints them.

Control Flow: write a function that, given a numeric “KDA” value, returns a string “good”, “okay”, or “needs work”.

Loops & Functions: write a loop that reads a list of game durations (ints) and prints how many are over 30 minutes.

Classes & Modules: bundle that KDA logic into a PerformanceAnalyzer class in its own file, then import it into your main script.

"""