# Make sure libraries and such are up to date
# Imports the packages
import sys
import os
from utils import set_hooks
from dotenv import load_dotenv
from encryption import decrypt
from itertools import cycle
import datetime
from discord.ext import commands, tasks
import discord
import ensure_libs
ensure_libs.ready()



# Need this so run.py can log the prints properly.
# Otherwise subprocess.Popen doesn't count them as
# 'real' stdout lines


@tasks.loop(seconds=3)
async def flush_prints():
    sys.stdout.flush()
flush_prints.start()

# Define variables to make the rest run
load_dotenv()
prod = not ("IS_DEV" in os.environ and os.environ["IS_DEV"] == "yes")

token = decrypt(
    os.environ["TOKEN" if prod else "DEV_TOKEN"],
    os.environ["KEY" if prod else "DEV_KEY"]
)
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

# Slash commands

@bot.slash_command()
async def time(ctx: discord.ApplicationContext):
    timestamp = round(datetime.datetime.now().timestamp())
    await ctx.respond(f"<t:{timestamp}:F> (<t:{timestamp}:R>)")


@bot.slash_command()
async def ping(ctx: discord.ApplicationContext):
    rounded_ping = round((bot.latency * 1000), 5)
    await ctx.respond(f"Pong! Latency is {rounded_ping} ms")

status = cycle([
    lambda: discord.Activity(type=discord.ActivityType.listening, name="song"),
    lambda: discord.Game("with your mind"),
    lambda: discord.Activity(
        type=discord.ActivityType.watching, name=f'{len(bot.guilds)} Servers'),
    lambda: discord.Game("2D Minecraft")
])


@tasks.loop(seconds=10)
async def change_status():
    await bot.change_presence(activity=next(status)())


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    try:
        change_status.start()
    except:
        print('had error but is fine')
    else:
        pass


@bot.event
async def on_connect():
    try:
        await super(type(bot), bot).on_connect()
    except discord.errors.HTTPException as e:
        print(f"had error {e.code} ({e.text}), was fine")

# Runs the bot
all_cogs = [
    "configuration_bot",
    "audit_logs_bot",
    "level_bot",
    "mod_bot",
    "music_bot",
    "reaction_bot",
    "help_command_bot",
    "application_bot"
]
for cog in all_cogs:
    bot.load_extension('cogs.' + cog)

if len(bot.extensions) != len(all_cogs):
    raise Exception("Cog problem idk")

set_hooks(bot)
bot.run(token)
# me when the when the, when the when
