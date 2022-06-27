from __future__ import unicode_literals

import ensure_libs
ensure_libs.ready()

#Imports the packages
import discord
from discord.ext import commands, tasks
import os
import datetime
import pytz
from itertools import cycle
from cryptography.fernet import Fernet
from dotenv import load_dotenv

#Define variables to make the rest run
load_dotenv()
key = bytes(os.environ["KEY"],"utf-8")
token_bytes = Fernet(key).decrypt(bytes(os.environ['TOKEN'],"utf-8"))
token = str(token_bytes)[2:-1]
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!')

#Slash commands
@bot.slash_command()
async def time(ctx):
    timestamp = round(datetime.datetime.utcnow().timestamp())
    await ctx.respond(f"<t:{timestamp}:F> (<t:{timestamp}:R>)")


@bot.slash_command()
async def ping(ctx):
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

print("hi")
#Runs the bot
for cog in os.listdir("cogs"):
    if os.path.isfile("cogs/"+cog):
        bot.load_extension('cogs.' + cog[:-3])
        print(f"loaded cog {cog}")
bot.run(token)
