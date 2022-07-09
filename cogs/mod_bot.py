import discord
from discord.ext import commands, tasks
import json

from utils import guild_only
from configuration import requires
cursewords = "cursewords"

class Mod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        with open("configure_bot/cursewords.json", "r") as file:
            self.cursewords = json.load(file)
            print(list(self.cursewords.keys()))
        self.config = self.bot.get_cog("Configuration").configuration
        self.save.start()
        


    
    @discord.slash_command()
    @guild_only
    @requires.moderation
    async def add_bad_word(self, ctx, *, bad_word):
        gid = str(ctx.guild.id)
        if gid not in self.cursewords:
            self.cursewords[gid] = {}
        if bad_word not in self.cursewords[gid]:
            self.cursewords[gid][cursewords] = bad_word
            await ctx.respond(f"added ||{bad_word}|| to the banned words list")
        else:
            await ctx.respond(f"||{bad_word}|| was already added to the banned words list")



        print(self.cursewords)
        await self.save()

    @discord.slash_command()
    @guild_only
    @requires.moderation
    async def remove_bad_word(self, ctx, *, bad_word):
        gid = str(ctx.guild.id)
        word_data = self.cursewords[gid][cursewords]
        if gid not in self.cursewords:
            self.cursewords[gid] = {}
        if bad_word in word_data:
            self.cursewords[gid][cursewords][bad_word] = ""
            await ctx.respond(f"removed ||{bad_word}|| from the banned words list")
        else:
            await ctx.respond(f"||{bad_word}|| was already removed from the banned words list")
        print(self.cursewords)
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.id == self.bot.user.id or not message.guild:
            return
        msg_content = message.content.lower()
    
        # delete curse word if match with the list
        if self.is_swear(msg_content, message.guild.id):
            await message.delete()
            await message.channel.send('no swearing')

        print(self.cursewords)
        await self.save()

    @tasks.loop(minutes=20)
    async def save(self):
        with open("configure_bot/cursewords.json", "w") as file:
            json.dump(self.cursewords, file, sort_keys=True, indent=4)
        print("save cursewords")

    def is_swear(self, text, guild_id):
        gid = str(guild_id)
        if not self.config[gid]["moderation"]:
            return
        text = text.lower()
        return str(guild_id) in self.cursewords\
        and any(word for word in self.cursewords[gid][cursewords])
        
def setup(bot):
    bot.add_cog(Mod(bot))