import discord
from discord.ext import commands, tasks
import json

class ReactionRoles(commands.Cog):
	def __init__(self, bot:discord.Bot):
		self.bot = bot
		with open("configure_bot/reactions.json", "r", encoding='utf-8') as file:
			self.reaction : dict[str, dict[str, dict[str, int]]] = json.load(file)
			print(self.reaction)
		self.save.start()

	@discord.slash_command()
	async def reactionsetup(self, ctx: discord.ApplicationContext, *, themessageid: str, emoji, theroleid: str): # can't use message as argument type, :(
		mid = themessageid
		rid = int(theroleid)
		gid = str(ctx.guild.id)
		if gid not in self.reaction:
			self.reaction[gid] = {}
		if mid not in self.reaction[gid]:
			self.reaction[gid][mid] = {}
		if emoji not in self.reaction[gid][mid]:
			await self.bot.get_message(int(themessageid)).add_reaction(emoji)
			self.reaction[gid][mid][emoji] = rid

		else:
			await ctx.respond('that is already a reaction role')
			return
		await ctx.respond(f'added {mid} to be monitered by reactions\nemoji being watched is{emoji}\nrole being given is {rid}')
		await self.save()

	@commands.Cog.listener()
	async def on_reaction_add(self, reaction: discord.Reaction, user: discord.User):
		mid = str(reaction.message.id)
		print(mid)
		emoji = reaction.emoji
		gid = str(user.guild.id)
		uid = user.id
		guildw = self.bot.get_guild(int(gid))
		membera = guildw.get_member(int(uid))
		print(gid)
		if gid in self.reaction:
			print("1 third there")
			print(f"message id is {mid}")
			if mid in self.reaction[gid]:
				print('2 thirds there')
				if str(emoji) in self.reaction[gid][mid]:
					rid = self.reaction[gid][mid][emoji]
					therole = guildw.get_role(int(rid))
					await membera.add_roles(therole, reason=None, atomic=True)
				else:
					print("No emoji")
			else:
				print("no mid")
		else:
			print("no gid")
	
	@commands.Cog.listener()
	async def on_reaction_remove(self, reaction: discord.Reaction, user: discord.User):
		mid = str(reaction.message.id)
		print(mid)
		emoji = reaction.emoji
		gid = str(user.guild.id)
		uid = user.id
		guildw = self.bot.get_guild(int(gid))
		membera = guildw.get_member(int(uid))
		print(gid)
		if gid in self.reaction:
			print("1 third there")
			print(f"message id is {mid}")
			if mid in self.reaction[gid]:
				print('2 thirds there')
				if str(emoji) in self.reaction[gid][mid]:
					rid = self.reaction[gid][mid][emoji]
					therole = guildw.get_role(int(rid))
					await membera.remove_roles(therole, reason=None, atomic=True)
				else:
					print("No emoji")
			else:
				print("no mid")
		else:
			print("no gid")

	@tasks.loop(minutes=5)
	async def save(self):
		with open("configure_bot/reactions.json", "w") as file:
			json.dump(self.reaction, file, sort_keys=False, indent=4)
		print("save reactions")

def setup(bot):
    bot.add_cog(ReactionRoles(bot))