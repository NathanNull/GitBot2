import discord
from discord.ext import commands, tasks
from configuration import requires
import appinput
import random
from utils import read_db, update_db, perm_mod


async def autocomplete_app_name(ctx: discord.AutocompleteContext):
    apps: dict[str, dict[str, list[str]]] = ctx.cog.app
    gid = str(ctx.interaction.guild_id)
    if gid not in apps or "applications" not in apps[gid]:
        return []
    return [k for k, _ in apps[gid]["applications"].items()]

class App(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot
        self.app: dict[str, dict[str, int | dict[str, list[str]]]] = {}
        self.active_applications: dict[str, tuple[str, str, list[str]]] = {}

    def channelidstuff(self, guild: discord.Guild):
        return self.cid_raw(str(guild.id))

    def cid_raw(self, gid):
        if gid not in self.app:
            return
        return self.bot.get_channel(int(self.app[gid]["channel"]))

    @tasks.loop(seconds=10)
    async def check_updates(self):
        if len(self.update_info) != 0:
            for _, val in self.update_info.items():
                gid = val[0]
                channel = self.cid_raw(gid)
                await channel.send("yay things worked")
            self.update_info = {}

    cmd_grp = discord.SlashCommandGroup("application")

    @cmd_grp.command(description="Create an application for people to apply", guild_only=True, default_member_permissions=perm_mod)
    async def create(self, ctx: discord.ApplicationContext, app_name, question_amount: int):
        await ctx.send_modal(appinput.QuestionInput(cog=self, q_amt=question_amount, title=app_name))

    @cmd_grp.command()
    @discord.option("app_name", autocomplete=autocomplete_app_name)
    async def apply(self, ctx: discord.ApplicationContext, app_name):
        gid = str(ctx.guild_id)
        uid = str(ctx.author.id)
        if app_name not in self.app[gid]["applications"]:
            await ctx.respond(f"Unknown application '{app_name}'", ephemeral=True)
        elif uid not in self.active_applications:
            questions = self.app[gid]["applications"][app_name]
            if await dm(ctx, ctx.author, f"Question 1/{len(questions)}: {questions[0]}"):
                self.active_applications[uid] = (gid, app_name, [])
            await ctx.respond("Worked", ephemeral=True)
        else:
            await ctx.respond("Can't start an application while you already have one", ephemeral=True)
        # await ctx.send_modal(appinput.AnswerInput(cog=self, questions=self.app[gid]["applications"][app_name], title=app_name))

    async def save(self):
        update_db('appchannel', self.app)
    
    @commands.Cog.listener()
    async def on_ready(self):
        self.app = read_db("appchannel")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # Filter messages that are not application-relevant
        if not isinstance(message.channel, discord.DMChannel):
            return
        uid = str(message.author.id)
        if uid not in self.active_applications:
            return
        
        # Get application info
        (gid, app, answers) = self.active_applications[uid]
        try:
            questions = self.app[gid]["applications"][app]
        except IndexError:
            del self.active_applications[uid]
            return
        
        answers.append(message.content)

        # Ask next question
        try:
            next_question = questions[len(answers)]
        except:
            embed = discord.Embed(title=f"Answers to {app}")
            for q, a in zip(questions, answers):
                embed.add_field(name=q, value=a, inline=False)
            await self.cid_raw(gid).send(f'this application is from <@{uid}>')
            await self.cid_raw(gid).send(embed=embed)
            del self.active_applications[uid]
            return
        await message.channel.send(f"Question {len(answers)+1}/{len(questions)}: {next_question}")

def setup(bot):
    bot.add_cog(App(bot))

async def dm(ctx: discord.ApplicationContext, user: discord.User, message: str) -> bool:
    try:
        await user.send(message)
        return True
    except discord.Forbidden:
        uid = user.id
        await ctx.respond(f'<@{uid}>If you would like to apply to the server you ran this in then please unblock the bot and try again')
        return False