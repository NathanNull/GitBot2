import discord
from discord import ui, ButtonStyle, Interaction, ApplicationContext

class MyModal(discord.ui.Modal):
	def __init__(self, *args, next:discord.ui.Modal, **kwargs) -> None:
		self.next = next
		super().__init__(*args, **kwargs)
		print('does this do things')
		self.add_item(discord.ui.InputText(label="Question", style=discord.InputTextStyle.long))

	async def callback(self, interaction: discord.Interaction):
		# embed = discord.Embed(title="Modal Results")
		# embed.add_field(name="Long Input", value=self.children[0].value)
		# await interaction.channel.send(self.children[0].value)
		await interaction.response.send_message("Recieved.")
		if self.next is not None:
			print(self.next)
			await interaction.channel.send("Click for the next set", view=NextButton(self.next))
		else:
			await interaction.channel.send("Done!")

class NextButton(discord.ui.View):
	def __init__(self, next):
		super().__init__(timeout=None)
		self.next = next
	
	@discord.ui.button(label="Next")
	async def next_modal(self, b:discord.ui.Button, i: discord.Interaction):
		await self.message.delete()
		await i.response.send_modal(self.next)