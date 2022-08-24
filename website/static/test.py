from browser import window, document, ajax
from browser.local_storage import storage
from browser.object_storage import ObjectStorage
from urllib.parse import urlparse

nav = document.select(".navbar")[0]
store = ObjectStorage(storage)

def try_idx(s:str, char:str, idx:int):
    substrings = s.split(char)
    try:
        return substrings[idx]
    except:
        return ""

def onload():
    url = window.location.href
    frag_args = {try_idx(p,"=",0):try_idx(p,"=",1) for p in urlparse(url).fragment.split("&")}

    access_token, token_type = frag_args.get("access_token"), frag_args.get("token_type")

    if not access_token:
        nav.select("#login")[0].style.display = "inline-block"
        return
    
    ajax.get("https://discord.com/api/users/@me", headers={
        "authorization": f"{token_type} {access_token}"
    }, mode="json", oncomplete=on_discord_info)
    store["token"] = {"access":access_token, "type":token_type}

def on_discord_info(result):
    json = result.json
    uname, disc = json["username"], json["discriminator"]
    store["discord_user_data"] = json
    nav.select("#info")[0].text = f"{uname}#{disc}"

onload()