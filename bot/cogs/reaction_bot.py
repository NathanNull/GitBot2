import discord
import discord.utils
from discord.ext import commands, tasks
from utils import read_db, update_db, perm_mod
from configuration import requires
import re

EMOJI_REGEX = re.compile(r"<(a?):([a-zA-Z0-9_]+):([0-9]+)>")


class EmojiValidator(commands.Converter):
	async def convert(self, ctx: commands.Context, argument: str) -> str:
		partial = discord.PartialEmoji.from_str(argument)
		if not partial.is_custom_emoji() and not partial.is_unicode_emoji():
			raise commands.BadArgument(f"Not a valid emoji! {argument}")
		return argument


colours = [
	"teal", "dark_teal", "green", "dark_green", "blue", "dark_blue", "purple",
	"dark_purple", "magenta", "dark_magenta", "gold", "orange",
		"red", "dark_grey", "light_grey", "darker_grey",
		"og_blurple", "blurple", "greyple",
		"fuchsia", "yellow", "nitro_pink"
]


class ReactionRoles(commands.Cog):
	def __init__(self, bot: discord.Bot):
		self.bot = bot
		self.utils = discord.utils
		self.reaction: dict[str, dict[str, dict[str, int]]] = {}
		self.update_info = {}
		self.check_updates.start()

	@discord.slash_command(name="create-reaction-roles", description="adds reaction roles to specified message", guild_only=True, default_member_permissions=perm_mod)
	@requires.reaction_roles
	@discord.option("role", discord.Role, description="The role to give")
	@discord.option("emoji", EmojiValidator, description="Reaction emoji")
	@discord.option("content", str, description="Message content")
	@discord.option("embedtitle", str, description="Embed title", required=False, default=None)
	@discord.option("embedcolor", str, description="Embed color", choices=colours, required=False, default="default")
	@discord.option("channel", discord.TextChannel, description="Channel to send message in", required=False, default=None)
	async def reactionsetup(self, ctx: discord.ApplicationContext, *,
							role: discord.Role, emoji: str, content: str, embedtitle: str | None, embedcolor: str, channel: discord.TextChannel | None):  # type: ignore
		await ctx.defer()
		if channel is None:
			channelid = ctx.channel.id
		else:
			channelid = channel.id
		message = "dummy message content"
		if embedtitle != None or embedcolor != "default":
			message = discord.Embed(color=getattr(
				discord.Colour, embedcolor)(), title=embedtitle, description=content)
		else:
			message = content

		await self.rxn_raw(role.id, channelid, message, emoji, ctx.respond)

	@discord.slash_command(name="add-reaction-roles", description="adds reaction roles to specified message", guild_only=True, default_member_permissions=perm_mod)
	@requires.reaction_roles
	@discord.option("role", discord.Role, description="The role to give")
	@discord.option("emoji", EmojiValidator, description="Reaction emoji")
	@discord.option("messageid", str, description="Message ID")
	@discord.option("channel", discord.TextChannel, description="Channel that message is in", required=False, default=None)
	async def reactionadd(self, ctx: discord.ApplicationContext, *,
							role: discord.Role, emoji: str, messageid: str, channel: discord.TextChannel | None):  # type: ignore
		await ctx.defer()
		if channel is None:
			channel: discord.TextChannel = ctx.channel
		channelid = channel.id

		await self.rxn_raw(role.id, channelid, int(messageid), emoji, ctx.respond)

	@reactionsetup.error
	async def reactionsetuperror(self, ctx: discord.ApplicationContext, error: discord.DiscordException):
		if isinstance(error, commands.ConversionError) and isinstance(error.original, commands.BadArgument):
			await ctx.respond(f"Invalid argument: {error.original}", ephemeral=True)
		else:
			await ctx.respond(f"Something went wrong: {error}", ephemeral=True)

	@reactionadd.error
	async def reactionadderror(self, ctx: discord.ApplicationContext, error: discord.DiscordException):
		if isinstance(error, commands.ConversionError) and isinstance(error.original, commands.BadArgument):
			await ctx.respond(f"Invalid argument: {error.original}", ephemeral=True)
		else:
			await ctx.respond(f"Something went wrong: {error}", ephemeral=True)

	async def rxn_raw(self, rid: int, cid: int, themessage: str | int | discord.Embed, emoji: str, send=None):
		print(rid, cid, themessage)
		print(cid)
		channel: discord.TextChannel = self.bot.get_channel(cid)
		print(channel)
		if send is None:
			send = channel.send
		gid = str(channel.guild.id)
		mid = ""
		if isinstance(themessage, int):
			mid = str(themessage)
			print(mid)
		elif isinstance(themessage, str):
			message = await channel.send(themessage)
			mid = str(message.id)
		elif isinstance(themessage, discord.Embed):
			message = await channel.send(embed=themessage)
			mid = str(message.id)
		if gid not in self.reaction:
			self.reaction[gid] = {}
		if mid not in self.reaction[gid]:
			self.reaction[gid][mid] = {}
		if emoji not in self.reaction[gid][mid]:
			message = await channel.fetch_message(int(mid))
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
	async def on_ready(self):
		self.reaction = read_db("reaction")

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
