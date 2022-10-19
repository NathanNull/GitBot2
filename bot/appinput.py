import discord

class QuestionInput(discord.ui.Modal):
	def __init__(self, *args, cog, q_amt, **kwargs) -> None:
		self.cog = cog
		self.q_amt = q_amt
		self.curr_qs = []
		super().__init__(*args, **kwargs)
		self.add_item(discord.ui.InputText(label="Question", style=discord.InputTextStyle.long))

	async def callback(self, interaction: discord.Interaction):
		await interaction.response.send_message("Recieved.")
		self.curr_qs.append(self.children[0].value)
		if len(self.curr_qs) < self.q_amt:
			await interaction.channel.send(
				f"Click to add the next question (so far you've added {len(self.curr_qs)}/{self.q_amt})",
				view=NextButton(self)
			)
		else:
			embed = discord.Embed(title="Here are your questions")
			for i, q in enumerate(self.curr_qs):
				embed.add_field(name=f"Question {i+1}", value=q, inline=False)
			await interaction.channel.send(embed=embed)
			gid = str(interaction.guild_id)
			if gid not in self.cog.app:
				self.cog.app[gid] = {"applications": {}, "channel": -1}
			self.cog.app[gid]["applications"][self.title] = self.curr_qs
			await self.cog.save()

class AnswerInput(discord.ui.Modal):
	def __init__(self, *args, cog, questions, **kwargs) -> None:
		self.cog = cog
		self.questions = (f"{i+1}. {q}" for i, q in enumerate(questions))
		self.num_qs = len(questions)
		self.answers = []
		super().__init__(*args, **kwargs)
		self.add_item(discord.ui.InputText(label="sdsdsdsd", style=discord.InputTextStyle.long))
		self.next_q()

	def next_q(self):
		self.children[0].label = next(self.questions)

	async def callback(self, interaction: discord.Interaction):
		await interaction.response.send_message("Recieved.")
		curr_q = self.children[0]
		self.answers.append((curr_q.label, curr_q.value))
		try:
			self.next_q()
			await interaction.channel.send(
				f"Click to see the next question (so far you've answered {len(self.answers)}/{self.num_qs})",
				view=NextButton(self)
			)
		except StopIteration:
			embed = discord.Embed(title="Your answers")
			for q, a in self.answers:
				embed.add_field(name=q, value=a, inline=False)
			await self.cog.channelidstuff(interaction.guild).send(embed=embed)

class NextButton(discord.ui.View):
	def __init__(self, control_modal):
		super().__init__(timeout=None)
		self.control_modal = control_modal
	
	@discord.ui.button(label="Next")
	async def control_modal_modal(self, b:discord.ui.Button, i: discord.Interaction):
		await self.message.delete()
		await i.response.send_modal(self.control_modal)

# Broken, fix maybe
# class ReviewScreen(discord.ui.View):
# 	def __init__(self, control_modal:QuestionInput):
# 		super().__init__(timeout=None)
# 		self.control_modal = control_modal
# 		for i, q in enumerate(self.control_modal.curr_qs):
# 			self.add_item(RemoveButton(i, self, label=f"Remove Q{i+1}"))

# class RemoveButton(discord.ui.Button):
# 	def __init__(self, q_idx:int, screen:ReviewScreen, **kwargs):
# 		super().__init__(**kwargs)
# 		self.screen = screen
# 		self.q_idx = q_idx
	
# 	async def callback(self, interaction: Interaction):
# 		self.screen.remove_item(self)
# 		self.screen.control_modal.curr_qs.pop(self.q_idx)
# 		self.screen.message.embeds[0].remove_field(self.q_idx)
# 		await interaction.response.send_message("yee", ephemeral=True)