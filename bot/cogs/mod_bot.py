import discord
from discord.ext import commands, tasks
import json

from utils import guild_only, basepath
from configuration import requires, config_type
cursewords = "cursewords"

class Mod(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot
        with open(basepath+"configure_bot/cursewords.json", "r") as file:
            self.cursewords:dict[str,list[str]] = json.load(file)
            print(list(self.cursewords.keys()))
        self.config:config_type = self.bot.get_cog("Configuration").configuration
        self.save.start()
            
    @discord.slash_command()
    @guild_only
    @requires.moderation
    async def add_bad_word(self, ctx:discord.ApplicationContext, *, bad_word:str):
        gid = str(ctx.guild.id)
        if gid not in self.cursewords:
            self.cursewords[gid] = []
        if bad_word not in self.cursewords[gid]:
            self.cursewords[gid].append(bad_word)
            await ctx.respond(f"added ||{bad_word}|| to the banned words list")
        else:
            await ctx.respond(f"||{bad_word}|| was already added to the banned words list")

        print(self.cursewords)
        await self.save()

    @discord.slash_command()
    @guild_only
    @requires.moderation
    async def remove_bad_word(self, ctx:discord.ApplicationContext, *, bad_word:str):
        gid = str(ctx.guild.id)
        if gid not in self.cursewords:
            self.cursewords[gid] = []
        try:
            self.cursewords[gid].remove(bad_word)
            await ctx.respond(f"Removed ||{bad_word}|| from the banned words list")
        except ValueError:
            await ctx.respond(f"||{bad_word}|| was already removed from the banned words list")
        print(self.cursewords)

    @commands.Cog.listener()
    async def on_message(self, message:discord.Message):
        if message.author.id == self.bot.user.id or not message.guild:
            return
        msg_content = message.content.lower()
    
        # delete curse word if match with the list
        if self.is_swear(msg_content, message.guild.id):
            await message.delete()
            await message.channel.send('no swearing')

        print(self.cursewords)

    @tasks.loop(minutes=20)
    async def save(self):
        with open(basepath+"configure_bot/cursewords.json", "w") as file:
            json.dump(self.cursewords, file, sort_keys=True, indent=4)
        print("save cursewords")

    def is_swear(self, text:str, guild_id:int) -> bool:
        gid = str(guild_id)
        if not self.config[gid]["moderation"]:
            return
        text = text.lower().replace(" ", "")
        return str(guild_id) in self.cursewords\
            and any(word in text for word in self.cursewords[gid])
        
def setup(bot:commands.Bot):
    bot.add_cog(Mod(bot))