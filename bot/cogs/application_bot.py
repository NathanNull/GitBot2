import discord
from discord.ext import commands, tasks
from configuration import requires
import appinput
import random
from utils import update_db


async def autocomplete_app_name(ctx: discord.AutocompleteContext):
    apps: dict[str, dict[str, list[str]]] = ctx.cog.app
    gid = str(ctx.interaction.guild_id)
    return [k for k, _ in apps[gid]["applications"].items()]

class App(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

        self.app: dict[str, dict[str, int | dict[str, list[str]]]] = {}

    def channelidstuff(self, guild: discord.Guild):
        return self.cid_raw(str(guild.id))

    def cid_raw(self, gid):
        if gid not in self.app:
            return
        return self.bot.get_channel(int(self.app[gid]["channel"]))

    async def botupdate(self, gid):
        self.update_info[random.randint(10000, 99999)] = [gid]

    @tasks.loop(seconds=10)
    async def check_updates(self):
        if len(self.update_info) != 0:
            for _, val in self.update_info.items():
                gid = val[0]
                channel = self.cid_raw(gid)
                await channel.send("yay things worked")
            self.update_info = {}

    cmd_grp = discord.SlashCommandGroup("application")

    @cmd_grp.command(description="Create an application for people to apply")
    async def create(self, ctx: discord.ApplicationContext, app_name, question_amount: int):
        await ctx.send_modal(appinput.QuestionInput(cog=self, q_amt=question_amount, title=app_name))

    @cmd_grp.command()
    @discord.option("app_name", autocomplete=autocomplete_app_name)
    async def apply(self, ctx: discord.ApplicationContext, app_name):
        gid = str(ctx.guild_id)
        await ctx.send_modal(appinput.AnswerInput(cog=self, questions=self.app[gid]["applications"][app_name], title=app_name))
        await self.channelidstuff(ctx.guild).send('worked')
    
    async def save(self):
        update_db('appchannel', self.app)

def setup(bot):
    bot.add_cog(App(bot))
