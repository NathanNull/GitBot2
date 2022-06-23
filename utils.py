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

def check_config(type):
    def decorator(cmd):
        @wraps(cmd)
        async def wrapper(me, ctx, *args, **kwargs):
            global server_config
            if str(ctx.guild.id) in server_config and not server_config[str(ctx.guild.id)]:
                await ctx.respond("That command has been disabled in this server")
                return
            await cmd(me, ctx, *args, **kwargs)
        return wrapper
    return decorator

@tasks.loop(minutes=5)
async def save():
    with open("configure_bot/levels.json", "w") as file:
        json.dump(server_config, file, sort_keys=True, indent=4)
    print("save (config)")
save.start()