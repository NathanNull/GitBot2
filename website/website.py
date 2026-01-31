from flask import Flask, url_for, render_template
from check_prod import is_prod
from w_backend import add_backend
from flask_cors import CORS

host = "0.0.0.0"

app = Flask(__name__)
CORS(app)

if is_prod:
    discord_login = \
        r"https://discord.com/oauth2/authorize?client_id=985641530356273182&response_type=code&redirect_uri=http%3A%2F%2Fsurfbot.my.to%2Fserverlist&scope=identify+guilds+guilds.join+guilds.members.read"
    
    invite_link = \
        r"https://discord.com/api/oauth2/authorize?client_id=985641530356273182&"+\
        r"permissions=1644971949559&scope=bot%20applications.commands"
else:
    discord_login = \
        r"https://discord.com/oauth2/authorize?client_id=1444562104609669120&response_type=code&redirect_uri=http%3A%2F%2Flocalhost%3A5000%2Fserverlist&scope=guilds.members.read+guilds+guilds.join+identify"

    invite_link = \
        r"https://discord.com/api/oauth2/authorize?client_id=1444562104609669120&"+\
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
    "client_id": "985641530356273182" if is_prod else "1444562104609669120",
    "client_secret": "dEWJxhVGhDQ-lD0UyCVtvZQx8Rk2FVUI" if is_prod else "D81OafFsY8YxMNEwXW7LVQTKbTi87QjF"
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