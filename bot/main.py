#Make sure libraries and such are up to date
import ensure_libs
ensure_libs.ready()

#Imports the packages
import discord
from discord.ext import commands, tasks
import os
import datetime
from itertools import cycle
from encryption import decrypt
from dotenv import load_dotenv

#Define variables to make the rest run
load_dotenv()
prod = "IS_PROD" in os.environ and os.environ["IS_PROD"] == "yes"
token = decrypt(os.environ["TOKEN" if prod else "DEVTOKEN"], os.environ["KEY" if prod else "DEVKEY"])
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!')

#Slash commands
@bot.slash_command()
async def time(ctx:discord.ApplicationContext):
    timestamp = round(datetime.datetime.now().timestamp())
    await ctx.respond(f"<t:{timestamp}:F> (<t:{timestamp}:R>)")

@bot.slash_command()
async def ping(ctx:discord.ApplicationContext):
    rounded_ping = round((bot.latency * 1000), 5)
    await ctx.respond(f"Pong! Latency is {rounded_ping} ms")

status = cycle([
    discord.Activity(type=discord.ActivityType.listening, name="song"),
    discord.Game("with your mind"),
    discord.Activity(type=discord.ActivityType.watching, name="you"),
    discord.Game("2D Minecraft")
])

@tasks.loop(seconds=10)
async def change_status():
    await bot.change_presence(activity=next(status))

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    change_status.start()

@bot.event
async def on_connect():
    try:
        await super(type(bot),bot).on_connect()
    except discord.errors.HTTPException as e:
        print(f"had error {e.code} ({e.text}), was fine")

print("hey look guys it's me doin the stuff")
#Runs the bot
for cog in [
    "configuration_bot",
    "audit_logs_bot",
    "level_bot",
    "mod_bot",
    "music_bot",
    "reaction_bot"
]:
    bot.load_extension('cogs.' + cog)
    print(f"loaded cog {cog}")
print(bot.extensions)
bot.run(token)