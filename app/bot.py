import os

import discord
from dotenv import load_dotenv
from discord.ext import commands
from app.mc_client import McClient

load_dotenv()


EXTENSIONS = [
    "app.cogs.manage",
    "app.cogs.player",
]


class CCBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="cc!",
            case_insensitive=True
        )
        self.mc = McClient("~/circuitcraft")
        self.rc = McClient("~/registercraft")

    def run(self):
        self.mc.launch()
        for ext in EXTENSIONS:
            self.load_extension(ext)
        super().run(os.getenv("TOKEN"))

    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        if not message.guild:
            return
        if message.guild.id != 842526715476574279:
            return

        await self.process_commands(message)

    async def on_command_error(self, ctx: commands.Context, err: Exception):
        await ctx.send(err)
