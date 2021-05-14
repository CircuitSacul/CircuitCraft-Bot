import typing
import string
import random

from discord.ext import commands

if typing.TYPE_CHECKING:
    from app.bot import CCBot


def random_code() -> str:
    return "".join(random.choices(string.ascii_letters, k=5))


class Player(commands.Cog):
    def __init__(self, bot: "CCBot"):
        self.bot = bot
        self.codes: typing.Dict[int, typing.List[str, str, int]] = {}

    @commands.command(
        name="register", aliases=["link"],
        brief="Sets your minecraft username."
    )
    async def register_username(
        self, ctx: commands.Context, *, mc_username: str
    ):
        if ctx.author.id in self.codes:
            del self.codes[ctx.author.id]
        code = random_code()
        self.codes[ctx.author.id] = [mc_username, code, 0]
        result = await self.bot.rc.run_command(
            f"tell \"{mc_username}\" your code is {code}."
        )
        result = result.strip()
        if "No targets matched selector" == result:
            await ctx.send(
                "Please follow these steps:\n"
                " - Join the server at IP `144.172.75.195` and port `5555`.\n"
                f" - Run `mc!register {mc_username}` again.\n"
                " - The server will send you a code through chat.\n"
                " - Run `mc!verify <code>` to verify that you own the account."
            )
        else:
            await ctx.send(
                "I've send you a code through the Minecraft server. Run "
                "`cc!verify <code>` to verify that you own this account."
            )

    @commands.command(
        name="verify",
        brief="Verifies that you own an account."
    )
    async def verify_username(self, ctx: commands.Context, *, code: str):
        try:
            mc_username, real_code, attempts = self.codes[ctx.author.id]
        except KeyError:
            await ctx.send("Please run `cc!register <username>` first.")
            return
        if code != real_code:
            if attempts >= 3:
                await ctx.send(
                    "This is the third failed attempt. You need to stat over "
                    "by running `cc!register <username>`."
                )
                del self.codes[ctx.author.id]
                return
            self.codes[ctx.author.id][2] += 1
            await ctx.send("Wrong code!")
        else:
            await ctx.send(f"You've verified that you own {mc_username}!")
            del self.codes[ctx.author.id]


def setup(bot: "CCBot"):
    bot.add_cog(Player(bot))
