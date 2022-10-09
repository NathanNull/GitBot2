import discord
from discord.ext import commands, tasks
import json
from utils import basepath, guild_only
from configuration import requires
import appinput

class App(commands.Cog):
	def __init__(self, bot:discord.Bot):
		self.bot = bot
		with open(basepath+"configure_bot/application.json", "r", encoding='utf-8') as file:
			self.app : dict[str, dict[str, dict[str, int]]] = json.load(file)
			print(self.app)
    
	@discord.slash_command()
	async def testing(self, ctx:discord.ApplicationContext, question_amount: int):
		uid = ctx.author.id
		dms = self.bot.get_channel(uid)
		dmchannel = await self.bot.create_dm(ctx.author)
		modals = []
		for questions in range(question_amount):
			modals += [appinput.MyModal(next = modals[-1] if modals else None, title="title")]
		await ctx.send_modal(modals[-1])

	async def save(self):
		with open(basepath+"configure_bot/application.json", "w") as file:
			json.dump(self.reaction, file, sort_keys=False, indent=4)

def setup(bot):
    bot.add_cog(App(bot))
