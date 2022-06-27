import discord
from discord.ext import commands
import json
from utils import guild_only, check_config


class Mod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        with open("configure_bot/cursewords.json", "r") as file:
            self.cursewords = json.load(file)
            print(list(self.cursewords.keys()))
        self.config = self.bot.get_cog("Configuration").configuration
        

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.id == self.bot.user.id or not message.guild:
            return
        msg_content = message.content.lower()
    
        # delete curse word if match with the list
        if self.is_swear(msg_content, message.guild.id):
            await message.delete()
            await message.channel.send('no swearing')

    def is_swear(self, text, guild_id):
        gid = str(guild_id)
        if self.config[gid]["moderation"] == "false":
            return
        text = text.lower()
        return str(guild_id) in self.cursewords\
        and any(word in text for word in self.cursewords[str(guild_id)])
        
def setup(bot):
    bot.add_cog(Mod(bot))