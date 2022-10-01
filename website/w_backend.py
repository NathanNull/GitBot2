import sys, random
from flask import Flask, jsonify
from requests import get

from dotenv import load_dotenv
import os
from cryptography.fernet import Fernet
load_dotenv()
from check_prod import is_prod

backend = Flask(__name__)

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

@backend.route("/notify-bot/<notif>")
def notify_bot(notif):
    #notif = json.dumps(request.json)
    print(notif)
    with open(f"./bot/notif/{random.randint(10000,99999)}.json", "x") as file:
        file.write(notif)
    
    response = jsonify({"yeah":"ok"})
    response.headers.add("Access-Control-Allow-Origin", "*")
    print(response.access_control_allow_headers)
    sys.stdout.flush()
    return response

def main():
    backend.run(port=3001)

if __name__ == "__main__":
    main()