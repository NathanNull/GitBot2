from typing import Any
import discord
import os
import random
from firebase_admin import db, credentials, initialize_app

# def guild_only(cmd:Callable):
#     @wraps(cmd)
#     async def wrapper(me:Cog, ctx:discord.ApplicationContext, *args, **kwargs):
#         if not ctx.guild:
#             await ctx.respond("This command isn't enabled in DMs")
#             return
#         await cmd(me, ctx, *args, **kwargs)
#     return wrapper
perm_mod = discord.Permissions(administrator=True)

basedir = os.path.dirname(__file__)
basepath = basedir+os.sep


def make_config():
    config = {
        "level": True,
        "music": True,
        "moderation": True,
        "reaction_roles": True
    }
    return config

def init_db():
    is_prod = not ("IS_DEV" in os.environ and os.environ["IS_DEV"] == "yes")
    cred = credentials.Certificate(
        r'./surfbot-e0d83-firebase-adminsdk-dgaks-b191f56486.json' if is_prod else r'./testing-99c64-firebase-adminsdk-t7j1l-9fc9429ff6.json')
    url = "https://surfbot-e0d83-default-rtdb.firebaseio.com" if is_prod else "https://testing-99c64-default-rtdb.firebaseio.com"
    default_app = initialize_app(cred, {'databaseURL': url})


def set_hooks(bot: discord.Bot):
    init_db()
    root_ref = db.reference()

    def update_bot(gid: str, category: str, diff):
        match category:
            case 'config':
                cog = bot.get_cog("Configuration")
                if gid not in cog.configuration:
                    cog.configuration[gid] = make_config()
                ccgid: 'dict[str, str]' = cog.configuration[gid]
                ccgid["music"] = diff["music"]
                ccgid["level"] = diff["level"]
                ccgid["moderation"] = diff["moderation"]
                ccgid["reaction_roles"] = diff["reaction_roles"]
            case 'auditchannel':
                cog = bot.get_cog("AuditLogging")
                cog.auditchannel[gid] = int(diff)
            case 'appchannel':
                cog = bot.get_cog("App")
                cog.app[gid] = diff
            case 'bannedwords':
                cog = bot.get_cog("Mod")
                cog.cursewords[gid] = diff
            case 'add_reaction':
                cog = bot.get_cog("ReactionRoles")
                for (key, data) in diff.items():
                    themessage = data['message']
                    rid = int(data['role'])
                    emoji = data['emoji']
                    cid = int(data['channel'])
                    cog.update_info[random.randint(10000, 99999)] = (
                        rid, cid, themessage, emoji)
                    db.reference(f"/add_reaction/{gid}/{key}").delete()

    def callback(event: db.Event):
        path: str = event.path
        if event.data == None: # This indicates a deletion
            return
        
        print("db update")
        match path.split("/"):
            case ["", ""]:
                for (category, data) in event.data.items():
                    for (gid, info) in data.items():
                        update_bot(gid, category, info)

            case ["", category]:
                print(f"path: {path}")
                for (gid, info) in event.data.items():
                    update_bot(gid, category, info)

            case ["", category, gid, *nested_path]:
                data = db.reference(
                    f"/{category}/{gid}").get()
                update_bot(gid, category, data)

            case _:
                print(f"{event.event_type} from {event.path}")
                print("you messed up")

    root_ref.listen(callback)


def update_db(category, data):
    db.reference(f"/{category}").set(data)

def read_db(category) -> Any:
    return db.reference(f"/{category}").get()