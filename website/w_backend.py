from check_prod import is_prod
from cryptography.fernet import Fernet
from dotenv import load_dotenv
import random
import json
from typing import Any
from flask import Flask, jsonify, request
from flask_cors import cross_origin
from requests import get, post
from firebase_admin import db, credentials, initialize_app

import os
basedir = os.path.dirname(__file__)
basepath = os.path.abspath(os.path.join(basedir, os.pardir))

load_dotenv(basepath+"/website/.env")

cred = credentials.Certificate(
    r'./surfbot-e0d83-firebase-adminsdk-dgaks-b191f56486.json' if is_prod else r'./testing-99c64-firebase-adminsdk-t7j1l-9fc9429ff6.json')
url = "https://surfbot-e0d83-default-rtdb.firebaseio.com" if is_prod else "https://testing-99c64-default-rtdb.firebaseio.com"
default_app = initialize_app(cred, {'databaseURL': url})

key = bytes(os.environ["KEY" if is_prod else "DEVKEY"], "utf-8")
encrypted = bytes(os.environ["TOKEN" if is_prod else "DEVTOKEN"], "utf-8")
token_bytes = Fernet(key).decrypt(encrypted)
token = str(token_bytes)[2:-1]


def api_get_request(url):
    return jsonify(get(
        url, headers={
            "Authorization": "Bot "+token
        }
    ).json())


def send_dm(uid, message):
    print(uid)
    res = post('https://discord.com/api/users/@me/channels', json={'recipient_id': uid}, headers={
        "Authorization": "Bot "+token,
        'Content-Type': 'application/json'
    }).json()
    channel_id = res['id']
    post(f'https://discord.com/api/channels/{channel_id}/messages', json={'content': message}, headers={
        "Authorization": "Bot "+token,
        'Content-Type': 'application/json'
    })


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
        notif = request.json
        category = notif["type"]
        gid = notif["gid"]
        info = notif["info"]

        match category:
            case "auditchannel" | "config" | "bannedwords":
                print(f"{info=}")
                db.reference(f"/{category}/{gid}").set(info)
            case "reaction":
                db.reference(f"/add_reaction/{gid}").push(info)
            case "appchannel":
                db.reference(f"/{category}/{gid}/channel").set(info)
            case _:
                return "What even is this", 400

        return "All good", 200

    @app.route("/api/bot-info/<guildid>/<infotype>")
    @cross_origin()
    def bot_info(guildid: str, infotype: str):
        match infotype:
            case "config":
                def process(c): return c
                default = {"music": True, "moderation": True,
                           "level": True, "reaction_roles": True}
            case "auditchannel":
                def process(c): return f'"{str(c)}"'
                default = "NotSet"
            case "bannedwords":
                def process(w): return w
                default = []
            case _:
                return "Invalid info type", 400
        ref = db.reference(f"/{infotype}/{guildid}")
        data: dict[str, Any] = ref.get()
        if data is not None:
            return process(data)
        else:
            return process(default)

    @app.route('/api/sendmsg', methods=['POST'])
    @cross_origin()
    def send_msg():
        msg = request.json
        print(msg)
        send_dm(701878045413474314, msg)
        send_dm(634189650608652310, msg)
        return 'yes', 200
