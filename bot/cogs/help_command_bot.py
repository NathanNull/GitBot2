import discord
from discord.ext import commands, tasks

class Help(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot
    
    def get_info(self, thing:str):
        match thing:
            case "level":
                return """**|-Level Commands-|**
                    /give_xp (Admin Only, well, it's supposed to be.)
                    /reset_user [USER] (Admin Only, well, it's supposed to be.)
                    /reset_server (Admin Only, well, it's supposed to be.)
                    /rank [USER] <-- (optional field)"""
            case "music":
                return """**|-Music Commands-|**
                    /play [SONG]"""
            case "moderation":
                return """**|-Moderation Commands-|**
                    /add_bad_word [WORD]
                    /remove_bad_word [WORD]
                    /config_bot [SETTING] [ENABLE]"""
            case "reaction":
                return """**|-Reaction Commands-|**
                    /reactionsetup [MESSAGE] [EMOJI] [ROLE ID] [CHANNEL]"""
            case "auditlogs":
                return """**|-Audit Log Commands-|**
                    /set_audit_channel [CHANNEL]"""
            case "utility":
                return """**|-Utility Commands-|**
                    /time
                    /ping"""
            case "help":
                return """"But why..." -evin"""

    @discord.slash_command()
    async def help(self, ctx:discord.ApplicationContext, setting: discord.Option(str,choices=[ # type: ignore
        discord.OptionChoice("Level", "level"),
        discord.OptionChoice("Music", "music"),
        discord.OptionChoice("Utility","utility"),
        discord.OptionChoice("Help","help"),
        discord.OptionChoice("Moderation", "moderation"),
        discord.OptionChoice("Audit Logs", "auditlogs")])):

        await ctx.respond(self.get_info(setting))

def setup(bot):
    bot.add_cog(Help(bot))