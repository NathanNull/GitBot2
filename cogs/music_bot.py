import discord
from discord.ext import commands
from views import View, queue
from youtube_dl import YoutubeDL
from discord.utils import get
import requests
import time
from utils import guild_only

FFMPEG_OPTIONS = {
    'before_options':
    '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

#no touchy touchy (I touched it)

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.do_loop = "none"
        self.volume = 1.0

        self.now_playing = None

        self.skipped = False

    def is_connected(self, ctx):
        voice_client = get(self.bot.voice_clients, guild=ctx.guild)
        return voice_client and voice_client.is_connected()

    async def when_done(self, ctx, video, source, when_started):
        print("running")
        stopped_prematurely = (video["duration"] > (time.time()-when_started)) and not self.skipped
        self.skipped = False
        if stopped_prematurely:
            await ctx.send("The song had an error, try again later")
        if self.do_loop == "song":
            print("looping")
            queue.insert(0, (video, source))
        elif self.do_loop == "queue":
            print("queue loop")
            queue.append((video, source))
        elif self.do_loop == "none":
            print("Not looping")
        await self.check_queue(ctx)

    async def play_song(self, ctx, vc, video, source, embed=True):
        if embed:
            await ctx.send(embed=make_song_embed(video), view=View(self.bot, self))

        audio = discord.PCMVolumeTransformer(
            (discord.FFmpegPCMAudio(source, **FFMPEG_OPTIONS)), self.volume)
        current_time = time.time()
        vc.play(audio, after=lambda e: self.bot.loop.create_task(
                        self.when_done(ctx, video, source, current_time)))
        

    async def check_queue(self, ctx, embed=True):
        if len(queue) != 0:
            vc = ctx.guild.voice_client
            video, source = queue.pop(0)
            await self.play_song(ctx, vc, video, source, embed)
        else:
            await ctx.send("No songs in queue")

    @discord.slash_command()
    @guild_only
    async def play(self, ctx, *, query):
        await ctx.defer() #very useful much nice
        voice = ctx.author.voice.channel

        if self.is_connected(ctx):
            print("hello")
            vc = get(self.bot.voice_clients, guild=ctx.guild)

        else:
            print(voice)
            vc = await voice.connect()
            print("connected")

        dur_seconds = sum([int(v['duration']) for (v, s) in queue])
        
        video, source = search(query)
        queue.append((video, source))
        print("Finished downloading")

        if vc.is_playing():
            print(dur_seconds)
            cs_duration = f"{int(video['duration']//60):02d}, {int(video['duration']%60):02d}"
            print(cs_duration)
            time_to_play = f"{dur_seconds//60:02d}:{int(dur_seconds%60):02d}"
            print(time_to_play)
            embed = discord.Embed(title="Added song to queue",description=f"The song {video['title']} is now in the queue. Estimated time until it plays: {time_to_play}")
            await ctx.followup.send(embed=embed)
        else:
            await ctx.followup.send(embed=make_song_embed(video),
                                    view=View(self.bot, self))
            await self.check_queue(ctx, False)

    @discord.slash_command()
    @guild_only
    async def play_playlist(self, ctx, *, url):
        await ctx.defer() #very useful much nice
        voice = ctx.author.voice.channel

        if self.is_connected(ctx):
            print("hello")
            vc = get(self.bot.voice_clients, guild=ctx.guild)

        else:
            print(voice)
            vc = await voice.connect()
            print("connected")

        dur_seconds = sum([v['duration'] for (v, s) in queue])#need to do this before adding new elements
        
        vids = get_playlist(url)
        for video, source in vids:
            queue.append((video, source))
        print("Finished downloading")

        if vc.is_playing():
            time_to_play = f"{dur_seconds//60:02d}:{dur_seconds%60:02d}"
            embed = discord.Embed(title="Added song to queue",description=f"The playlist is now in the queue. Estimated time until it plays: {time_to_play}")
            await ctx.followup.send(embed=embed)
        else:
            await ctx.followup.send(embed=make_song_embed(video),
                                    view=View(self.bot, self))
            await self.check_queue(ctx, False)

    @discord.slash_command()
    @guild_only
    async def joinvc(self, ctx):
        voice = ctx.author.voice.channel
        if not voice:
            await ctx.respond("You aren't in a voice channel!")
        if not self.is_connected(ctx):
            print("trying to connect")
            await voice.connect()
            print("connected")
            await ctx.respond('joined vc')

    @discord.slash_command()
    @guild_only
    async def checkvolume(self, ctx):
        await ctx.respond(f"The Volume of the music is at {self.volume*100}%")

    @discord.slash_command()
    @guild_only
    async def changevolume(self, ctx, thevolume: discord.Option(
        float,
        "What Do You Want The Volume At?",
        min_value=0,
        max_value=100,
        default=100)):
        self.volume = thevolume / 100

        if ctx.guild.voice_client:
            vc = ctx.guild.voice_client
            vc.source.volume = self.volume

        await ctx.respond(f"The Volume Is Now Set To {self.volume*100}%")

    @discord.slash_command()
    @guild_only
    async def loopsong(self, ctx, set: discord.Option(str,choices=[
        discord.OptionChoice("This song", "song"),
        discord.OptionChoice("The queue", "queue"),
        discord.OptionChoice("Off", "none"),
    ])):
        self.do_loop = set
        if set == "song":
            await ctx.respond("Looping...")
        elif set == "queue":
            await ctx.respond("Looping queue")
        elif set == "none":
            await ctx.respond("No more loop")

    @discord.slash_command()
    @guild_only
    async def queue(self, ctx):
        if len(queue) == 0:
            await ctx.respond("There is nothing in the queue")
            return

        embed = discord.Embed(title="Queue:")
        for video, source in queue:
            duration = f"{int(video['duration']//60):02d}:{int(video['duration']%60):02d}"
            embed.add_field(name=video["title"], value=duration, inline=False)
        await ctx.respond(embed=embed)


def make_song_embed(video):
    duration = f"{int(video['duration']//60):02d}:{int(video['duration']%60):02d}"
    embed = discord.Embed(title="Now playing:", description=video['title'])
    embed.add_field(name="Length", value=duration, inline=True)
    return embed


def search(query):
    with YoutubeDL({'format': 'bestaudio', 'noplaylist': 'True'}) as ydl:
        try:
            requests.get(query)
        except:
            info = ydl.extract_info(f"ytsearch:{query}",
                                    download=False)['entries'][0]
        else:
            info = ydl.extract_info(query, download=False)
    return (info, info['formats'][0]['url'])

def get_playlist(url):
    with YoutubeDL({'format': 'bestaudio', 'yesplaylist': 'True', 'playlist-end': '50'}) as ydl:
        info = ydl.extract_info(url, download=False)["entries"]
        return [(v, v['formats'][0]['url']) for v in info]


def setup(bot):  # this is called by Pycord to setup the cog
    bot.add_cog(Music(bot))  # add the cog to the self.bot