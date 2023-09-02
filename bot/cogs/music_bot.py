import pycord_cogsbyserver as pcs
import discord, yt_dlp, requests, json
from discord.utils import get
import asyncio
import music_embeds

FFMPEG_OPTIONS = {
    'before_options':
    '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

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
    async def play(self, ctx: discord.ApplicationContext, *, query):
        await ctx.defer()

        vc:discord.VoiceClient = None
        if get(self.bot.voice_clients, guild=self.guild) is not None:
            # Bot is in VC in the guild that this command was run in
            vc = get(self.bot.voice_clients, guild=self.guild)
        elif ctx.author.voice != None:
            # Bot isn't in a vc, but the command's user is, so join that one
            vc = await ctx.author.voice.channel.connect()
        else:
            await ctx.respond("Neither of us are in a voice channel.")
            return
        '''try:
            print(ctx.author.voice.channel)
            vc = await ctx.author.voice.channel.connect()
        except:
            await ctx.send('already in vc')'''
        
        v_info, url = self.search(query)

        if vc.is_playing():
            self.queue.append((v_info, url))
            await ctx.respond("Song added to queue")
            await music_embeds.send_song_embed(v_info, self.queue, vc, ctx, self)
        else:
            if self.leave_timer != None:
                self.leave_timer.cancel()
                self.leave_timer = None
            await self.raw_play(v_info, url, vc, ctx)
    
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
    async def volume(self, ctx: discord.ApplicationContext, *, vol:discord.Option(int, min_value=0, max_value=100)=None):
        if vol is None:
            await ctx.respond(f"The volume is currently {int(self.vol*100)}%")
        else:
            dv = (vol/100) - self.vol
            self.adjust_volume(dv)
            await ctx.respond(f"Volume set to {vol}%", ephemeral=True)
    
    async def when_done(self, ctx: discord.ApplicationContext, vc: discord.VoiceClient):
        if len(self.queue) > 0:
            v_info, url = self.queue.pop(0)
            await self.raw_play(v_info, url, vc, ctx)
        else:
            self.leave_timer = self.bot.loop.create_task(self.leave_if_inactive(vc))
    
    async def raw_play(self, v_info, url, vc: discord.VoiceClient, ctx):
        self.audio = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(url, **FFMPEG_OPTIONS), self.vol)
        vc.play(self.audio, after=lambda e: self.bot.loop.create_task(self.when_done(ctx, vc)))
        await music_embeds.send_song_embed(v_info, self.queue, vc, ctx, self)
    
    async def leave_if_inactive(self, vc: discord.VoiceClient):
        await asyncio.sleep(300)
        await vc.disconnect()
        
    def search(self, query:str) -> tuple[dict, str]:
        with yt_dlp.YoutubeDL({'format': 'm4a/bestaudio/best', 'noplaylist': 'True'}) as ydl:
            try:
                requests.get(query)
            except:
                info = ydl.extract_info(
                    f"ytsearch:{query}", download=False
                )['entries'][0]
            else:
                info = ydl.extract_info(query, download=False)
        return (info, info['url'])

def setup(bot):
    bot.add_cog(Music.make_cog(bot))
