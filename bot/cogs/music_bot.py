import discord
from discord.ext import commands
import wavelink
import typing


class Music(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        nodes = [wavelink.Node(
            identifier="Node1",
            uri="http://0.0.0.0:2333",
            password="goodpassword")
        ]
        await wavelink.Pool.connect(nodes=nodes, client=self.bot)

    @discord.slash_command()
    async def play(self, ctx: discord.ApplicationContext, *, search: str):
        vc = typing.cast(wavelink.Player, ctx.voice_client)

        if not vc:
            vc = await ctx.author.voice.channel.connect(cls=wavelink.Player)
        if ctx.author.voice.channel.id != vc.channel.id:
            return await ctx.respond("must be in same vc")

        song = await wavelink.Playable.search(search)

        if not song:
            return await ctx.respond("not found")

        await vc.play(song)
        await ctx.respond(f'now playing: {song.title}')

def setup(bot: commands.Bot):
    bot.add_cog(Music(bot))