import discord
from discord import ui, ButtonStyle, Interaction, ApplicationContext
from discord.utils import get

res_args = {"delete_after": 3}

class PlayView(ui.View):
    def __init__(self, bot, m_cog, vc: discord.VoiceClient):
        super().__init__(timeout=None)
        self.bot: discord.Bot = bot
        self.m_cog = m_cog
        self.vc = vc
    
    def still_in_vc(self):
        return any(vc.channel == self.vc.channel for vc in self.bot.voice_clients)
    
    @ui.button(label="Skip", style=ButtonStyle.grey)
    async def skip_song(self, button: ui.Button, interaction: Interaction):
        if not self.still_in_vc():
            await interaction.response.send_message("Not in VC", **res_args)
            return

        if self.vc is not None and self.vc.is_playing():
            self.vc.stop()
            await interaction.response.send_message("Skipped a song", **res_args)
        else:
            await interaction.response.send_message("I'm not playing anything.", **res_args)
    
    async def raw_stop(self, button: ui.Button, interaction: Interaction, silent=False):
        if self.vc.is_playing():
            self.m_cog.queue = []
            self.vc.stop()
            if not silent:
                await interaction.response.send_message("Stopped", **res_args)
        else:
            if not silent:
                await interaction.response.send_message("I'm not playing anything.", **res_args)

    @ui.button(label="Stop", style=ButtonStyle.red)
    async def stop_song(self, button: ui.Button, interaction: Interaction):
        if not self.still_in_vc():
            await interaction.response.send_message("Not in VC", **res_args)
            return

        await self.raw_stop(button, interaction)
    
    @ui.button(label="Leave VC", style=ButtonStyle.blurple)
    async def leave_vc(self, button: ui.Button, interaction: Interaction):
        if not self.still_in_vc():
            await interaction.response.send_message("Not in VC", **res_args)
            return

        await self.raw_stop(button, interaction, True)
        await self.vc.disconnect()
        await interaction.response.send_message("Left VC", **res_args)
    
    @ui.button(label="Play/Pause", style=ButtonStyle.green)
    async def play_pause(self, button:ui.Button, interaction: Interaction):
        if not self.still_in_vc():
            await interaction.response.send_message("Not in VC", **res_args)
            return

        if self.vc.is_paused():
            self.vc.resume()
            await interaction.response.send_message("Resumed", **res_args)
        elif self.vc.is_playing():
            self.vc.pause()
            await interaction.response.send_message("Paused", **res_args)
        else:
            await interaction.response.send_message("Nothing playing or paused", **res_args)

    @ui.button(label="Volume Down", style=ButtonStyle.gray)
    async def vol_down(self, button:ui.Button, interaction: Interaction):
        valid = self.m_cog.adjust_volume(-0.05)
        if valid:
            await interaction.response.send_message(f"Volume decreased to {round(self.m_cog.vol*100)}%", **res_args)
        else:
            await interaction.response.send_message("Volume is already 0%", **res_args)

    @ui.button(label="Volume Up", style=ButtonStyle.gray)
    async def vol_up(self, button:ui.Button, interaction: Interaction):
        valid = self.m_cog.adjust_volume(+0.05)
        if valid:
            await interaction.response.send_message(f"Volume increased to {round(self.m_cog.vol*100)}%", **res_args)
        else:
            await interaction.response.send_message("Volume is already 100%", **res_args)

async def send_song_embed(song_info: dict, queue:list, vc:discord.VoiceClient, ctx: ApplicationContext, this):
    title = "Now Playing" if not queue else f"Added to Queue at Position #{len(queue)+1}"
    e = discord.Embed(color=discord.Colour(0x00ffff), title=title)
    secs = song_info['duration'] % 60
    mins = song_info['duration'] // 60
    time = f"{mins:02d}:{secs:02d}"
    e.add_field(name=song_info['title'], value=f"Duration: {time}")
    await ctx.respond(embed=e, view=PlayView(ctx.bot, this, vc))