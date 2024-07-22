from discord.ext import commands, tasks
from utils.config import TEST_SERVER, get_test_server_id, get_pl_timezone
import discord.ui
from discord import Interaction
import utils.club_calendar as calendar
import utils.banhammer as banhammer
import re
import asyncio
from datetime import datetime


class CalendarCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.task_clear_calendar.start()

    @commands.command()
    @commands.is_owner()
    async def show_buttons(self, ctx):
        await ctx.message.delete()
        view = CalendarView(self.bot)
        await ctx.send(view=view)
    
    @commands.command()
    @commands.is_owner()
    async def embed_calendar(self, ctx):
        await ctx.message.delete()
        guild = self.bot.get_guild(get_test_server_id())
        embed = embed_calendar_info(guild)
        await ctx.send(embed = embed)
    
    @commands.command()
    @commands.is_owner()
    async def clear_calendar(self, ctx):
        await ctx.message.delete()
        calendar.clear_calendar()
        await edit_msg(self.bot)
    
    @commands.command()
    @commands.is_owner()
    async def banhammer(self, ctx, user_id):
        banhammer.banhammer_callendar(user_id)
        await ctx.message.delete()
    
    @commands.command()
    @commands.is_owner()
    async def unhammer(self, ctx, user_id):
        banhammer.unhammer_callendar(user_id)
        await ctx.message.delete()

    @tasks.loop(time=datetime.time(hour=8, tzinfo=get_pl_timezone())) #loop uruchamiany codziennie o 23
    async def task_clear_calendar(self):
        pl_tzinfo = get_pl_timezone().tzinfo
        day = datetime.datetime.now(tz=pl_tzinfo)
        if day.isoweekday() == 1:
            calendar.clear_calendar() # w poniedziałek o 8 czyścimy stoły.
    
    @task_clear_calendar.before_loop
    async def task_clear_calendar_before_loop(self):
        await self.bot.wait_until_ready()
        print("Tak clear_calendar ruszył")

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

class ResignationDaySelectView(discord.ui.View):
    def __init__(self, interaction: discord.Interaction):
        super().__init__()
        self.answer: str = ""
        self.days: list[str] = []
        self.hours: list[int] = [] 
        
        self.days, self.hours = calendar.get_days_of_user(interaction.user.id)

        self.select = discord.ui.Select(
            placeholder="Dni",
            options=[discord.SelectOption(label = f'{day} {str(hour[:2]) + ":" + str(hour[2:])}', 
                                          value = day) for day, hour in zip(self.days,self.hours)])
        
        self.select.callback = self.day_select_callback
        self.add_item(self.select)
    
    async def day_select_callback(self, interaction: discord.Interaction): #select_item : discord.ui.Select):
        self.answer = self.select.values[0]
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
            await edit_msg(self.bot)
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
        banned_list: list[int] = banhammer.get_banned_calendar_list()
        resign_day_select_view = ResignationDaySelectView(interaction)

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

            await interaction.response.send_message(view=resign_day_select_view, ephemeral = True)

            await resign_day_select_view.wait()
            day = resign_day_select_view.answer

            calendar.remove_from_calendar(day=day, id = interaction.user.id)
            await edit_msg(self.bot)
            await interaction.edit_original_response(content="Gratulacje udało Ci się wypisać z dnia! Te wiadomości znikną za 5 sekund", view=None)

            for time in range(4, 0, -1):
                await asyncio.sleep(1)
                await interaction.edit_original_response(content = f"Gratulacje udało Ci się wypisać z dnia! Te wiadomości znikną za {time} sekund")
                    
            await interaction.delete_original_response()
                    
            for user in self.users_list:
                if user == interaction.user.id:
                    self.users_list.remove(user)


def embed_calendar_info(guild: discord.Guild) -> discord.Embed:
    data = calendar.load_json()
    embed = discord.Embed(title="Chętni do zagrania", color=discord.Color.blue())
    text = ""
    gracz = ""
    godzina = ""
    for key, value in data.items():
        day = str(key).capitalize()
        for v in value:
            if type(v) == int:
                member = guild.get_member(v)
                gracz = str(member.display_name)
                text = text + gracz + " "
            else:
                time = str(v[:2]) + ":" + str(v[2:])
                godzina = str(time)
                text = text + godzina + "\n"  
        embed.add_field(name=day, value=text, inline = False)
        text = ""
    return embed

async def edit_msg(bot: discord.Client) -> None:
    MESSAGE_ID = "1263819112786694287"
    CHANNEL = bot.get_channel(1263818899036831785)
    GUILD = bot.get_guild(get_test_server_id())
    msg_to_edit = await CHANNEL.fetch_message(MESSAGE_ID)
    await msg_to_edit.edit(embed=embed_calendar_info(GUILD))

