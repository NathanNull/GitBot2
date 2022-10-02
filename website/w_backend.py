import sys, random, json
from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
from requests import get

from dotenv import load_dotenv
import os
from cryptography.fernet import Fernet
load_dotenv()
from check_prod import is_prod

backend = Flask(__name__)
CORS(backend)

key = bytes(os.environ["KEY" if is_prod else "DEVKEY"],"utf-8")
encrypted = bytes(os.environ["TOKEN" if is_prod else "DEVTOKEN"],"utf-8")
token_bytes = Fernet(key).decrypt(encrypted)
token = str(token_bytes)[2:-1]

@backend.route("/botservers")
def get_env():
    guilds: list = get(
        "https://discord.com/api/users/@me/guilds",
        headers={
            "Authorization": "Bot "+token
        }
    ).json()

    response = jsonify(*guilds)
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response

@backend.route("/notify-bot", methods=["POST"])
@cross_origin()
def notify_bot():
    notif = json.dumps(request.json)
    with open(f"./bot/notif/{random.randint(10000,99999)}.json", "x") as file:
        file.write(notif)
    
    response = jsonify(notif)
    return response

@backend.route("/bot-info/<guildid>/<infotype>")
def bot_info(guildid, infotype):
    match infotype:
        case "config":
            response = jsonify()

def main():
    backend.run(port=3001)

if __name__ == "__main__":
    main()