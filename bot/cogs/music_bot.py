from sys import platform
import pycord_cogsbyserver as pcs
import discord
import yt_dlp
import requests
from discord.utils import get
import asyncio
from configuration import requires
import music_embeds

FFMPEG_OPTIONS = {
    'before_options':
    '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

js_path = "C:\\Program Files\\nodejs\\node.exe" if platform not in ["linux", "linux2"] else "/usr/local/bin/deno"
js_type = "node" if platform not in ["linux", "linux2"] else "deno"

class Music(pcs.ServerCog):
    def __init__(self, *args):
        super().__init__(*args)

        self.do_loop = "none"
        self.vol = 1.0
        self.queue = []
        self.leave_timer = None
        self.audio = None

    @pcs.ServerCog.listener()
    async def on_ready(self):
        pass

    @pcs.ServerCog.slash_command()
    @requires.music
    async def join(self, ctx: discord.ApplicationContext):
        await ctx.defer()

        # 1. SAFE CONNECTION WITH TIMEOUT
        try:
            vc = await asyncio.wait_for(ctx.author.voice.channel.connect(), timeout=10.0)
        except asyncio.TimeoutError:
            await ctx.respond("Voice connection timed out. Oracle Cloud UDP is likely blocked.", ephemeral=True)
            return
        except discord.ClientException as e:
            await ctx.respond(f"Failed to connect: {e}", ephemeral=True)
            return

        # 2. CLEAN UP ZOMBIE VC STATE
        if not vc.is_connected():
            # Remove failed client from bot's registry to prevent state confusion
            self.bot.voice_clients = [v for v in self.bot.voice_clients if v.guild != self.guild]
            await ctx.respond("Voice connection failed. Please try again.", ephemeral=True)
            return


    @pcs.ServerCog.slash_command()
    @requires.music
    async def play(self, ctx: discord.ApplicationContext, *, query: str):
        await ctx.defer()

        # 1. SAFE CONNECTION WITH TIMEOUT
        if get(self.bot.voice_clients, guild=self.guild) is not None:
            # Bot is in VC in the guild that this command was run in
            vc = get(self.bot.voice_clients, guild=self.guild)
        else:
            try:
                vc = await asyncio.wait_for(ctx.author.voice.channel.connect(), timeout=10.0)
            except asyncio.TimeoutError:
                await ctx.respond("Voice connection timed out. Oracle Cloud UDP is likely blocked.", ephemeral=True)
                return
            except discord.ClientException as e:
                await ctx.respond(f"Failed to connect: {e}", ephemeral=True)
                return

        # 2. CLEAN UP ZOMBIE VC STATE
        if not vc.is_connected():
            # Remove failed client from bot's registry to prevent state confusion
            self.bot.voice_clients = [v for v in self.bot.voice_clients if v.guild != self.guild]
            await ctx.respond("Voice connection failed. Please try again.", ephemeral=True)
            return

        # 3. REST OF YOUR LOGIC (unchanged)
        if vc.is_playing():
            v_info, url = self.search(query)
            self.queue.append((v_info, url))
            await ctx.respond("Song added to queue", ephemeral=True)
            await music_embeds.send_song_embed(v_info, self.queue, vc, ctx, self)
        else:
            if self.leave_timer is not None:
                self.leave_timer.cancel()
                self.leave_timer = None
            try:
                v_info, url = self.search(query)
                await self.raw_play(v_info, url, vc, ctx)
            except RuntimeError as e:
                await ctx.respond(str(e), ephemeral=True)
                if vc.is_connected():
                    await vc.disconnect()



    '''@pcs.ServerCog.slash_command()
    @requires.music
    async def play(self, ctx: discord.ApplicationContext, *, query):
        await ctx.defer()

        vc: discord.VoiceClient = None
        if get(self.bot.voice_clients, guild=self.guild) is not None:
            # Bot is in VC in the guild that this command was run in
            vc = get(self.bot.voice_clients, guild=self.guild)
        elif ctx.author.voice != None:
            # Bot isn't in a vc, but the command's user is, so join that one
            print("starting vc connect")
            vc = await ctx.author.voice.channel.connect()
            print(f"1: {vc.is_connected()=}")
        else:
            await ctx.respond("Neither of us are in a voice channel.", ephemeral=True)
            return

        print(f"2: {vc.is_connected()=}")
        v_info, url = self.search(query)

        while vc.is_connected() == False:
            vc = await ctx.author.voice.channel.connect()
            print(f"3: {vc.is_connected()=}")
        if vc.is_playing():
            self.queue.append((v_info, url))
            await ctx.respond("Song added to queue", ephemeral=True)
            await music_embeds.send_song_embed(v_info, self.queue, vc, ctx, self)
        else:
            if self.leave_timer != None:
                self.leave_timer.cancel()
                self.leave_timer = None
            await self.raw_play(v_info, url, vc, ctx)'''

    def adjust_volume(self, change):
        self.vol += change
        newvol = max(0, min(1, self.vol))

        if self.audio is not None:
            self.audio.volume = newvol

        if newvol != self.vol:
            self.vol = newvol
            return False
        return True

    @pcs.ServerCog.slash_command()
    @requires.music
    async def volume(self, ctx: discord.ApplicationContext, *,
                     vol: discord.Option(
                         int, min_value=0, max_value=100) = None  # type: ignore
                     ):
        if vol is None:
            await ctx.respond(f"The volume is currently {int(self.vol*100)}%", ephemeral=True)
        else:
            dv = (vol/100) - self.vol
            self.adjust_volume(dv)
            await ctx.respond(f"Volume set to {vol}%", ephemeral=True)

    async def when_done(self, ctx: discord.ApplicationContext, vc: discord.VoiceClient):
        if len(self.queue) > 0:
            v_info, url = self.queue.pop(0)
            await self.raw_play(v_info, url, vc, ctx)
        else:
            self.leave_timer = self.bot.loop.create_task(
                self.leave_if_inactive(vc))

    async def raw_play(self, v_info, url, vc: discord.VoiceClient, ctx):
        self.audio = discord.PCMVolumeTransformer(
            discord.FFmpegPCMAudio(url, **FFMPEG_OPTIONS), self.vol)
        vc.play(self.audio, after=lambda e: self.bot.loop.create_task(
            self.when_done(ctx, vc)))
        await music_embeds.send_song_embed(v_info, self.queue, vc, ctx, self)

    async def leave_if_inactive(self, vc: discord.VoiceClient):
        await asyncio.sleep(300)
        await vc.disconnect()

    def search(self, query: str) -> tuple[dict, str]:
        with yt_dlp.YoutubeDL({
            'format': 'bestaudio',  # Let yt-dlp pick the best available instead of forcing m4a
            'noplaylist': True,
            'default_search': 'auto',
            'quiet': True,
            'no_warnings': True,
            'retries': 3,
            'socket_timeout': 10,
            'http_chunk_size': 10485760,
            'merge_output_format': 'm4a',  # Forces output to m4a even if source is webm
            'keep_video': False,
        }) as ydl:
            try:
                r = requests.get(query, stream=True, timeout=3)
                r.close()
            except Exception:
                # Not a valid URL -> treat as search
                info = ydl.extract_info(f"ytsearch:{query}", download=False)[
                    'entries'][0]
            else:
                # Valid URL -> extract directly
                info = ydl.extract_info(query, download=False)

        return (info, info['url'])


def setup(bot):
    bot.add_cog(Music.make_cog(bot))
