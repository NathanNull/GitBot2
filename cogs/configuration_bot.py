import discord
from discord.ext import commands, tasks
import json
from functools import wraps
from utils import guild_only

class Configuration(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        with open("configure_bot/configuration.json", "r") as file:
            self.configuration = json.load(file)
            print(list(self.configuration.keys()))
        
        global config
        config = self.configuration

        self.save.start()

    @discord.slash_command()
    @guild_only
    async def config_bot(self, ctx, *, 
            setting: discord.Option(str,choices=[
                discord.OptionChoice("Level", "level"),
                discord.OptionChoice("Music", "music"),
                discord.OptionChoice("Moderation", "moderation")
            ]),
            enable: discord.Option(bool, "Turn on or off?")
        ):

        gid = str(ctx.guild.id)
        print(enable, self.configuration[gid][setting])

        if gid not in self.configuration:
            self.configuration[gid] = {"moderation": True,"level": True,"music":True}

        if self.configuration[gid][setting] == enable:
            await ctx.respond(f"{setting.capitalize()} was already {'enabled' if enable else 'disabled'} for this server")
        else:
            self.configuration[gid][setting] = enable
            await ctx.respond(f"{setting.capitalize()} is now {'enabled' if enable else 'disabled'} for this server")
            await self.save()
        

    @tasks.loop(minutes=20)
    async def save(self):
        with open("configure_bot/configuration.json", "w") as file:
            json.dump(self.configuration, file, sort_keys=True, indent=4)
        print("save config")

def check_config(type_):
    def decorator(cmd):
        @wraps(cmd)
        async def wrapper(me, ctx, *args, **kwargs):
            global config
            if str(ctx.guild.id) in config and not config[str(ctx.guild.id)][type_]:
                await ctx.respond(f"{type_.capitalize()} commands have been disabled in this server")
                return
            await cmd(me, ctx, *args, **kwargs)
        return wrapper
    return decorator

def setup(bot):
    bot.add_cog(Configuration(bot))