import discord
from discord.ext import commands, tasks
from utils import guild_only

class Help(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot
    
    def get_info(self, thing:str):
        match thing:
            case "level":
                return "**|-Level Commands-|**\n\t/give_xp (Admin Only, well, it's supposed to be.)\n\t/reset_user [USER] (Admin Only, well, it's supposed to be.)\n\t/reset_server (Admin Only, well, it's supposed to be.)\n\t/rank [USER] <-- (optional field)\n\t"
            case "music":
                return "**|-Music Commands-|**\n\t/play [SONG]"
            case "moderation":
                return "**|-Moderation Commands-|**\n\t/add_bad_word [WORD]\n\t/remove_bad_word [WORD]\n\t/config_bot [SETTING] [ENABLE]\n\t"
            case "reaction":
                return "**|-Reaction Commands-|**\n\t/reactionsetup [MESSAGE] [EMOJI] [ROLE ID] [CHANNEL]\n\t"
            case "auditlogs":
                return "**|-Audit Log Commands-|**\n\t/set_audit_channel [CHANNEL]\n\t"
            case "utility":
                return "**|-Utility Commands-|**\n\t/time\n\t/ping\n\t"
            case "help":
                return "\"But why...\" -evin"

    @discord.slash_command()
    async def help(self, ctx:discord.ApplicationContext, setting: discord.Option(str,choices=[
                discord.OptionChoice("Level", "level"),
                discord.OptionChoice("Music", "music"),
                discord.OptionChoice("Utility","utility"),
                discord.OptionChoice("Help","help"),
                discord.OptionChoice("Moderation", "moderation"),
                discord.OptionChoice("Reaction Roles", "reaction"),
                discord.OptionChoice("Audit Logs", "auditlogs")])):

        await ctx.respond(self.get_info(setting))

def setup(bot):
    bot.add_cog(Help(bot))