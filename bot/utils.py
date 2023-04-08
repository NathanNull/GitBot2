from functools import wraps
from typing import Callable
from discord.ext.commands import Cog
from watchdog.events import PatternMatchingEventHandler, FileSystemEvent
import discord
import os, json, asyncio, random, threading

# def guild_only(cmd:Callable):
#     @wraps(cmd)
#     async def wrapper(me:Cog, ctx:discord.ApplicationContext, *args, **kwargs):
#         if not ctx.guild:
#             await ctx.respond("This command isn't enabled in DMs")
#             return
#         await cmd(me, ctx, *args, **kwargs)
#     return wrapper
perm_mod = discord.Permissions(administrator=True)

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

class SingleFolderEventHandler(PatternMatchingEventHandler):
    def __init__(self, filepath, encoding="UTF-8"):
        super().__init__(["."+filepath], None, False, False)
        self.filepath = basepath+filepath
        self.encoding = encoding
    def on_any_event(self, event:FileSystemEvent):
        match event.event_type:
            case "deleted":
                asyncio.run(self.file_update(event.src_path, "", True))
            case "created":
                with open(event.src_path, encoding=self.encoding) as file:
                    contents = file.read()
                asyncio.run(self.file_update(event.src_path, contents))
            case _:
                return
            
    async def file_update(self, path, contents, deleted=False):
        pass

class NotifDetector(SingleFolderEventHandler):
    def __init__(self, bot:discord.Bot):
        self.bot = bot
        super().__init__("/notif/*.json")
    
    async def serve(self, websocket):
        async for message in websocket:
            res = await self.on_message(message)
            if res is not None:
                await websocket.send(res)
    
    async def file_update(self, path, contents, deleted=False):
        if deleted:
            return
        info = json.loads(contents)
        gid = info["gid"]
        diff = info["info"]
        audit = self.bot.get_cog("AuditLogging")
        match info["type"]:
            case 'config':
                cog = self.bot.get_cog("Configuration")
                if gid not in cog.configuration:
                    cog.configuration[gid] = make_config()
                ccgid: 'dict[str, str]' = cog.configuration[gid]
                ccgid["music"] = diff["music"]
                ccgid["level"] = diff["level"]
                ccgid["moderation"] = diff["moderation"]
                ccgid["reaction_roles"] = diff["reaction_roles"]
                await cog.save()
                print("wheeeeeeeeee")
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
        await audit.botupdate(gid)
        os.remove(path)