import datetime
from discord.ext import commands, tasks
from config import TEST_SERVER
import pytz

utc = pytz.UTC

# If no tzinfo is given then UTC is assumed.

time = datetime.time(hour=14, minute=38) 


class MyCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.my_task.start()

    def cog_unload(self):
        self.my_task.cancel()

    @tasks.loop(time = time)
    async def my_task(self):
        print("My task is running!")

    @commands.command()
    async def test_ping(self, ctx):
        await ctx.send("Test ping")

async def setup(bot:commands.Bot) -> None:
    await bot.add_cog(MyCog(bot), guild=TEST_SERVER)