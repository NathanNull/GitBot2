import websockets
import discord
import json
from utils import basepath

def bot_info(guildid:str, infotype:str):
    match infotype:
        case "config":
            filename = basepath+"/configure_bot/configuration.json"
            process = lambda c:c
            default = {"music":True, "moderation":True, "level":True, "reaction_roles":True}
        case "auditchannel":
            filename = basepath+"/configure_bot/auditlogchannel.json"
            process = lambda c:str(c)
            default = "NotSet"
        case "bannedwords":
            filename = basepath+"/configure_bot/cursewords.json"
            process = lambda c:c
            default = []
        case _:
            return "Invalid info type", 400
    with open(filename) as file:
        data:dict[str] = json.load(file)
        if guildid in data:
            return process(data[guildid])
        else:
            return process(default)