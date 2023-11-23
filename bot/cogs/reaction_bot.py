import discord
import discord.utils
from discord.ext import commands, tasks
import json
from utils import basepath, perm_mod
from configuration import requires

class ReactionRoles(commands.Cog):
	def __init__(self, bot:discord.Bot):
		self.bot = bot
		self.utils = discord.utils
		with open(basepath+"configure_bot/reactions.json", "r", encoding='utf-8') as file:
			self.reaction : dict[str, dict[str, dict[str, int]]] = json.load(file)
		self.save.start()
		self.update_info = {}
		self.check_updates.start()

	@discord.slash_command(name="add-reaction-roles",description="adds reaction roles to specified message", guild_only=True, default_member_permissions=perm_mod)
	@requires.reaction_roles
	async def reactionsetup(self, ctx: discord.ApplicationContext, *, messageopt: discord.Option(str,
                    "Would you like to use a Message ID or have the bot send a message?", 
                    choices=["Send Message", "Message ID"], 
                    required=True), emoji, theroleid, channel: discord.TextChannel, textmessageorid): # can't use message as argument type, :(
		await ctx.defer()
		theroleid = int(theroleid)
		if messageopt == "Send Message":
			def check(textmessageorid):
				return message.author == ctx.author

			themessage = str(textmessageorid)

		elif messageopt == "Message ID":
			def check(textmessageorid):
				return message.author == ctx.author

			themessage = int(textmessageorid)

		await self.rxn_raw(theroleid, channel.id, themessage, emoji, ctx.respond)
	
	async def rxn_raw(self, rid:int, cid:int, themessage, emoji:str, send=None):
		channel = self.bot.get_channel(cid)
		if send is None:
			send = channel.send
		gid = str(channel.guild.id)
		if isinstance(themessage, int):
			mid = themessage
			print(mid)
		elif isinstance(themessage, str):
			message = await channel.send(themessage)
			mid = message.id
		if gid not in self.reaction:
			self.reaction[gid] = {}
		if mid not in self.reaction[gid]:
			self.reaction[gid][mid] = {}
		if emoji not in self.reaction[gid][mid]:
			message = await channel.fetch_message(mid)
			await message.add_reaction(emoji) 
			self.reaction[gid][mid][emoji] = rid

		else:
			await send('that is already a reaction role')
			return
		await self.save()
		await send(f'added {mid} to be monitered by reactions\nemoji being watched is{emoji}\nrole being given is {rid}')
	
	@tasks.loop(seconds=1)
	async def check_updates(self):
		if len(self.update_info) != 0:
			for _, val in self.update_info.items():
				await self.rxn_raw(*val)
			self.update_info = {}

	@commands.Cog.listener()
	async def on_raw_reaction_add(self, reaction: discord.Reaction):
		mid = str(reaction.message_id)
		emoji = reaction.emoji.name
		gid = str(reaction.guild_id)
		uid = reaction.user_id
		guildw = self.bot.get_guild(int(reaction.guild_id))
		membera = guildw.get_member(int(uid))
		if gid in self.reaction:
			if mid in self.reaction[gid]:
				if str(emoji) in self.reaction[gid][mid]:
					rid = self.reaction[gid][mid][emoji]
					therole = guildw.get_role(int(rid))
					await membera.add_roles(therole, reason=None, atomic=True)
			elif int(mid) in self.reaction[gid]:
				mid = int(mid)
				if emoji in self.reaction[gid][mid]:
					rid = self.reaction[gid][mid][emoji]
					therole = guildw.get_role(int(rid))
					await membera.add_roles(therole, reason=None, atomic=True)
	
	@commands.Cog.listener()
	async def on_raw_reaction_remove(self, reaction: discord.Reaction):
		mid = str(reaction.message_id)
		emoji = reaction.emoji.name
		gid = str(reaction.guild_id)
		uid = reaction.user_id
		guildw = self.bot.get_guild(int(reaction.guild_id))
		membera = guildw.get_member(int(uid))
		if gid in self.reaction:
			if mid in self.reaction[gid]:
				if str(emoji) in self.reaction[gid][mid]:
					rid = self.reaction[gid][mid][emoji]
					therole = guildw.get_role(int(rid))
					await membera.remove_roles(therole, reason=None, atomic=True)
			elif int(mid) in self.reaction[gid]:
				mid = int(mid)
				if emoji in self.reaction[gid][mid]:
					rid = self.reaction[gid][mid][emoji]
					therole = guildw.get_role(int(rid))
					await membera.remove_roles(therole, reason=None, atomic=True)
	@tasks.loop(minutes=5)
	async def save(self):
		with open(basepath+"configure_bot/reactions.json", "w") as file:
			json.dump(self.reaction, file, sort_keys=False, indent=4)

def setup(bot):
    bot.add_cog(ReactionRoles(bot))