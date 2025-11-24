import discord
from discord.ext import commands, tasks
from functools import wraps
from typing import Callable
from utils import update_db, perm_mod


class Configuration(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

        self.configuration: dict[str, dict[str, bool]] = {}

        global config
        config = self.configuration

        self.save.start()

    @discord.slash_command(name="configure-bot", description="Configure the bot settings", guild_only=True, default_member_permissions=perm_mod)
    async def config_bot(self, ctx: discord.ApplicationContext, *,
                         setting: discord.Option(str, choices=[ # type: ignore
                             discord.OptionChoice("Level", "level"),
                             discord.OptionChoice("Music", "music"),
                             discord.OptionChoice("Moderation", "moderation"),
                             discord.OptionChoice(
                                 "Reaction Roles", "reaction_roles")
                         ]),
                         enable: discord.Option(bool, "Turn on or off?") # type: ignore
                         ):
        setting: str
        enable: bool

        gid = str(ctx.guild.id)

        if gid not in self.configuration:
            self.configuration[gid] = {
                "moderation": True, "level": True, "music": True, 'reaction_roles': True}

        if self.configuration[gid][setting] == enable:
            await ctx.respond(f"{setting.capitalize()} was already {'enabled' if enable else 'disabled'} for this server")
        else:
            self.configuration[gid][setting] = enable
            await ctx.respond(f"{setting.capitalize()} is now {'enabled' if enable else 'disabled'} for this server")
            await self.save()

    @tasks.loop(minutes=1)
    async def save(self):
        update_db("config", self.configuration)

def check_config(type_: str):
    def decorator(cmd: Callable):
        @wraps(cmd)
        async def wrapper(me: commands.Cog, ctx: discord.ApplicationContext, *args, **kwargs):
            global config
            if str(ctx.guild.id) in config and not config[str(ctx.guild.id)][type_]:
                await ctx.respond(f"{type_.capitalize()} commands have been disabled in this server")
                return
            await cmd(me, ctx, *args, **kwargs)
        return wrapper
    return decorator


def setup(bot: commands.Bot):
    bot.add_cog(Configuration(bot))
