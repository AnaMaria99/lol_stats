import os
from datetime import datetime

from dotenv import load_dotenv
from flask import Flask, render_template, request
import requests

from utils import get_champion_id_name

app = Flask(__name__)

load_dotenv()  # Load environment variables from .env

RIOT_API_KEY = os.getenv('RIOT_API_KEY')
print(RIOT_API_KEY)  # Should print your API key
# Replace with your Riot Games API Key
REGION = "europe"  # Change to the platform region (e.g., 'euw1', 'na1', 'kr')
REGIONAL_ROUTING = "eun1"  # Change based on account region ('americas', 'europe', 'asia')

# URLs for Riot API
SUMMONER_BY_NAME_URL = f"https://{REGION}.api.riotgames.com/riot/account/v1/accounts/by-riot-id"
CHAMPION_MASTERY_URL = f"https://{REGIONAL_ROUTING}.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-puuid"
RANKED_STATS_URL = f"https://{REGIONAL_ROUTING}.api.riotgames.com/lol/league/v4/entries/by-summoner"
SUMMONER_ID_URL = f"https://{REGIONAL_ROUTING}.api.riotgames.com/lol/summoner/v4/summoners/by-puuid"
MATCH_HISTORY_URL = f"https://{REGION}.api.riotgames.com/lol/match/v5/matches/by-puuid"
MATCH_DETAILS_URL = f"https://{REGION}.api.riotgames.com/lol/match/v5/matches"
#TODO: Lcreate a class which contains the regions and api links for requests

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/profile', methods=['POST'])
def get_summoner_profile():
    summoner_name = request.form['summoner_name']
    summoner_tagline = request.form['summoner_tagline']

    # Get the summoner's data
    response = requests.get(f"{SUMMONER_BY_NAME_URL}/{summoner_name}/{summoner_tagline}",
                            headers={"X-Riot-Token": RIOT_API_KEY})

    if response.status_code != 200:
        return f"Error fetching summoner data: {response.status_code}"

    summoner_data = response.json()

    puuid = summoner_data['puuid']
    summoner_gameName = summoner_data['gameName']

    response2 = requests.get(f"{SUMMONER_ID_URL}/{str(puuid)}", headers={"X-Riot-Token": RIOT_API_KEY})
    if response2.status_code != 200:
        return f"Error fetching summoner id: {response2.status_code}"
    summoner_data2 = response2.json()
    summoner_id = summoner_data2.get("id")
    print("error in template ")
    return render_template('profile.html', summoner_data=summoner_data, summoner_name=summoner_gameName, puuid=puuid, summoner_id=summoner_id)


@app.route('/ranked_stats/<combo>')
def get_ranked_stats(combo):
    # Get ranked stats for the summoner
    puuid, summoner_id = combo.split("****")
    ranked_response = requests.get(f"{RANKED_STATS_URL}/{summoner_id}",
                                   headers={"X-Riot-Token": RIOT_API_KEY})

    if ranked_response.status_code != 200:
        return f"Error fetching ranked stats: {ranked_response.status_code}"

    ranked_stats = ranked_response.json()

    return render_template('ranked_stats.html', ranked_stats=ranked_stats, summoner_id=summoner_id, puuid=puuid)


@app.route('/champion_mastery/<puuid_summoner_id>')
def get_champion_mastery(puuid_summoner_id):
    # Get champion mastery data for the summoner
    puuid, summoner_id = puuid_summoner_id.split("****")
    mastery_response = requests.get(f"{CHAMPION_MASTERY_URL}/{puuid}",
                                    headers={"X-Riot-Token": RIOT_API_KEY})

    if mastery_response.status_code != 200:
        return f"Error fetching champion mastery data: {mastery_response.status_code}"

    mastery_data = mastery_response.json()
    champion_names = get_champion_id_name()
    for champion in mastery_data:
        champion["championName"] = champion_names[str(champion["championId"])]
        champion["lastPlayTime"] = datetime.utcfromtimestamp(champion["lastPlayTime"]/1000).strftime('%Y-%m-%d %H:%M:%S')

    return render_template('champion_mastery.html', mastery_data=mastery_data, puuid=puuid, summoner_id=summoner_id)



@app.route('/match_history/<puuid>')
def get_match_history(puuid):
    # Get match history for the summoner's account
    match_response = requests.get(f"{MATCH_HISTORY_URL}/{puuid}/ids?start=0&count=20",
                                  headers={"X-Riot-Token": RIOT_API_KEY})

    if match_response.status_code != 200:
        return f"Error fetching match history: {match_response.status_code}"

    match_history_ids = match_response.json()

    # Fetch details for each match
    match_details = []
    for match_id in match_history_ids:
        details_response = requests.get(f"{MATCH_DETAILS_URL}/{match_id}",
                                        headers={"X-Riot-Token": RIOT_API_KEY})
        if details_response.status_code == 200:
            match_details.append(details_response.json())
    response2 = requests.get(f"{SUMMONER_ID_URL}/{str(puuid)}", headers={"X-Riot-Token": RIOT_API_KEY})
    if response2.status_code != 200:
        return f"Error fetching summoner id: {response2.status_code}"
    summoner_data2 = response2.json()
    summoner_id = summoner_data2.get("id")

    return render_template('match_history.html', match_details=match_details, puuid=puuid, summoner_id=summoner_id)

@app.route('/profile/<summoner_name_tagline>')
def get_know_player_profile(summoner_name_tagline):
    summoner_name, summoner_tagline = str(summoner_name_tagline).split('****')
    response = requests.get(f"{SUMMONER_BY_NAME_URL}/{summoner_name}/{summoner_tagline}",
                            headers={"X-Riot-Token": RIOT_API_KEY})

    if response.status_code != 200:
        return f"Error fetching summoner data: {response.status_code}"

    summoner_data = response.json()

    puuid = summoner_data['puuid']

    response2 = requests.get(f"{SUMMONER_ID_URL}/{str(puuid)}", headers={"X-Riot-Token": RIOT_API_KEY})
    if response2.status_code != 200:
        return f"Error fetching summoner id: {response.status_code}"
    summoner_data2 = response2.json()
    summoner_id = summoner_data2.get("id")

    return render_template('profile.html', summoner_data=summoner_data, summoner_name=summoner_name, puuid=puuid,
                           summoner_id=summoner_id, summoner_data2=summoner_data2)


if __name__ == "__main__":
    app.run(debug=True)
