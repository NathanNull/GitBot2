from cogs.configuration_bot import check_config

#class solely for the simplification of check_config
class requires:
    level = check_config("level")
    moderation = check_config("moderation")
    music = check_config("music")
    reaction_roles = check_config("reaction_roles")

config_type = dict[str, dict[str, bool]]