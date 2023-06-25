import discord
from discord.ext import commands, tasks
import json
import random
from time import time
from utils import basepath, perm_mod
from configuration import requires, config_type

class Level(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot
        with open(basepath+"configure_bot/levels.json", "r") as file:
            self.levels:dict[str,dict[str,dict[str,int]]] = json.load(file)
        with open(basepath+"configure_bot/levelroles.json", "r") as file:
            self.levelroles:dict[str,dict[str,dict[str,int]]] = json.load(file)
        self.config:config_type = self.bot.get_cog("Configuration").configuration
        self.save.start()
            
    @commands.Cog.listener()
    async def on_message(self, message:discord.Message):
        if message.author.bot\
            or message.content.startswith(self.bot.command_prefix)\
            or not message.guild\
            or (str(message.guild.id) in self.config and not self.config[str(message.guild.id)]["level"]):
            
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

    @discord.slash_command(description="Checks the rank of the user", guild_only=True)
    @requires.level
    async def rank(self, ctx:discord.ApplicationContext, *, user:discord.Option(discord.User, required=False)):
        user:discord.User = user if user else ctx.author
        
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
        embed.add_field(name=f"Level {lvl}, XP {xp}/{xp_to_level(lvl+1)}", value=bar)
        await ctx.respond(embed=embed)

    @discord.slash_command(name="reset-server-xp", description="Resets server XP", guild_only=True, default_member_permissions=perm_mod)
    @requires.level
    async def reset_server(self, ctx:discord.ApplicationContext):
        for user in self.levels[str(ctx.guild.id)]:
            self.levels[str(ctx.guild.id)][user].update({"level": 0,"xp": 0})
        await self.save()
        await ctx.respond("Cleared all levels in this server")

    @discord.slash_command(name="reset-user-xp", description="Resets users XP", guild_only=True, default_member_permissions=perm_mod)
    @requires.level
    async def reset_user(self, ctx:discord.ApplicationContext, *, user:discord.Option(discord.User)):
        user:discord.User
        self.levels[str(ctx.guild.id)][str(user.id)].update({"level": 0,"xp": 0})
        await self.save()
        await ctx.respond(f"Cleared levels for user {user}")

    @discord.slash_command(guild_only=True, default_member_permissions=perm_mod)
    @requires.level
    async def give_xp(self, ctx:discord.ApplicationContext, *, amount:discord.Option(int), user:discord.Option(discord.User)):
        amount:int; user:discord.User

        user_data = self.levels[str(ctx.guild.id)][str(user.id)]
        user_data["xp"] += amount
        next_amount = xp_to_level(user_data["level"]+1)
        while next_amount <= user_data["xp"]:
            user_data["level"] += 1
            user_data["xp"] -= next_amount
            next_amount = xp_to_level(user_data["level"]+1)

    @discord.slash_command(guild_only=True, default_member_permissions=perm_mod)
    @requires.level
    async def add_level_role(self, ctx:discord.ApplicationContext, *, level:discord.Option(int), role:discord.Option(discord.guild.fetch_roles)):
        gid = str(ctx.guild.id)
        if gid not in self.levelroles:
            self.levelroles[gid] = {}
            print(self.levelroles)



    @tasks.loop(minutes=5)
    async def save(self):
        with open(basepath+"configure_bot/levels.json", "w") as file:
            json.dump(self.levels, file, sort_keys=True, indent=4)

def xp_to_level(level:int):
    return (5 * (level ** 2)) + (25 * level) - 10

def xp_bar(xp:int, level:int, length:int=20):
    to_next = xp_to_level(level+1)
    num_blocks = clamp(round(length*xp/to_next),1,length-1)
    
    return "```" + "█"*num_blocks + "-"*(length-num_blocks) + "```"

def clamp(val, mini, maxi):
    return min(max(val,mini),maxi)

def setup(bot):
    bot.add_cog(Level(bot))