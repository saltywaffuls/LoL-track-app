from module2 import get_riot_ID, get_summoner_ID  # Import necessary functions and constants
from module3 import get_lol_match_ID, get_match_data, extract_my_stats, compute_summary
import argparse, requests
from urllib.parse import quote  # For URL encoding of summoner names

def main():
    pass

# 1) Parse command-line arguments
    parser = argparse.ArgumentParser("LoL Track")
    parser.add_argument("summoner_name", help="Your in-client summoner name (spaces allowed)")
    parser.add_argument("--region",    default="na1", help="Platform region (na1, euw1, etc.)")
    parser.add_argument("--matches",   type=int, default=20, help="How many recent games to analyze")
    args = parser.parse_args()


    puuid = get_riot_ID(args.summoner_name, args.region)  # Fetch the PUUID using the provided summoner name and region
    summ = get_summoner_ID(puuid, args.region)  # Fetch the summoner data using the PUUID
    print(f"Level: {summ['summonerLevel']}  Icon: {summ['profileIconId']}")

    match_ids = get_lol_match_ID(puuid, start=0, count=args.matches)  # Fetch the match IDs for the provided PUUID

    stats = []
    for match_id in match_ids:
        match_data = get_match_data(match_id,)  # Fetch the match data using the match ID
        my_stats = extract_my_stats(match_data, puuid)  # Extract the player's stats from the match data
        if my_stats:  # If stats are found, append them to the list
            stats.append(my_stats)

    summary = compute_summary(stats)  # Compute the summary statistics from the list of stats
    print(f"\nOver last {args.matches} games:")
    print(f"Avg KDA: {summary['avg_kda']:.2f}")
    print(f"Avg CS/min: {summary['avg_cs_per_min']:.2f}")
    print(f"Win rate: {summary['win_rate']:.2%}")

#safe_name = quote(summoner_name)  # Encodes spaces and special characters in the summoner name

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
        print("Unexpected error:", e)