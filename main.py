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
    await ctx.respond(getTime())


@bot.slash_command()
async def ping(ctx):
    rounded_ping = round((bot.latency * 1000), 5)
    await ctx.respond(f"Pong! Latency is {rounded_ping} ms")


def getTime():
    #set time zone
    t = pytz.utc.localize(datetime.datetime.utcnow()).astimezone(
        pytz.timezone("America/Los_Angeles"))

    #Converts the day of the week from integer to day
    days = [
        "Monday", "Tuesday", "Wednesday", "Thursday", "Thursday", "Friday",
        "Saturday", "Sunday"
    ]
    weekday = days[t.weekday()]

    #Convert the time to am or pm
    if t.hour < 12:
        hour = t.hour
        ampm = 'am'
    elif t.hour == 12:
        hour = t.hour
        ampm = 'pm'
    elif t.hour > 12:
        hour = t.hour - 12
        ampm = 'pm'
    else:
        hour = 'ERR'
        ampm = 'OR'

    #gets the month, day, and time from datetime
    return t.strftime(f'{weekday}, %B %d, {hour}:%M{ampm}')


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
        print(f"had error {e.code}, was fine")

print("hi")
#Runs the bot
bot.load_extension('cogs.music_bot')
bot.load_extension('cogs.level_bot')
bot.load_extension('cogs.mod_bot')
bot.run(token)
