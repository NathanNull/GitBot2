from watchdog.events import PatternMatchingEventHandler, FileSystemEvent
from functools import wraps
from typing import Callable
from discord.ext.commands import Cog
import discord
import os, json, asyncio, random

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

class NotifDetector(Cog):
    def __init__(self, bot:discord.Bot):
        self.bot = bot
    
    @Cog.listener()
    async def on_message(self, message:discord.Message):
        if message.guild is None\
        or message.channel.id != 1036385135567831051\
        or message.author.id != self.bot.user.id:
            print("no")
            return
        
        info = json.loads(message.content)
        gid = info["gid"]
        audit = self.bot.get_cog("AuditLogging")
        if info["type"] == 'config':
            cog = self.bot.get_cog("Configuration")
            if gid not in cog.configuration:
                cog.configuration[gid] = make_config()
            cog.configuration[gid]["music"] = info["info"]["music"]
            cog.configuration[gid]["level"] = info["info"]["level"]
            cog.configuration[gid]["moderation"] = info["info"]["moderation"]
            cog.configuration[gid]["reaction_roles"] = info["info"]["reaction_roles"]
            asyncio.run(audit.botupdate(gid))
            asyncio.run(cog.save())
        elif info["type"] == 'auditchannel':
            cog = self.bot.get_cog("AuditLogging")
            cog.auditchannel[gid] = int(info["info"])
            asyncio.run(cog.save())
        elif info["type"] == 'appchannel':
            cog = self.bot.get_cog("App")
            cog.app[gid]['channel'] = int(info["info"])
            asyncio.run(cog.save())
        elif info["type"] == 'bannedwords':
            cog = self.bot.get_cog("Mod")
            cog.cursewords[gid] = info["info"]
            cog.should_save = True
        elif info["type"] == 'reaction':
            cog = self.bot.get_cog("ReactionRoles")
            themessage = info['info']['message']
            rid = int(info['info']['role'])
            emoji = info['info']['emoji']
            cid = int(info['info']['channel'])
            cog.update_info[random.randint(10000,99999)] = (rid, cid, themessage, emoji)
            asyncio.run(cog.save())
        