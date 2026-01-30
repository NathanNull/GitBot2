import discord
from discord.ext import commands, tasks
import random
from time import time
from utils import read_db, update_db, perm_mod
from configuration import requires, config_type


class Level(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

        self.levels: dict[str, dict[str, dict[str, int]]] = {}

        self.levelroles: dict[str, dict[str, int]] = {}
        self.config: config_type = self.bot.get_cog(
            "Configuration").configuration

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot\
                or message.content.startswith(self.bot.command_prefix)\
                or not message.guild\
                or (str(message.guild.id) in self.config and not self.config[str(message.guild.id)]["level"]):

            return

        gid = str(message.guild.id)
        uid = str(message.author.id)
        cid = message.guild.id
        if gid not in self.levels:
            self.levels[gid] = {}
        if uid not in self.levels[gid]:
            self.levels[gid][uid] = {"level": 0, "xp": 0, "last_timestamp": 0}

        user_data = self.levels[gid][uid]

        if user_data["last_timestamp"] + 1 < time() and not self.bot.get_cog("Mod").is_swear(message.content, message.guild.id):

            user_data["xp"] += random.randint(5, 20)

            # while instead of if so that if you level up multiple times it works
            while user_data["xp"] >= xp_to_level(user_data["level"]+1):
                user_data["xp"] -= xp_to_level(user_data["level"]+1)
                user_data["level"] += 1
                await self.save()
                await message.channel.send(f"<@{uid}> leveled up to level {user_data['level']}")
                if gid in self.levelroles and str(user_data["level"]) in self.levelroles[gid]:
                    rid = self.levelroles[gid][str(user_data["level"])]
                    await message.author.add_roles(message.guild.get_role(rid))

            user_data["last_timestamp"] = round(time())

    @discord.slash_command(description="Checks the rank of the user", guild_only=True)
    @requires.level
    async def rank(self, ctx: discord.ApplicationContext, *, user: discord.Option(discord.User, required=False)):  # type: ignore
        user: discord.User = user if user else ctx.author

        gid = str(ctx.guild.id)
        uid = str(user.id)
        try:
            rank_check = self.levels[gid][uid]
            xp, lvl = rank_check["xp"], rank_check['level']
        except KeyError:
            await ctx.respond(f"The user {user} has no level yet, tell them to send a message and get one.")
            return
        embed = discord.Embed(title=f"{user}")
        bar = xp_bar(xp, lvl)
        embed.add_field(
            name=f"Level {lvl}, XP {xp}/{xp_to_level(lvl+1)}", value=bar)
        await ctx.respond(embed=embed)

    @discord.slash_command(name="reset-server-xp", description="Resets server XP", guild_only=True, default_member_permissions=perm_mod)
    @requires.level
    async def reset_server(self, ctx: discord.ApplicationContext):
        for user in self.levels[str(ctx.guild.id)]:
            member = ctx.guild.get_member(int(user))
            for rid in self.levelroles[str(ctx.guild.id)].values():
                if any(r.id == rid for r in member.roles):
                    await member.remove_roles(ctx.guild.get_role(rid))
            self.levels[str(ctx.guild.id)][user].update({"level": 0, "xp": 0})
        await self.save()
        await ctx.respond("Cleared all levels in this server")

    @discord.slash_command(name="reset-user-xp", description="Resets users XP", guild_only=True, default_member_permissions=perm_mod)
    @requires.level
    async def reset_user(self, ctx: discord.ApplicationContext, *, user: discord.Option(discord.User)):  # type: ignore
        user: discord.User
        member = ctx.guild.get_member(user.id)
        for rid in self.levelroles[str(ctx.guild.id)].values():
            if any(r.id == rid for r in member.roles):
                await member.remove_roles(ctx.guild.get_role(rid))
        self.levels[str(ctx.guild.id)][str(user.id)
                                       ].update({"level": 0, "xp": 0})
        await self.save()
        await ctx.respond(f"Cleared levels for user {user}")

    @discord.slash_command(guild_only=True, default_member_permissions=perm_mod)
    @requires.level
    async def give_xp(self, ctx: discord.ApplicationContext, *, amount: discord.Option(int), user: discord.Option(discord.User)):  # type: ignore
        amount: int
        user: discord.User
        gid = str(ctx.guild.id)

        if gid not in self.levels:
            self.levels[gid] = {}
        if str(user.id) not in self.levels[gid]:
            self.levels[gid][str(user.id)] = {"level": 0, "xp": 0, "last_timestamp": 0}
        user_data = self.levels[gid][str(user.id)]
        user_data["xp"] += amount
        next_amount = xp_to_level(user_data["level"]+1)
        while next_amount <= user_data["xp"]:
            user_data["level"] += 1
            user_data["xp"] -= next_amount
            next_amount = xp_to_level(user_data["level"]+1)
            if gid in self.levelroles and str(user_data["level"]) in self.levelroles[gid]:
                rid = self.levelroles[gid][str(user_data["level"])]
                await ctx.guild.get_member(user.id).add_roles(ctx.guild.get_role(rid))
        await ctx.guild.get_member(user.id).send(f"You leveled up to level {user_data['level']} in {ctx.guild.name}")
        await ctx.respond(f"Done! The user is now lvl{user_data['level']}", ephemeral=True)

    @discord.slash_command(guild_only=True, default_member_permissions=perm_mod)
    @requires.level
    async def add_level_role(self, ctx: discord.ApplicationContext, *, level: discord.Option(int), role: discord.Role):  # type: ignore
        gid = str(ctx.guild.id)
        if gid not in self.levelroles:
            self.levelroles[gid] = {}
            print(self.levelroles)
        if any(rid == role.id for rid in self.levelroles[gid].values()):
            await ctx.respond("That role is already being used for another level.")
            return
        if str(level) in self.levelroles[gid]:
            await ctx.respond("That level already has a role assigned to it.")
            return
        self.levelroles[gid][str(level)] = role.id
        for user in self.levels[gid]:
            if self.levels[gid][user]["level"] >= level:
                await ctx.guild.get_member(int(user)).add_roles(role)
        await ctx.respond(role.id)
        await self.save()

    @discord.slash_command(guild_only=True, default_member_permissions=perm_mod)
    @requires.level
    async def remove_level_role(self, ctx: discord.ApplicationContext, *, role: discord.Role):
        gid = str(ctx.guild.id)
        if gid not in self.levelroles:
            await ctx.respond("There are no level-assigned roles in this server.")
            return
        if role.id not in self.levelroles[gid].values():
            await ctx.respond("There is no role assigned to this level")
            return
        else:
            level = [k for k, v in self.levelroles[gid].items() if v ==
                     role.id][0]
            del self.levelroles[gid][level]
        await ctx.respond(role.id)
        await self.save()

    @commands.Cog.listener()
    async def on_ready(self):
        self.levels = read_db("levels")

    async def save(self):
        update_db("levels", self.levels)
        # with open("asafuhsriiizdhconfigure_bot/levelroles.jon", "w") as file:
        #     pass#jon.dump(self.levelroles, file, sort_keys=True, indent=4)


def xp_to_level(level: int):
    return (5 * (level ** 2)) + (25 * level) - 10


def xp_bar(xp: int, level: int, length: int = 20):
    to_next = xp_to_level(level+1)
    num_blocks = clamp(round(length*xp/to_next), 1, length-1)

    return "```" + "█"*num_blocks + "-"*(length-num_blocks) + "```"


def clamp(val, mini, maxi):
    return min(max(val, mini), maxi)


def setup(bot):
    bot.add_cog(Level(bot))
