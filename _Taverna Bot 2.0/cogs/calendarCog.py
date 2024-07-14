from discord.ext import commands
from utils.config import TEST_SERVER


class CalendarCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Calendar Cog is ready!")

async def setup(bot:commands.Bot) -> None:
    await bot.add_cog(CalendarCog(bot), guild=TEST_SERVER)