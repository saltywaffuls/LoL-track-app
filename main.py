from module2 import get_riot_ID, get_summoner_ID  # Import necessary functions and constants
from module3 import get_lol_match_ID, get_match_data,  extract_my_stats, compute_summary
from module5 import init_storage, save_match_data, load_data  # Import functions for data storage and retrieval
import argparse, requests
from urllib.parse import quote  # For URL encoding of summoner names
from datetime import datetime, timedelta

def main():

# 1) Parse command-line arguments
    parser = argparse.ArgumentParser("LoL Track")
    sub = parser.add_subparsers(dest="command", required=True)  # Create a subparser for commands

    # define stats subcommand
    stats_p = sub.add_parser("stats", help="Fetch recent games and update history | stats <SummonerName> [--tag_line na1] [--matches N]")
    stats_p.add_argument("summoner_name", help="Your in-client summoner name (spaces allowed)")
    stats_p.add_argument("--tag_line",    default="na1", help="Platform tag_line (na1, euw1, etc.)")
    stats_p.add_argument("--matches",   type=int, default=20, help="How many recent games to analyze")
    

    # define progress subcommand
    prog_p = sub.add_parser("progress", help="show history | progress [--days X]")
    prog_p.add_argument("--days", type=int, default=20, help="shows progress over the last X days")

    # Parse the command-line arguments
    args = parser.parse_args()  
    if args.command == "stats":  # If the command is 'progress', load and display historical data  
        run_account(args)  # Call the function to fetch and display account stats
    elif args.command == "progress": # If the command is 'stats', fetch and display recent game stats
        run_progress(args)
    else:
        parser.print_help  # Call the function to show progress

def run_account(args):
        name = quote(args.summoner_name)
        puuid = get_riot_ID(name, args.tag_line)  # Fetch the PUUID using the provided summoner name and region
        summ = get_summoner_ID(puuid, args.tag_line)  # Fetch the summoner data using the PUUID
        print(f"Level: {summ['summonerLevel']}  Icon: {summ['profileIconId']}")

        match_ids = get_lol_match_ID(puuid, start=0, count=args.matches)  # Fetch the match IDs for the provided PUUID

        stats = [extract_my_stats(get_match_data(mid), puuid)
                  for mid in match_ids 
                  if extract_my_stats(get_match_data(mid), puuid)]  # Extract stats for each match ID
        init_storage()  # Initialize the CSV file for storing historical stats
        for s in stats:
            s["summoner_id"] = args.summoner_name  # Add the summoner name to the data
            s["tag_line"] = args.tag_line               # Add the tag_line to the data
            s["ingest_date"] = datetime.now().strftime("%m-%d-%Y %H:%M:%S")  # (optional: overwrite date with save time)
            save_match_data(s)  # Save the match data to the CSV file

        summary = compute_summary(stats)  # Compute the summary statistics from the list of stats
        print(f"\nOver last {args.matches} games:")
        print(f"Avg KDA: {summary['avg_kda']:.2f}")
        print(f"Avg CS/min: {summary['avg_cs_per_min']:.2f}")
        print(f"Win rate: {summary['win_rate']:.2%}")
        print(f"Acg dmg/game: {summary['avg_damage']:.2f}")
        print(f"Avg kill participation: {summary['avg_kp']:.2%}")
        print(f"Avg gold per game: {summary['avg_gold']:.2f}")
        print(f"Abg vision score per game: {summary['avg_vision']:.2f}")
    


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

if __name__ == "__main__":
    try:
        main()
    except requests.HTTPError as http_err:
        code = http_err.response.status_code
        if code == 404:
            print("❌  Not found—check your summoner name and region.")
        elif code == 429:
            print("⏳  Rate limit exceeded—please wait a bit and try again.")
        else:
            print(f"HTTP {code} error: {http_err.response.text}")
    # Catch-all for unexpected errors that are not HTTP-related.
    # This ensures the program does not crash and provides a message for debugging.
    except Exception as e:
        print("Unexpected error:", e)