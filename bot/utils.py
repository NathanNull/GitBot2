from watchdog.events import PatternMatchingEventHandler, FileSystemEvent
from functools import wraps
from typing import Callable
from discord.ext.commands import Cog
import discord
import os, json, asyncio

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

class SingleFolderEventHandler(PatternMatchingEventHandler):
    def __init__(self, filepath, encoding="UTF-8"):
        super().__init__(["."+filepath], None, False, False)
        self.filepath = basepath+filepath
        self.encoding = encoding
    def on_any_event(self, event:FileSystemEvent):
        print(event.event_type, event.src_path)
        match event.event_type:
            case "deleted":
                self.file_update(event.src_path, "", True)
            case "created":
                with open(event.src_path, encoding=self.encoding) as file:
                    contents = file.read()
                self.file_update(event.src_path, contents)
            case _:
                return
            
    def file_update(self, contents, deleted=False):
        pass

class NotifDetector(SingleFolderEventHandler):
    def __init__(self, bot:discord.Bot):
        super().__init__("/notif/*.json")
        self.bot = bot
    def file_update(self, path, contents, deleted=False):
        print("heyyyyy, update")
        if deleted:
            return
        info = json.loads(contents)
        gid = info["gid"]
        if info["type"] == 'config':
            cog = self.bot.get_cog("Configuration")
            if gid not in cog.configuration:
                cog.configuration[gid] = make_config()
            cog.configuration[gid]["music"] = info["info"]["music"]
            cog.configuration[gid]["level"] = info["info"]["level"]
            cog.configuration[gid]["moderation"] = info["info"]["moderation"]
            cog.configuration[gid]["reaction_roles"] = info["info"]["reaction_roles"]
            asyncio.run(cog.save())
        elif info["type"] == 'auditchannel':
            cog = self.bot.get_cog("AuditLogging")
            cog.auditchannel[gid] = info["info"]
            asyncio.run(cog.save())
        elif info["type"] == 'bannedwords':
            cog = self.bot.get_cog("Mod")
            cog.cursewords[gid] = info["info"]
            asyncio.run(cog.save())
        print(path)
        os.remove(path)
        