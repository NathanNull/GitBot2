from flask import Flask, url_for, render_template
from check_prod import is_prod
from w_backend import add_backend
from flask_cors import CORS

host = "0.0.0.0"

app = Flask(__name__)
CORS(app)

if is_prod:
    discord_login = \
        r"https://discord.com/api/oauth2/authorize?client_id=985641530356273182&redirect_uri=http%3A%2F%2Fsurfbot.my.to%2Fserverlist&response_type=code&scope=identify%20guilds%20guilds.members.read%20guilds.join"
    
    invite_link = \
        r"https://discord.com/api/oauth2/authorize?client_id=985641530356273182&"+\
        r"permissions=1644971949559&scope=bot%20applications.commands"
else:
    discord_login = \
        r"https://discord.com/api/oauth2/authorize?client_id=835950957196083201&redirect_uri=http%3A%2F%2Flocalhost%3A8080%2Fserverlist&response_type=code&scope=guilds%20guilds.join%20guilds.members.read%20identify"

    invite_link = \
        r"https://discord.com/api/oauth2/authorize?client_id=835950957196083201&"+\
        r"permissions=1644971949559&scope=bot%20applications.commands"

def getpath(static_path: str):
    return url_for("static", filename=static_path)

def getstyle(name: str):
    return getpath("css/"+name+".css")

def make_page(template_name: str, **local_params: dict):
    return render_template("base_site.html", **PARAMS, **local_params, pagename=template_name)

PARAMS = {
    "login": discord_login,
    "getpath": getpath,
    "getstyle": getstyle,
    "invite": invite_link,
    "client_id": "985641530356273182" if is_prod else "835950957196083201",
    "client_secret": "CswKZV4Ed1ApKlxr0U2o0g45n68HbKFT" if is_prod else "6RBxvFT8dWGQw4nJyRPB-pPHPSTnseUZ"
}

@app.route("/")
def home():
    return make_page("home")

@app.route("/serverlist")
def serverlist():
    return make_page("serverlist")

@app.route("/console/<serverid>")
def console(serverid):
    return make_page("console", serverid=serverid)

add_backend(app)

def main():
    app.run(host, port=8080)

if __name__ == "__main__":
    main()