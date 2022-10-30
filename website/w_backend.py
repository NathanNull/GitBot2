import random, json
from typing import Any
from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
from requests import get, post

from dotenv import load_dotenv
import os
from cryptography.fernet import Fernet
load_dotenv()
from check_prod import is_prod

basedir = os.path.dirname(__file__)
basepath = os.path.abspath(os.path.join(basedir, os.pardir))
botpath = basepath+"/bot"

notif_cid = 1036385135567831051

backend = Flask(__name__)
CORS(backend)

key = bytes(os.environ["KEY" if is_prod else "DEVKEY"],"utf-8")
encrypted = bytes(os.environ["TOKEN" if is_prod else "DEVTOKEN"],"utf-8")
token_bytes = Fernet(key).decrypt(encrypted)
token = str(token_bytes)[2:-1]

def api_get_request(url):
    return get(
        url, headers={
            "Authorization": "Bot "+token
        }
    ).json()

@backend.route("/botservers")
@cross_origin()
def get_env():
    return api_get_request("https://discord.com/api/users/@me/guilds")

@backend.route("/server/<gid>")
@cross_origin()
def get_server(gid):
    return api_get_request(f"https://discord.com/api/guilds/{gid}")

@backend.route("/channels/<gid>")
@cross_origin()
def get_channels(gid):
    return api_get_request(f"https://discord.com/api/guilds/{gid}/channels")

@backend.route("/roles/<gid>")
@cross_origin()
def get_roles(gid):
    return api_get_request(f"https://discord.com/api/guilds/{gid}/roles")

@backend.route("/notify-bot", methods=["POST"])
@cross_origin()
def notify_bot():
    notif = json.dumps(request.json)
    n_res = post(f"https://discord.com/api/channels/{notif_cid}/messages", {
        "content": notif
    }, headers={
        "Authorization": "Bot "+token
    }).json()
    print(n_res)
    response = jsonify(notif)
    return response

@backend.route("/bot-info/<guildid>/<infotype>")
@cross_origin()
def bot_info(guildid:str, infotype:str):
    match infotype:
        case "config":
            filename = botpath+"/configure_bot/configuration.json"
            process = lambda c:c
            default = {"music":True, "moderation":True, "level":True, "reaction_roles":True}
        case "auditchannel":
            filename = botpath+"/configure_bot/auditlogchannel.json"
            process = lambda c:str(c)
            default = "NotSet"
        case "bannedwords":
            filename = botpath+"/configure_bot/cursewords.json"
            process = lambda w:w
            default = []
        case _:
            return "Invalid info type", 400
    with open(filename) as file:
        data:dict[str,Any] = json.load(file)
        if guildid in data:
            return process(data[guildid])
        else:
            return process(default)

def main():
    backend.run(port=3001)

if __name__ == "__main__":
    main()