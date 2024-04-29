from firebase_admin import db, credentials, initialize_app
cred = credentials.Certificate(
    '.\\surfbot-e0d83-firebase-adminsdk-dgaks-b191f56486.json')
url = "https://surfbot-e0d83-default-rtdb.firebaseio.com"
default_app = initialize_app(cred, {'databaseURL': url})

ref = db.reference("/bannedwords/dummy")
ref.set("lmao")