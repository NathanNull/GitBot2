import discord
from discord.ext import commands, tasks
from utils import guild_only

class Help(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot
    
    def get_info(self, thing:str):
        match thing:
            case "level":
                return "level info"
            case "music":
                return "music infos"
            case "moderation":
                return "mod info"
            case "reaction":
                return "react info"
            case "auditlogs":
                return "audit info"

    @discord.slash_command()
    async def help(self, ctx:discord.ApplicationContext, setting: discord.Option(str,choices=[
                discord.OptionChoice("Level", "level"),
                discord.OptionChoice("Music", "music"),
                discord.OptionChoice("Moderation", "moderation"),
                discord.OptionChoice("Reaction Roles", "reaction"),
                discord.OptionChoice("Audit Logs", "auditlogs")])):
        
        await ctx.respond(self.get_info(setting))

def setup(bot):
    bot.add_cog(Help(bot))