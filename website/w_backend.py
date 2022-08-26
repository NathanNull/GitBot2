from flask import Flask, jsonify

from dotenv import load_dotenv
import os
from cryptography.fernet import Fernet
load_dotenv()

backend = Flask(__name__)

@backend.route("/token")
def get_env():
    key = bytes(os.environ["DEVKEY"],"utf-8")
    encrypted = bytes(os.environ["DEVTOKEN"],"utf-8")
    token_bytes = Fernet(key).decrypt(encrypted)
    token = str(token_bytes)[2:-1]
    response = jsonify(token=token)
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response

def main():
    backend.run(port=3001)

if __name__ == "__main__":
    main()