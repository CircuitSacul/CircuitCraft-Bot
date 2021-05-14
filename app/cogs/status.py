import re
from typing import TYPE_CHECKING
import discord
from discord.ext import commands, tasks

if TYPE_CHECKING:
    from app.bot import CCBot


class Status(commands.Cog):
    def __init__(self, bot: "CCBot"):
        self.bot = bot
        self.update_status.start()

    @tasks.loop(minutes=5)
    async def update_status(self):
        await self.bot.wait_until_ready()
        string = await self.bot.mc.run_command("list")
        number = re.search(
            r"There are (\d)\/\d+ players online", string
        ).group(1)
        inflection = "person" if number == 1 else "people"
        await self.bot.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name=f"{number} {inflection} play CircuitCraft"
            )
        )


def setup(bot: "CCBot"):
    bot.add_cog(Status(bot))
