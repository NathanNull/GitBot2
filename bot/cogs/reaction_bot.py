import discord
import discord.utils
from discord.ext import commands, tasks
from utils import update_db, perm_mod
from configuration import requires

class ReactionRoles(commands.Cog):
	def __init__(self, bot:discord.Bot):
		self.bot = bot
		self.utils = discord.utils
		self.reaction : dict[str, dict[str, dict[str, int]]] = {}
		self.update_info = {}
		self.check_updates.start()

	@discord.slash_command(name="add-reaction-roles",description="adds reaction roles to specified message", guild_only=True, default_member_permissions=perm_mod)
	@requires.reaction_roles
	async def reactionsetup(self, ctx: discord.ApplicationContext, *, messageopt: discord.Option(str,
                    "Would you like to use a Message ID or have the bot send a message?", 
                    choices=["Send Message", "Message ID"], 
                    required=True), emoji, theroleid, channel: discord.TextChannel, textmessageorid): # type: ignore
		await ctx.defer()
		theroleid = int(theroleid)
		if messageopt == "Send Message":
			themessage = str(textmessageorid)

		elif messageopt == "Message ID":
			themessage = int(textmessageorid)

		await self.rxn_raw(theroleid, channel.id, themessage, emoji, ctx.respond)
	
	async def rxn_raw(self, rid:int, cid:int, themessage, emoji:str, send=None):
		print(rid, cid, themessage)
		print(cid)
		channel = self.bot.get_channel(cid)
		print(channel)
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
		if len(self.update_info) != 0 and self.bot.is_ready():
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

	async def save(self):
		update_db("reaction", self.reaction)

def setup(bot):
    bot.add_cog(ReactionRoles(bot))