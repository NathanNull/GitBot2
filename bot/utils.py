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
    def __init__(self):
        super().__init__("/notif/*.json")
    def file_update(self, path, contents, deleted=False):
        print("heyyyyy, update")
        if deleted:
            return
        print(json.loads(contents))
        
        print(path)
        os.remove(path)
        