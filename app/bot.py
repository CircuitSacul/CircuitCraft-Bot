from app.database import Database
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
        self.rc = McClient("~/verifycraft")
        self.db = Database()

    def run(self):
        self.mc.launch()
        self.rc.launch()
        for ext in EXTENSIONS:
            self.load_extension(ext)
        super().run(os.getenv("TOKEN"))

    async def start(self, *args, **kwargs):
        await self.db.init()
        await super().start(*args, **kwargs)

    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        if not message.guild:
            return
        if message.guild.id != 842526715476574279:
            return

        await self.process_commands(message)

    async def on_command_error(self, ctx: commands.Context, err: Exception):
        try:
            err = err.original
        except KeyError:
            pass
        await ctx.send(err)
