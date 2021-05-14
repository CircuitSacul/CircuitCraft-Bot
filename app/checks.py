from discord.ext import commands


def mc_mod():
    return commands.check_any(
        commands.has_role(842606751478972416),
        commands.is_owner()
    )
