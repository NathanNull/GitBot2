import discord
from discord.ext import commands
from datetime import datetime
from math import floor
import os

class AuditLogging(commands.Cog):
	def __init__(self, bot:discord.Bot):
		self.bot = bot
	
	@commands.Cog.listener()
	async def on_ready(self):
		channelid = None
		self.channel = self.bot.get_channel(channelid)

	@commands.Cog.listener()
	async def on_member_join(self, member:discord.Member):
		age = get_relative_time(member.created_at)
		embed = discord.Embed(title="User Joined", description=(f'User Name {member.name}'))
		embed.add_field(name="Account created:", value=f"{age} ago", inline=True)
		await self.channel.send(embed=embed)

	@commands.Cog.listener()
	async def on_member_remove(self, member:discord.Member):
		age = get_relative_time(member.joined_at)
		embed = discord.Embed(title="User Left", description=(f'User Name {member.name}'))
		embed.add_field(name="User joined:", value=f"{age} ago", inline=True)
		await self.channel.send(embed=embed)
	
	@commands.Cog.listener()
	async def on_guild_channel_create(self, channel: discord.abc.GuildChannel):
		ENABLED = '✅'
		DISABLED = '❎'
		
		name = channel.name
		catname = channel.category
		perms = channel.overwrites
		embed = discord.Embed(title="Channel created", description=f"**Channel name:** {name}.\n**Channel Category:** {catname}")
		for role, overwrites in perms.items():
			if isinstance(role, discord.Role):
				writes = ""
				for perm, value in overwrites:
					if value is not None:
						writes += (f"{perm}: {ENABLED if value else DISABLED}\n")
				writes = writes[:-1].replace("_", " ").title()
				embed.add_field(name=role, value=writes, inline=True)
		await self.channel.send(embed=embed)

	@commands.Cog.listener()
	async def on_guild_channel_delete(self, channel):
		name = channel.name
		catname = channel.category
		await self.channel.send(embed=discord.Embed(title='Channel Removed',
							description=f'**Channel Name:** {name}\n**Category Name:** {catname}'))
		
	@commands.Cog.listener()
	async def on_member_ban(self, guild: discord.Guild, user: discord.Member):
		await self.channel.send(embed=discord.Embed(title='Member Banned', description=user.name))

	@commands.Cog.listener()
	async def on_member_unban(self, guild: discord.Guild, user: discord.Member):
		await self.channel.send(embed=discord.Embed(title='Member Unbanned', description=user.name))

	@commands.Cog.listener()
	async def on_message_delete(self, message: discord.Message):
		await self.channel.send(embed=discord.Embed(title="Deleted Message", description=f"{message.content}, sent by {message.author}, was deleted from {message.channel}"))

	@commands.Cog.listener()
	async def on_message_edit(self, before, after):
		if before.embeds or after.embeds:
			return
		if before.content == "" or after.content == "":
			return
		await self.channel.send(embed=discord.Embed(title="Edited Message", description=f"{before.content}\n**was edited to be**\n{after.content}"))



def get_relative_time(time:datetime):
	DIFF_COUNT = 3

	current = datetime.now()
	difference = current.timestamp() - time.timestamp()

	curr_diff = int(difference)
	diffs = []
	units = ["second", "minute", "hour", "day", "month", "year"]
	maxes = [60, 60, 24, 30.438, 12, 99999999999]

	for name, max_val in zip(units, maxes):
		diffs = [(name, floor(curr_diff%max_val))] + diffs
		curr_diff = floor(curr_diff // max_val)
	
	print(diffs)

	nonzero_index = enumerate([d for d in diffs if d[1]!=0])
	largest = [d for i,d in nonzero_index if i < DIFF_COUNT]

	return ", ".join(str(unit[1]) + " " + unit[0] + ("s" if unit[1] != 1 else "") for unit in largest)

def NoneCheck(channelid):
	if channelid == None:
		pass

def setup(bot):
	bot.add_cog(AuditLogging(bot))