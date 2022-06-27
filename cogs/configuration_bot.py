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

    @discord.slash_command()
    #@guild_only
    async def config_moderation(self, ctx, *, moderation: discord.Option(str,choices=[
        discord.OptionChoice("Yes Moderation", "True"),
        discord.OptionChoice("No Moderation", "False")])):
        if moderation == True:
            ctx.respond("Moderation is now enabled")
        elif moderation == False:
            ctx.respond("Moderation is now disabled")
def setup(bot):
    bot.add_cog(Configuration(bot))