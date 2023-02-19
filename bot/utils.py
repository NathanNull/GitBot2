from functools import wraps
from typing import Callable
from discord.ext.commands import Cog
import discord
import os, json, asyncio, random, threading

def guild_only(cmd:Callable):
    @wraps(cmd)
    async def wrapper(me:Cog, ctx:discord.ApplicationContext, *args, **kwargs):
        if not ctx.guild:
            await ctx.respond("This command isn't enabled in DMs")
            return
        await cmd(me, ctx, *args, **kwargs)
    return wrapper

basedir = os.path.dirname(__file__)
basepath = basedir+os.sep

def make_config():
    config = {
        "level": True,
        "music": True,
        "moderation": True,
        "reaction_roles": True
    }
    return config

'''async def _serve(bot):
    responder = NotifResponder(bot)
    async with websockets.serve(responder.serve, port=8765):
        await asyncio.Future()  # run forever

def serve_botinfo(bot):
    t = threading.Thread(target=lambda *args: asyncio.run(_serve(*args)), args=[bot])
    t.start()
    return t

class NotifResponder:
    def __init__(self, bot:discord.Bot):
        self.bot = bot
    
    async def serve(self, websocket):
        async for message in websocket:
            res = await self.on_message(message)
            if res is not None:
                await websocket.send(res)
    
    async def on_message(self, message:str):
        info = json.loads(message)
        gid = info["gid"]
        diff = info["info"]
        audit = self.bot.get_cog("AuditLogging")
        match info["type"]:
            case 'config':
                cog = self.bot.get_cog("Configuration")
                if gid not in cog.configuration:
                    cog.configuration[gid] = make_config()
                ccgid = cog.configuration[gid]
                ccgid["music"] = diff["music"]
                ccgid["level"] = diff["level"]
                ccgid["moderation"] = diff["moderation"]
                ccgid["reaction_roles"] = diff["reaction_roles"]
                await cog.save()
            case 'auditchannel':
                cog = self.bot.get_cog("AuditLogging")
                cog.auditchannel[gid] = int(diff)
                await cog.save()
            case 'appchannel':
                cog = self.bot.get_cog("App")
                cog.app[gid]['channel'] = int(diff)
                await cog.save()
            case 'bannedwords':
                cog = self.bot.get_cog("Mod")
                cog.cursewords[gid] = diff
                await cog.save()
            case 'reaction':
                cog = self.bot.get_cog("ReactionRoles")
                themessage = info['info']['message']
                rid = int(info['info']['role'])
                emoji = info['info']['emoji']
                cid = int(info['info']['channel'])
                cog.update_info[random.randint(10000,99999)] = (rid, cid, themessage, emoji)
                await cog.save()
        await audit.botupdate(gid)'''