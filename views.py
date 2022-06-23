import discord
from discord.utils import get

queue = []

class View(discord.ui.View
           ):  # Create a class called View that subclasses discord.ui.View
    def __init__(self, bot, music):
        super().__init__(timeout=None)
        self.bot = bot
        self.music = music
        
    @discord.ui.button(label="Resume",
                       style=discord.ButtonStyle.primary,
                       emoji="▶")
    async def Play(self, button, interaction):
        await interaction.response.send_message("Resumed")
        voice_client: discord.VoiceClient = discord.utils.get(self.bot.voice_clients, guild=interaction.guild)
        discord.VoiceClient.resume(voice_client)

    @discord.ui.button(label="Skip",
                       style=discord.ButtonStyle.primary,
                       emoji="⏭️")
    async def Skip(self, button, interaction):
        await interaction.response.send_message("Skipping")
        self.music.skipped = True
        voice_client: discord.VoiceClient = discord.utils.get(self.bot.voice_clients, guild=interaction.guild)
        discord.VoiceClient.stop(voice_client)

    @discord.ui.button(label="Stop",
                       style=discord.ButtonStyle.primary,
                       emoji="⏹")
    async def Stop(self, button, interaction):
        await interaction.response.send_message("Stopping")
        queue.clear()
        self.music.skipped = True
        voice_client: discord.VoiceClient = discord.utils.get(self.bot.voice_clients, guild=interaction.guild)
        discord.VoiceClient.stop(voice_client)

    @discord.ui.button(label="Pause",
                       style=discord.ButtonStyle.primary,
                       emoji="⏸")
    async def Pause(self, button, interaction):
        await interaction.response.send_message("Paused")
        voice_client: discord.VoiceClient = discord.utils.get(self.bot.voice_clients, guild=interaction.guild)
        discord.VoiceClient.pause(voice_client)

    @discord.ui.button(label="Leave VC",
                       style=discord.ButtonStyle.primary,
                       emoji="👋")
    async def Leave(self, button, interaction):
        if get(self.bot.voice_clients, guild=interaction.guild) is not None:
            await get(self.bot.voice_clients, guild=interaction.guild).disconnect()
            await interaction.response.send_message('left vc')
        else:
            await interaction.response.send_message(
                "Im not in vc therefore can't leave a vc")