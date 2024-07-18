from discord.ext import commands
from utils.config import TEST_SERVER
import discord.ui
from discord import Interaction
import utils.club_calendar as calendar
import utils.banhammer as banhammer
import re
import asyncio


class CalendarCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    async def test(self, ctx):
        #await ctx.message.delete()
        view = CalendarView(self.bot, self.banned_list)
        await ctx.send(view=view)
    
    @commands.command()
    async def clear_calendar(self, ctx):
        calendar.clear_calendar()
    
    @commands.command()
    async def banhammer(self, ctx, user_id):
        banhammer.banhammer_callendar(user_id)
        await ctx.message.delete()
    
    @commands.command()
    async def unhammer(self, ctx, user_id):
        banhammer.unhammer_callendar(user_id)
        await ctx.message.delete()

    
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
        await interaction.response.defer()
        self.stop()

class CalendarView(discord.ui.View):
    def __init__(self,bot):
        super().__init__(timeout=None)
        self.bot = bot
        self.users_list: list[int] = []
    
    @discord.ui.button(label="Zapisz się!",custom_id="1", style=discord.ButtonStyle.green)
    async def sign_button(self, interaction: Interaction, button: discord.ui.Button):
        msg_list = []
        banned_list: list[int] = banhammer.get_banned_calendar_list()

        day_select_view: discord.ui.View = DaySelectView()
        day: str = ""
        time: str = ""
        pattern = re.compile(r'^(?:[01][0-9]|2[0-4])[0-5][0-9]$')

        if interaction.user.id in banned_list:
            await interaction.response.send_message(content="Nie możesz korzystaj z tej funkcjonalności, zgłośc się do administracji, ta wiadomość zniknie za 5 sekund.",ephemeral=True)
            
            for time in range(4, 0, -1):
                await asyncio.sleep(1)
                await interaction.edit_original_response(content = f"Nie możesz korzystaj z tej funkcjonalności, zgłośc się do administracji, ta wiadomość zniknie za {time} sekund.")
            await interaction.delete_original_response()
            return

        if interaction.user.id in self.users_list:
            await interaction.response.send_message(content="Nie klikaj tyle! Wiadomość zostanie usunięta za 5 sekund.",ephemeral=True)
            
            for time in range(4, 0, -1):
                await asyncio.sleep(1)
                await interaction.edit_original_response(content = f"Nie klikaj tyle! Wiadomość zostanie usunięta za {time} sekund.")
            await interaction.delete_original_response()
            return
        else:
            self.users_list.append(interaction.user.id)

            await interaction.response.send_message(view=day_select_view, ephemeral = True)

            await day_select_view.wait()
            day = day_select_view.answer

            await interaction.edit_original_response(content="Podaj godzinę o której chcesz przyjść do klubu w formacie HHMM. (np jeśli chcesz przyjść o 10:30 napisz: 1030)", view=None)

            def check(msg):
                return msg.author == interaction.user and msg.channel == interaction.channel

            msg = await self.bot.wait_for('message', check = check)
            msg_list.append(msg)

            while not pattern.match(msg.content):
                await interaction.edit_original_response(content="Podałeś godzinę w złym formacie. Spróbuj jeszcze raz.")
                
                msg = await self.bot.wait_for('message', check = check)
                msg_list.append(msg)

            time = msg.content

            calendar.add_to_calendar(day,interaction.user.id,time)
            await interaction.edit_original_response(content="Gratulacje udało Ci się zapisać do kalendarza! Te wiadomości znikną za 5 sekund")

            for time in range(4, 0, -1):
                await asyncio.sleep(1)
                await interaction.edit_original_response(content = f"Gratulacje udało Ci się zapisać do kalendarza! Te wiadomości znikną za {time} sekund")
                
            for msg in msg_list:
                await interaction.delete_original_response()
                await msg.delete()
                
            for user in self.users_list:
                if user == interaction.user.id:
                    self.users_list.remove(user)

    @discord.ui.button(label="Zrezygnuj",custom_id="2", style=discord.ButtonStyle.red)
    async def resign_button(self, interaction: Interaction, button: discord.ui.Button):
        await interaction.response.send_message(content="Wypisałęś się!")

