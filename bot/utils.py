from functools import wraps
from typing import Callable
import os
from discord.ext.commands import Cog
import discord

def guild_only(cmd:Callable):
    @wraps(cmd)
    async def wrapper(me:Cog, ctx:discord.ApplicationContext, *args, **kwargs):
        if not ctx.guild:
            await ctx.respond("This command isn't enabled in DMs")
            return
        await cmd(me, ctx, *args, **kwargs)
    return wrapper

basepath = os.path.dirname(__file__)+os.sep

def make_config():
    config = {
        "level": True,
        "music": True,
        "moderation": True
    }
    return config