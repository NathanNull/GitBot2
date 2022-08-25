from flask import Flask, url_for, render_template_string, render_template

host = "localhost"

app = Flask(__name__)

discord_login = \
    r"https://discord.com/api/oauth2/authorize?client_id=835950957196083201&"+\
    r"redirect_uri=http%3A%2F%2Flocalhost%3A5000%2Fserverlist&response_type="+\
    r"token&scope=identify%20guilds%20guilds.members.read"

invite_link = \
    r"https://discord.com/api/oauth2/authorize?client_id=835950957196083201&"+\
    r"permissions=1644971949559&scope=bot%20applications.commands"

def getpath(static_path: str):
    return url_for("static", filename=static_path)

def make_page(template_name: str):
    return render_template("base_site.html", **PARAMS, page_content=template_name)

PARAMS = {
    "login": discord_login,
    "getpath": getpath,
    "invite": invite_link
}

@app.route("/")
def home():
    return render_template_string(make_page("index.html"), **PARAMS)

@app.route("/serverlist")
def serverlist():
    return render_template_string(make_page("serverlist.html"), **PARAMS)

def main():
    app.run(host)

if __name__ == "__main__":
    main()