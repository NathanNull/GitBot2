import random, json
from typing import Any
from flask import Flask, jsonify, request
from flask_cors import cross_origin
from requests import get, post

import os
basedir = os.path.dirname(__file__)
basepath = os.path.abspath(os.path.join(basedir, os.pardir))
botpath = basepath+"/bot"

from dotenv import load_dotenv
from cryptography.fernet import Fernet
load_dotenv(basepath+"/website/.env")
from check_prod import is_prod

key = bytes(os.environ["KEY" if is_prod else "DEVKEY"],"utf-8")
encrypted = bytes(os.environ["TOKEN" if is_prod else "DEVTOKEN"],"utf-8")
token_bytes = Fernet(key).decrypt(encrypted)
token = str(token_bytes)[2:-1]

def api_get_request(url):
    return jsonify(get(
        url, headers={
            "Authorization": "Bot "+token
        }
    ).json())

def add_backend(app):
    @app.route("/api/botservers")
    @cross_origin()
    def get_env():
        print('getting thing')
        return api_get_request("https://discord.com/api/users/@me/guilds")

    @app.route("/api/server/<gid>")
    @cross_origin()
    def get_server(gid):
        return api_get_request(f"https://discord.com/api/guilds/{gid}")

    @app.route("/api/channels/<gid>")
    @cross_origin()
    def get_channels(gid):
        return api_get_request(f"https://discord.com/api/guilds/{gid}/channels")

    @app.route("/api/roles/<gid>")
    @cross_origin()
    def get_roles(gid):
        return api_get_request(f"https://discord.com/api/guilds/{gid}/roles")

    @app.route("/api/notify-bot", methods=["POST"])
    @cross_origin()
    def notify_bot():
        notif = json.dumps(request.json)
        with open(botpath+f"/notif/{random.randint(10000,99999)}.json", "x") as file:
            file.write(notif)
        response = jsonify(notif)
        return response

    @app.route("/api/bot-info/<guildid>/<infotype>")
    @cross_origin()
    def bot_info(guildid:str, infotype:str):
        match infotype:
            case "config":
                filename = botpath+"/configure_bot/configuration.json"
                process = lambda c:c
                default = {"music":True, "moderation":True, "level":True, "reaction_roles":True}
            case "auditchannel":
                filename = botpath+"/configure_bot/auditlogchannel.json"
                process = lambda c:f'"{str(c)}"'
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