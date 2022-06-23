import discord
from discord.ext import commands, tasks
import json
import random
from time import time
from utils import guild_only

class Level(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        with open("configure_bot/levels.json", "r") as file:
            self.levels = json.load(file)
            print(self.levels)
        self.save.start()
            
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot\
            or message.content.startswith(self.bot.command_prefix)\
            or not message.guild:
            
            return

        gid = str(message.guild.id)
        uid = str(message.author.id)

        if gid not in self.levels:
            self.levels[gid] = {}
        if uid not in self.levels[gid]:
            self.levels[gid][uid] = {"level": 0,"xp": 0,"last_timestamp":0}

        user_data = self.levels[gid][uid]
        
        if user_data["last_timestamp"] + 60 < time() and not self.bot.get_cog("Mod").is_swear(message.content, message.guild.id):
            
            user_data["xp"] += random.randint(5,20)
    
            if user_data["xp"] >= xp_to_level(user_data["level"]+1):
                user_data["xp"] -= xp_to_level(user_data["level"]+1)
                user_data["level"] += 1
                await message.author.send(f"You leveled up to level {user_data['level']} in {message.guild.name}")

            user_data["last_timestamp"] = round(time())

    @discord.slash_command()
    @guild_only
    async def rank(self, ctx, *, user:discord.Option(discord.User, required=False)):
        user = user if user else ctx.author
        
        gid = str(ctx.guild.id)
        uid = str(user.id)
        try:
            rank_check = self.levels[gid][uid]
            xp, lvl = rank_check["xp"],rank_check['level']
        except KeyError:
            await ctx.respond(f"The user {user} has no level yet, tell them to send a message and get one.")
            return
        embed = discord.Embed(title=f"{user}")
        bar = xp_bar(xp,lvl)
        print(bar)
        embed.add_field(name=f"Level {lvl}, XP {xp}/{xp_to_level(lvl+1)}", value=bar)
        await ctx.respond(embed=embed)

    @discord.slash_command()
    @guild_only
    async def reset_server(self, ctx):
        for user in self.levels[str(ctx.guild.id)]:
            self.levels[str(ctx.guild.id)][user].update({"level": 0,"xp": 0})
        await self.save()
        await ctx.respond("Cleared all levels in this server")

    @discord.slash_command()
    @guild_only
    async def reset_user(self, ctx, *, user:discord.Option(discord.User)):
        self.levels[str(ctx.guild.id)][str(user.id)].update({"level": 0,"xp": 0})
        await self.save()
        await ctx.respond(f"Cleared levels for user {user}")

    @discord.slash_command()
    @guild_only
    async def give_xp(self, ctx, *, amount:discord.Option(int), user:discord.Option(discord.User)):
        user_data = self.levels[str(ctx.guild.id)][str(user.id)]
        user_data["xp"] += amount
        next_amount = xp_to_level(user_data["level"]+1)
        while next_amount <= user_data["xp"]:
            user_data["level"] += 1
            user_data["xp"] -= next_amount
            next_amount = xp_to_level(user_data["level"]+1)

    @tasks.loop(minutes=5)
    async def save(self):
        with open("configure_bot/levels.json", "w") as file:
            json.dump(self.levels, file, sort_keys=True, indent=4)
        print("save")

def xp_to_level(level):
    return (5 * (level ** 2)) + (25 * level) - 10

def xp_bar(xp, level, length=20):
    to_next = xp_to_level(level+1)
    num_blocks = clamp(round(length*xp/to_next),1,length-1)

    print(num_blocks, length-num_blocks)
    
    return "```" + "█"*num_blocks + "-"*(length-num_blocks) + "```"

def clamp(val, mini, maxi):
    return min(max(val,mini),maxi)

def setup(bot):
    bot.add_cog(Level(bot))