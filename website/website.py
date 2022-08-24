import flask

app = flask.Flask(__name__)

discord_login = \
    r"https://discord.com/api/oauth2/authorize?client_id=835950957196083201&"+\
    r"redirect_uri=http%3A%2F%2Flocalhost%3A5000%2Fserverlist&response_type="+\
    r"token&scope=identify%20guilds%20guilds.members.read"

def getpath(static_path: str):
    return flask.url_for("static", filename=static_path)

base = open("base_site.html").read().split("###INSERT###")
def make_page(template_location: str):
    text = open("templates/"+template_location).read()
    return text.join(base)

PARAMS = {
    "login": discord_login,
    "getpath": getpath
}

@app.route("/")
def home():
    return flask.render_template_string(make_page("index.html"), **PARAMS)

@app.route("/serverlist")
def serverlist():
    return flask.render_template_string(make_page("serverlist.html"), **PARAMS)

def main():
    app.run()

if __name__ == "__main__":
    main()