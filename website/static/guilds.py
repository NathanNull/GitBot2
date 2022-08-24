from browser import document, timer, ajax
from browser.object_storage import ObjectStorage
from browser.local_storage import storage

store = ObjectStorage(storage)

def check_until_ready(is_ready, func, *args):
    print("checking")
    if is_ready():
        func(*args)
    else:
        timer.set_timeout(check_until_ready, 1000, is_ready, func, *args)

def get_guilds():
    global token
    token = store["token"]
    ajax.get("https://discord.com/api/users/@me/guilds", headers={
        "authorization": f"{token['type']} {token['access']}"
    }, mode="json", oncomplete=recieve_partial_guilds)

def recieve_partial_guilds(result):
    print([s["name"] for s in result.json])
    manage_guild_id = 0x20
    managed_guilds = []
    for idx, partial in enumerate(result.json):
        if int(partial["permissions"]) & manage_guild_id > 0:
            print(f"Got guild {idx+1}/{len(result.json)}")
            managed_guilds.append(partial)
    print([g["name"] for g in managed_guilds])


check_until_ready(lambda:"token" in store, get_guilds)