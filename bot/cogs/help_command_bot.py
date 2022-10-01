import discord
from discord.ext import commands, tasks
from utils import guild_only

class Help(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot

    
    @discord.slash_command()
    async def help(self, ctx:discord.ApplicationContext, setting: discord.Option(str,choices=[
                discord.OptionChoice("Level", "level"),
                discord.OptionChoice("Music", "music"),
                discord.OptionChoice("Moderation", "moderation"),
                discord.OptionChoice("Reaction Roles", "reaction"),
                discord.OptionChoice("Audit Logs", "auditlogs")])):
        await ctx.respond(setting)

def setup(bot):
    bot.add_cog(Help(bot))