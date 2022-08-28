from flask import Flask, jsonify
from requests import get

from dotenv import load_dotenv
import os
from cryptography.fernet import Fernet
load_dotenv()

backend = Flask(__name__)

is_prod = "IS_PROD" in os.environ and os.environ["IS_PROD"] == "yes"

@backend.route("/botservers")
def get_env():
    key = bytes(os.environ["KEY" if is_prod else "DEVKEY"],"utf-8")
    encrypted = bytes(os.environ["TOKEN" if is_prod else "DEVTOKEN"],"utf-8")
    token_bytes = Fernet(key).decrypt(encrypted)
    token = str(token_bytes)[2:-1]

    guilds: list = get(
        "https://discord.com/api/users/@me/guilds",
        headers={
            "Authorization": "Bot "+token
        }
    ).json()

    response = jsonify(*guilds)
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response

def main():
    backend.run(port=3001)

if __name__ == "__main__":
    main()