import discord
from discord.ext import commands
import json
from utils import guild_only


class Configuration(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        with open("configure_bot/configuration.json", "r") as file:
            self.configuration = json.load(file)
            print(list(self.configuration.keys()))
def setup(bot):  # this is called by Pycord to setup the cog
    bot.add_cog(Configuration(bot))