import json

to_write = {"hey":878854, "glurbe":True, "whee":["7",7,"seven"]}

with open("bot/notif.json", "x") as file:
    file.write(json.dumps(to_write, indent=4))