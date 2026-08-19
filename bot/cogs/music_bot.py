from sys import platform
import pycord_cogsbyserver as pcs
import discord
import yt_dlp
import requests
from discord.utils import get
import asyncio
from configuration import requires
import music_embeds
import random
import subprocess
import os

FFMPEG_OPTIONS = {
    'before_options':
    '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

js_path = "C:\\Program Files\\nodejs\\node.exe" if platform not in ["linux", "linux2"] else "/usr/local/bin/deno"
js_type = "node" if platform not in ["linux", "linux2"] else "deno"

if platform not in ["linux", "linux2"] :
    print('not linux')
else:
    print('is linux')

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
    async def play(self, ctx: discord.ApplicationContext, *, query: str):
        await ctx.defer()

        if not ctx.author.voice:
            await ctx.respond("You must be in a voice channel to use this command.", ephemeral=True)
            return

        # ... (Voice connection logic remains the same up until step 3) ...
        vc = get(self.bot.voice_clients, guild=self.guild)
        if not vc or not vc.is_connected():
            try:
                vc = await asyncio.wait_for(ctx.author.voice.channel.connect(), timeout=15.0)
            except asyncio.TimeoutError:
                await ctx.respond("Voice connection timed out. Check firewall/UDP settings.", ephemeral=True)
                print(vc)
                return
            except discord.ClientException as e:
                await ctx.respond(f"Failed to connect: {e}", ephemeral=True)
                print(vc)
                return
            except discord.HTTPException as e:
                await ctx.respond("Discord API error. Try again later.", ephemeral=True)
                print(vc)
                return


        if vc.is_connected():

            if vc.is_playing():
                await asyncio.sleep(random.uniform(2, 5))
                v_info, _ = self.search(query) # Only get info now
                # Handle error display here
                if v_info:
                    self.queue.append((v_info, query)) # Store the original query/info needed for search again
                    await ctx.respond("Song added to queue", ephemeral=True)
                    await music_embeds.send_song_embed(v_info, self.queue, vc, ctx, self)
            else:
                if self.leave_timer is not None:
                    self.leave_timer.cancel()
                    self.leave_timer = None
                try:
                    await asyncio.sleep(random.uniform(2, 5))
                    v_info, _ = self.search(query) # Only get info now
                    if v_info:
                        # *** NEW CORE CHANGE HERE ***
                        temp_file_path = f"/tmp/music_{self.bot.user.id}_{random.randint(1000, 9999)}.mp3"
                        success = await self.download_media(v_info, temp_file_path)
                        if success:
                            await self.raw_play(v_info, temp_file_path, vc, ctx)
                        else:
                             # Failure message was already sent in download_media
                             pass

                except Exception as e: # Catch any general search failure here
                    await ctx.respond(f"An error has occurred (Search/Playback): {e}", ephemeral=True)
                    if vc.is_connected():
                        await vc.disconnect()

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
        # When the current song finishes, we need to download and play the next one
        if len(self.queue) > 0:
            v_info, query = self.queue.pop(0) # Pop the stored info AND the query
            
            # *** NEW CORE CHANGE HERE ***
            temp_file_path = f"/tmp/music_{self.bot.user.id}_{random.randint(1000, 9999)}.mp3"
            success = await self.download_media(v_info, temp_file_path)
            if success:
                await self.raw_play(v_info, temp_file_path, vc, ctx)
        else:
            self.leave_timer = self.bot.loop.create_task(self.leave_if_inactive(vc))

    async def raw_play(self, v_info, temp_file_path, vc: discord.VoiceClient, ctx):
        """
        Plays audio from a local file path (bypassing network streaming errors).
        """
        if not os.path.exists(temp_file_path):
             await ctx.respond("Error: Temporary music file was not found.", ephemeral=True)
             return

        # Use the full local path for FFmpeg
        self.audio = discord.PCMVolumeTransformer(
            discord.FFmpegPCMAudio(temp_file_path, **FFMPEG_OPTIONS), self.vol)
        
        vc.play(self.audio, after=lambda e: self.bot.loop.create_task(
            self.when_done(ctx, vc)))
        await music_embeds.send_song_embed(v_info, self.queue, vc, ctx, self)

    async def download_media(self, info: dict, temp_file_path: str) -> bool:
        """Downloads the media using yt-dlp and saves it locally."""
        print("\n--- Initiating Local Download ---")
        try:
            # Use a temporary path format that FFmpeg likes (.mp3 or .ogg is usually safer than generic temp files)
            final_download_path = f"{temp_file_path}.mp3" 
            
            subprocess.run(
                ["yt-dlp", "-f", "bestaudio", "-o", final_download_path, info['webpage_url'] if 'webpage_url' in info else info['url'], "--cookies", "/home/opc/SurfBot/cookies.txt"],
                check=True, # Raises an error if the subprocess fails (e.g., 403)
                capture_output=False,
                text=True
            )
            print("Download successful.")
            return True
        except subprocess.CalledProcessError as e:
            # This will catch the 403 Forbidden error from yt-dlp!
            await self.bot.get_channel(1467246840134107371).send(f":x: Download failed (HTTP Error): {e}") # Replace 123 with a channel ID to notify admins
            print(f"\n--- CRITICAL DOWNLOAD FAILURE ---")
            print("The download process failed. This is likely due to network access restrictions.")
            print("Solution: Use cookies, or ensure the source website allows automated scraping.")
            return False
        except Exception as e:
            await self.bot.get_channel(1467246840134107371).send(f":x: An unknown error occurred during download: {e}") # Replace 123 with a channel ID
            print(f"\n--- CRITICAL DOWNLOAD FAILURE ---")
            return False


    async def leave_if_inactive(self, vc: discord.VoiceClient):
        await asyncio.sleep(300)
        await vc.disconnect()

    def search(self, query: str) -> tuple[dict, None]: # Note the type hint change: returns info and None
        """
        Fetches video information and performs necessary setup checks.
        It no longer returns a streaming URL.
        """
        print(js_type)
        print(js_path)
        available_formats = ['bestaudio/best', 'mp4', 'webm'] 
        USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:151.0) Gecko/20100101 Firefox/151.0'

        with yt_dlp.YoutubeDL({
            # ... (Keep all your existing options here for stability) ...
            'format': 'bestaudio[acodec=opus]/bestaudio/best',
            'remote_components': 'ejs:github',
            'noplaylist': True,
            'default_search': 'auto',
            'retries': 10,
            'socket_timeout': 15,
            'http_chunk_size': 10485760,
            'js_runtimes': {js_type: {'path': js_path}},
            'remote_components': ['ejs:github'],
            'cookiefile': '/home/opc/SurfBot/cookies.txt',
            # You can add headers here if you suspect it's a general header issue, 
            # but this is often complex to pass via yt-dlp options.
        }) as ydl:
            try:
                if query.startswith(('http://', 'https://', 'www.')):
                    info = ydl.extract_info(query, download=False)
                else:
                    # Use the correct structure for searching
                    extracted = ydl.extract_info(f"ytsearch:{query}", download=False)
                    if not extracted or 'entries' not in extracted or not extracted['entries']:
                        raise Exception("No search results found.")
                    info = extracted['entries'][0] # Get the first result
                
                # We only return info now. The URL will be handled by the downloader later.
                return info, None 

            except Exception as e:
                print(f"[yt-dlp ERROR] {type(e).__name__}: {str(e)}")
                raise Exception(f"Could not fetch song information: {str(e)}") from e
        
        # If everything fails to extract
        return (None, None)

def setup(bot):
    bot.add_cog(Music.make_cog(bot))
