from functools import wraps

def guild_only(cmd):
    @wraps(cmd)
    async def wrapper(me, ctx, *args, **kwargs):
        if not ctx.guild:
            await ctx.respond("This command isn't enabled in DMs")
            return
        await cmd(me, ctx, *args, **kwargs)
    return wrapper

def check_config(type):
    def decorator(cmd):
        @wraps(cmd)
        async def wrapper(me, ctx, *args, **kwargs):
            