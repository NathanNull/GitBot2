import discord
from discord.ext.commands import Bot, Cog
import discord.ui as d_ui
from discord.utils import get

queue = []

class View(d_ui.View
           ):  # Create a class called View that subclasses discord.ui.View
    def __init__(self, bot:Bot, music:Cog):
        super().__init__(timeout=None)
        self.bot = bot
        self.music = music
        
    @d_ui.button(label="Resume",
                       style=discord.ButtonStyle.primary,
                       emoji="▶")
    async def Play(self, button:d_ui.Button, interaction:discord.Interaction):
        await interaction.response.send_message("Resumed")
        voice_client: discord.VoiceClient = discord.utils.get(self.bot.voice_clients, guild=interaction.guild)
        discord.VoiceClient.resume(voice_client)

    @d_ui.button(label="Skip",
                       style=discord.ButtonStyle.primary,
                       emoji="⏭️")
    async def Skip(self, button:d_ui.Button, interaction:discord.Interaction):
        await interaction.response.send_message("Skipping")
        self.music.skipped = True
        voice_client: discord.VoiceClient = discord.utils.get(self.bot.voice_clients, guild=interaction.guild)
        discord.VoiceClient.stop(voice_client)

    @d_ui.button(label="Stop",
                       style=discord.ButtonStyle.primary,
                       emoji="⏹")
    async def Stop(self, button:d_ui.Button, interaction:discord.Interaction):
        await interaction.response.send_message("Stopping")
        queue.clear()
        self.music.skipped = True
        voice_client: discord.VoiceClient = discord.utils.get(self.bot.voice_clients, guild=interaction.guild)
        discord.VoiceClient.stop(voice_client)

    @d_ui.button(label="Pause",
                       style=discord.ButtonStyle.primary,
                       emoji="⏸")
    async def Pause(self, button:d_ui.Button, interaction:discord.Interaction):
        await interaction.response.send_message("Paused")
        voice_client: discord.VoiceClient = discord.utils.get(self.bot.voice_clients, guild=interaction.guild)
        discord.VoiceClient.pause(voice_client)

    @d_ui.button(label="Leave VC",
                       style=discord.ButtonStyle.primary,
                       emoji="👋")
    async def Leave(self, button:d_ui.Button, interaction:discord.Interaction):
        if get(self.bot.voice_clients, guild=interaction.guild) is not None:
            await get(self.bot.voice_clients, guild=interaction.guild).disconnect()
            await interaction.response.send_message('left vc')
        else:
            await interaction.response.send_message(
                "Im not in vc therefore can't leave a vc")