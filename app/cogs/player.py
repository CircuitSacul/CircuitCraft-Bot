import typing
import string
import random

from discord.ext import commands

if typing.TYPE_CHECKING:
    from app.bot import CCBot


class AlreadyVerified(Exception):
    def __init__(self, curr_username: str):
        super().__init__(
            f"You're already registered as {curr_username}! "
            "Use cc!unregister if you want to unregister."
        )


def random_code() -> str:
    return "".join(random.choices(string.ascii_letters, k=5))


async def raise_if_verified(bot: "CCBot", user_id: int):
    rows = await bot.db.fetch("SELECT * FROM users WHERE id=?", (user_id,))
    if not rows:
        return
    sql_user = rows[0]
    if sql_user["mc_username"] is None:
        return
    raise AlreadyVerified(sql_user["mc_username"])


async def verify(bot: "CCBot", user_id: int, mc_username: str):
    rows = await bot.db.fetch("SELECT * FROM users WHERE id=?", (user_id,))
    if not rows:
        await bot.db.execute(
            "INSERT INTO users VALUES (?, ?)", (user_id, mc_username,)
        )
    else:
        sql_user = rows[0]
        if sql_user["mc_username"] is not None:
            raise AlreadyVerified(sql_user["mc_username"])
        await bot.db.execute(
            "UPDATE users SET mc_username=? WHERE id=?",
            (mc_username, user_id,)
        )
    await bot.mc.run_command(f"whitelist add \"{mc_username}\"")


async def unverify(bot: "CCBot", user_id: int):
    rows = await bot.db.fetch("SELECT * FROM users WHERE id=?", (user_id,))
    if not rows:
        return
    sql_user = rows[0]
    await bot.mc.run_command(f"whitelist remove \"{sql_user['mc_username']}\"")
    await bot.db.execute(
        "UPDATE users SET mc_username=? WHERE id=?", (None, user_id,)
    )


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
        await raise_if_verified(self.bot, ctx.author.id)
        if ctx.author.id in self.codes:
            del self.codes[ctx.author.id]
        code = random_code()
        self.codes[ctx.author.id] = [mc_username, code, 1]
        result = await self.bot.rc.run_command(
            f"tell \"{mc_username}\" your code is {code}."
        )
        result = result.strip()
        if "No targets matched selector" == result:
            await ctx.send(
                "Please follow these steps:\n"
                " - Join the server at IP `144.172.75.195` and port `5555`.\n"
                f" - Run `cc!register {mc_username}` again.\n"
                " - The server will send you a code through chat.\n"
                " - Run `cc!verify <code>` to verify that you own the account."
            )
        else:
            await ctx.send(
                "I've send you a code through the Minecraft server. Run "
                "`cc!verify <code>` to verify that you own this account."
            )

    @commands.command(
        name="unverify", aliases=["unregister"],
        help="Unregisters you and removes your MC account from the whitelist."
    )
    async def unverify_user(self, ctx: commands.Context):
        await unverify(self.bot, ctx.author.id)
        await ctx.send("You've been unverified!")

    @commands.command(
        name="verify",
        brief="Verifies that you own an account."
    )
    async def verify_username(self, ctx: commands.Context, *, code: str):
        await raise_if_verified(self.bot, ctx.author.id)
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
            await verify(self.bot, ctx.author.id, mc_username)
            await ctx.send(f"You've verified that you own {mc_username}!")
            del self.codes[ctx.author.id]


def setup(bot: "CCBot"):
    bot.add_cog(Player(bot))
