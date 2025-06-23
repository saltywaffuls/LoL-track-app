from module1 import run_account, run_progress  # Import functions for account stats and progress tracking
from module6 import start_gui
from module5 import init_storage  # Import functions for data storage and retrieval
import argparse, requests
from urllib.parse import quote  # For URL encoding of summoner names
from datetime import datetime, timedelta
import traceback

def main():

# 1) Parse command-line arguments
    parser = argparse.ArgumentParser("LoL Track")
    sub = parser.add_subparsers(dest="command")  # <-- remove required=True

    # define stats subcommand
    stats_p = sub.add_parser("stats", help="Fetch recent games and update history | stats <SummonerName> [--tag_line na1] [--matches N]")
    stats_p.add_argument("summoner_name", help="Your in-client summoner name (spaces allowed)")
    stats_p.add_argument("--tag_line",    default="na1", help="Platform tag_line (na1, euw1, etc.)")
    stats_p.add_argument("--matches",   type=int, default=20, help="How many recent games to analyze")
    stats_p.add_argument("--champion", "-c",   help="If given, only show stats for this champion (name or ID)")
    stats_p.add_argument("--queue_type", "-qt", default="Ranked Solo/Duo", help="Queue type (e.g. Ranked Solo/Duo, ARAM, etc.)")
    

    # define progress subcommand
    prog_p = sub.add_parser("progress", help="show history | progress [--days X]")
    prog_p.add_argument("--days", type=int, default=20, help="shows progress over the last X days")

    init_storage()

    # Parse the command-line arguments
    args = parser.parse_args()  
    if args.command == "stats":  # If the command is 'progress', load and display historical data  
        run_account(args.summoner_name, args.tag_line, args.matches)  # Call the function to fetch and display account stats
    elif args.command == "progress": # If the command is 'stats', fetch and display recent game stats
        run_progress(args)
    else:
        # No command given: launch GUI
        start_gui()

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
    except Exception as e:
        traceback.print_exc()  # <--- Add this line!
        print("Unexpected error:", e)