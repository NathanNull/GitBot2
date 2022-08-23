import flask, threading

app = flask.Flask(__name__, template_folder=".")

@app.route("/")
def home():
    return flask.render_template("index.html")

if __name__ == "__main__":
    app.run()
else:
    threading.Thread(target=app.run).start()