from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session

import json
import logging
import requests
import sys
import time

# fill these in!
client_id = 'fillmein'
client_secret = 'fillmein'

# set up logging format incl time
root = logging.getLogger()
root.setLevel(logging.INFO)

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
root.addHandler(ch)

# authorize yourself to smashladder using oauth2
token_url = 'https://www.smashladder.com/oauth/token'
client = BackendApplicationClient(client_id=client_id)
oauth = OAuth2Session(client=client)
token = oauth.fetch_token(token_url=token_url, client_id=client_id, client_secret=client_secret)
headers = {"Authorization":"Bearer {}".format(token["access_token"])}

# main loop
while True:
    time.sleep(2)
    logging.info("Checking for matches...")
    # get your own id
    r = requests.get("https://www.smashladder.com/api/v1/player/me", headers=headers)
    me = json.loads(r.text)
    my_id = me['player']['id']

    # get your current match info
    r = requests.get("https://www.smashladder.com/api/v1/match/current_match", headers=headers)
    match = json.loads(r.text)

    opponent_id = ""
    opponent_username = "Searching for opponent..."
    opponent_location = ""
    opponent_rank = ""
    
    # get the player's info who doesn't match your id
    if "match" in match:
        if match["match"]["player1"]["id"] == my_id:
            opponent_id = str(match["match"]["player2"]["id"])
        else:
            opponent_id = str(match["match"]["player1"]["id"])

        opponent = match["match"]["players"][opponent_id]["player"]
        #logging.info(opponent)
        # get opponents username and location from match info
        opponent_username = "Opponent:\n" + opponent["username"]
        opponent_location = opponent.get("location", {}).get("state", {}).get("name", "Location Unknown")
        # make an additional request to the opponent's profile to get their rank
        r = requests.get("https://www.smashladder.com/api/v1/player/profile?id=" + opponent_id, headers=headers)
        opponent_profile = json.loads(r.text)
        # melee is hardcoded as ladder "2"
        opponent_rank = opponent_profile["user"]["ladder_information"]["2"]["league"].get("name", "Unranked")
        if opponent_rank != "Unranked":
            opponent_rank += " " + opponent_profile["user"]["ladder_information"]["2"]["league"]["division"]

    # write to opponent_info.txt
    f = open("opponent_info.txt", "w")
    f.write("{}\n{}\n{}".format(opponent_username, opponent_location, opponent_rank))
    f.close()
