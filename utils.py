from functools import wraps
import json
from discord.ext import tasks

def guild_only(cmd):
    @wraps(cmd)
    async def wrapper(me, ctx, *args, **kwargs):
        if not ctx.guild:
            await ctx.respond("This command isn't enabled in DMs")
            return
        await cmd(me, ctx, *args, **kwargs)
    return wrapper

with open("configure_bot/configuration.json", "r") as file:
    server_config = json.load(file)