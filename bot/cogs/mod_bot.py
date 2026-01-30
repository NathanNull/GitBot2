import discord
from discord.ext import commands, tasks
from utils import read_db, update_db, make_config, perm_mod
from configuration import requires, config_type
cursewords = "cursewords"


class Mod(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.cursewords: dict[str, list[str]] = {}
        self.warns: dict[str, list[str]] = {}
        self.config: config_type = self.bot.get_cog(
            "Configuration").configuration

        self.should_save = False

        self.check_updates.start()

    @tasks.loop(seconds=10)
    async def check_updates(self):
        if self.should_save:
            self.should_save = False
            await self.save()

    @discord.slash_command(name="add-blacklisted-word", description="adds blacklisted word to auto moderation", guild_only=True, default_member_permissions=perm_mod)
    @requires.moderation
    async def add_bad_word(self, ctx: discord.ApplicationContext, *, bad_word: str):
        gid = str(ctx.guild.id)
        if gid not in self.cursewords:
            self.cursewords[gid] = []
        if bad_word not in self.cursewords[gid]:
            self.cursewords[gid].append(bad_word)
            await ctx.respond(f"added ||{bad_word}|| to the banned words list")
        else:
            await ctx.respond(f"||{bad_word}|| was already added to the banned words list")
        await self.save()

    @discord.slash_command(name="remove-blacklisted-word", description="removes blacklisted word", guild_only=True, default_member_permissions=perm_mod)
    @requires.moderation
    async def remove_bad_word(self, ctx: discord.ApplicationContext, *, bad_word: str):
        gid = str(ctx.guild.id)
        if gid not in self.cursewords:
            self.cursewords[gid] = []
        try:
            self.cursewords[gid].remove(bad_word)
            await ctx.respond(f"Removed ||{bad_word}|| from the banned words list")
        except ValueError:
            await ctx.respond(f"||{bad_word}|| was already removed from the banned words list")

    @discord.slash_command(guild_only=True, default_member_permissions=perm_mod)
    @requires.moderation
    async def warn(self, ctx: discord.ApplicationContext, *, user: discord.User, reason: str):
        gid = str(ctx.guild.id)
        print(user)
        if gid not in self.warns:
            self.warns[gid] = {}
            await self.save()
        if str(user.id) not in self.warns[gid]:
            self.warns[gid][str(user.id)] = 0
        self.warns[gid][str(user.id)] += 1
        await self.save()
        await ctx.respond(f'<@{ctx.user.id}> has warned <@{user.id}> for {reason}')

    @discord.slash_command(guild_only=True, default_member_permissions=perm_mod)
    @requires.moderation
    async def remove_warn(self, ctx: discord.ApplicationContext, *, user: discord.User, reason: str):
        gid = str(ctx.guild.id)
        print(user)
        if gid not in self.warns:
            self.warns[gid] = {}
            await self.save()
        if str(user.id) not in self.warns[gid]:
            self.warns[gid][str(user.id)] = 0
            await self.save()
        if self.warns[gid][str(user.id)] <= 0:
            await ctx.respond(f'<@{user.id}> does not have any warns')
        else:
            self.warns[gid][str(user.id)] -= 1
            await self.save()
            await ctx.respond(f'<@{ctx.user.id}> has removed a warn for <@{user.id}>')

    @discord.slash_command(guild_only=True, default_member_permissions=perm_mod)
    @requires.moderation
    async def howmanywarns(self, ctx: discord.ApplicationContext, *, user: discord.User):
        gid = str(ctx.guild.id)
        print(user)
        if gid not in self.warns:
            self.warns[gid] = {}
            await self.save()
        if str(user.id) not in self.warns[gid]:
            self.warns[gid][str(user.id)] = 0
            await self.save()
        if self.warns[gid][str(user.id)] <= 0:
            await ctx.respond(f'<@{user.id}> does not have any warns')
        else:
            warnings = self.warns[gid][str(user.id)]
            await ctx.respond(f'<@{user.id}> has {warnings} warnings')

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.id == self.bot.user.id or not message.guild:
            return
        msg_content = message.content.lower()

        # delete curse word if match with the list
        if self.is_swear(msg_content, message.guild.id):
            await message.delete()
            await message.channel.send('no swearing')

    async def save(self):
        update_db("cursewords", self.cursewords)
        update_db("warns", self.warns)
    
    @commands.Cog.listener()
    async def on_ready(self):
        self.warns = read_db("warns")
        self.cursewords = read_db("cursewords")

    def is_swear(self, text: str, guild_id: int) -> bool:
        gid = str(guild_id)
        if gid not in self.config:
            self.config[gid] = make_config()
        if "moderation" in self.config[gid] and not self.config[gid]["moderation"]:
            return
        text = text.lower().replace(" ", "")
        return str(guild_id) in self.cursewords\
            and any(word in text for word in self.cursewords[gid])


def setup(bot: commands.Bot):
    bot.add_cog(Mod(bot))
