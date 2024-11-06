import requests


class Regions:
    def __init__(self):
        self._regions = ["br1", "eun1", "euw1", "jp1", "kr1", "la1", "la2", "na1", "oc1", "tr1", "ru", "ph2", "sg2",
                         "th2", "tw2", "vn2"]
        self._regional_routing = ["europa", "americas", "asia", "sea"]

    def get_region(self, region: str):
        for r in self._regions:
            if region.lower() == r:
                return r
        return None

    def get_regional(self, region: str):
        for r in self._regional_routing:
            if region.lower() == r:
                return r
        return None


class RequestsLinks:
    def __init__(self, region, riot_key, region_routing=None):
        self._region = region
        self._region_routing = region_routing
        self._riot_api_key = riot_key

    def get_summoner_by_name(self):
        if self._region:
            return f"https://{self._region}.api.riotgames.com/riot/account/v1/accounts/by-riot-id"
        return None

    def get_champion_mastery(self):
        if self._region_routing:
            return f"https://{self._region_routing}.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-puuid"

    def get_ranked_stats(self):
        if self._region_routing:
            return f"https://{self._region_routing}.api.riotgames.com/lol/league/v4/entries/by-summoner"

    def get_summoner_id(self, puuid):
        if self._region_routing:
            response2 = requests.get(
                f"https://{self._region_routing}.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{str(puuid)}",
                headers={"X-Riot-Token": self._riot_api_key})
            if response2.status_code != 200:
                return f"Error fetching summoner id: {response2.status_code}"

    def get_match_history(self):
        if self._region:
            return f"https://{self._region}.api.riotgames.com/lol/match/v5/matches/by-puuid"
        return None

    def get_match_details(self):
        if self._region:
            return f"https://{self._region}.api.riotgames.com/lol/match/v5/matches"
        return None


def get_champion_id_name():
    latest_version = requests.get("https://ddragon.leagueoflegends.com/api/versions.json").json()[0]
    champion_url = f"https://ddragon.leagueoflegends.com/cdn/{latest_version}/data/en_US/champion.json"
    champion_response = requests.get(champion_url)
    champion_data = champion_response.json()
    return {champion["key"]: champion["name"] for champion in champion_data["data"].values()}
