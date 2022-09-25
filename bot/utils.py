from watchdog.events import PatternMatchingEventHandler, FileSystemEvent
from functools import wraps
from typing import Callable
from discord.ext.commands import Cog
import discord
import os, time, json

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
        "moderation": True
    }
    return config

class SingleFileEventHandler(PatternMatchingEventHandler):
    def __init__(self, filepath, encoding="UTF-8"):
        super().__init__([filepath], None, False, False)
        self.filepath = filepath
        self.encoding = encoding
        self.last_timestamp = time.time()
    def on_any_event(self, event:FileSystemEvent):
        if self.last_timestamp + 0.2 < time.time():
            self.last_timestamp = time.time()
            
            if event.event_type == "deleted":
                self.file_update("", True)
                return
            with open(self.filepath, encoding=self.encoding) as file:
                contents = file.read()
            self.file_update(contents)
            
    def file_update(self, contents, deleted=False):
        pass

class NotifDetector(SingleFileEventHandler):
    def __init__(self):
        super().__init__("./bot/notif.json")
    def file_update(self, contents, deleted=False):
        print("heyyyyy, update")
        if deleted:
            return
        print(json.loads(contents))
        os.remove("./bot/notif.json")
        