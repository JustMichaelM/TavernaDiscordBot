from typing import List
from discord.components import SelectOption
from discord.ext import commands
from discord.utils import MISSING
from utils.config import TEST_SERVER
import discord.ui
from discord import Interaction
import utils.club_calendar as calendar
import re


class CalendarCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Calendar Cog is ready!")

    @commands.command()
    async def test(self, ctx):
        #await ctx.message.delete()
        view = CalendarView(self.bot)
        await ctx.send(view=view)

async def setup(bot:commands.Bot) -> None:
    await bot.add_cog(CalendarCog(bot), guild=TEST_SERVER)


class DaySelectView(discord.ui.View):
    answer: str = ""

    @discord.ui.select(
        placeholder="Wybierz dzień...",
        options=[
            discord.SelectOption(label="Poniedziałek",value="poniedziałek"),
            discord.SelectOption(label="Wtorek",value="wtorek"),
            discord.SelectOption(label="Środa",value="środa"),
            discord.SelectOption(label="Czwartek",value="czwartek"),
            discord.SelectOption(label="Piątek",value="piątek")
        ]
    )
    async def day_select_callback(self, interaction: discord.Interaction, select_item : discord.ui.Select):
        self.answer = select_item.values[0]
        self.children[0].disabled = True
        await interaction.message.edit(view = self)
        await interaction.response.defer()
        self.stop()

class CalendarView(discord.ui.View):
    def __init__(self,bot):
        super().__init__(timeout=None)
        self.bot = bot
    
    @discord.ui.button(label="Zapisz się!", style=discord.ButtonStyle.green)
    async def sign_button(self, interaction: Interaction, button: discord.ui.Button):
        
        day_select_view: discord.ui.View = DaySelectView()
        clicking_user_id: int = interaction.user.id
        day: str = ""
        time: str = ""
        pattern = re.compile(r'^\d{4}$')

        await interaction.response.defer()

        #await interaction.channel.send(view=day_select_view)
        await interaction.response.send_message(view=day_select_view, ephemeral=True)
        await interaction.response.defer()
        await day_select_view.wait()
        day = day_select_view.answer
        print(day)
        
        await interaction.followup.send(content="Podaj godzinę o której chcesz przyjść do klubu w formacie HHMM. (np jeśli chcesz przyjść o 10:30 napisz: 1030)", ephemeral = True)

        msg = await self.bot.wait_for('message')
        
        while not pattern.match(msg.content):
            await interaction.follow.send(content="Podałeś godzinę w złym formacie. Spróbuj jeszcze raz.", ephemeral = True)
            msg = await self.bot.wait_for('message')
            
        time = msg.content
        
        calendar.add_to_calendar(day,clicking_user_id,time)

    @discord.ui.button(label="Zrezygnuj", style=discord.ButtonStyle.red)
    async def resign_button(self, interaction: Interaction, button: discord.ui.Button):
        await interaction.response.send_message(content="Wypisałęś się!")

