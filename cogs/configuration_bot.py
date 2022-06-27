import discord
from discord.ext import commands, tasks
import json
from utils import guild_only


class Configuration(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        with open("configure_bot/configuration.json", "r") as file:
            self.configuration = json.load(file)
            print(list(self.configuration.keys()))
        self.save.start()

    @discord.slash_command()
    @guild_only
    async def config_bot(self, ctx, *, setting: discord.Option(str,choices=[
        discord.OptionChoice("Level", "level"),
        discord.OptionChoice("Music", "music"),
        discord.OptionChoice("Moderation", "moderation")]), enabled: discord.Option(str,choices=[
        discord.OptionChoice("Yes", "true"),
        discord.OptionChoice("No", "false")])):
        print("currently thinking")
        gid = str(ctx.guild.id)
        print(gid)
        if gid not in self.configuration:
            self.configuration[gid] = {"moderation": "true","level": "true","music":"true"}
        mod_data = self.configuration[gid]
        if enabled == "true":
            print("worked true")
            mod_data[setting] = "true"
            await ctx.respond("Moderation is now enabled")
        elif enabled == "false":
            print("worked false")
            mod_data[setting] = "false"
            await ctx.respond("Moderation is now disabled")
        else:
            print("something failed")
            await ctx.respond("something failed")
        await self.save()

    @tasks.loop(minutes=20)
    async def save(self):
        with open("configure_bot/configuration.json", "w") as file:
            json.dump(self.configuration, file, sort_keys=True, indent=4)
        print("save")
def setup(bot):
    bot.add_cog(Configuration(bot))