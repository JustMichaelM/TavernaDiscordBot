import discord
import asyncio
import datetime
import pytz
import utils.table as table
import utils.calendar as calendar
from discord import app_commands
from discord.ext import commands, tasks
from utils.config import TEST_SERVER, get_test_server_id,get_channel_id
from discord.ui import Select, View

dt_utcnow = datetime.datetime.now(tz=pytz.utc)
dt_pl = dt_utcnow.astimezone(pytz.timezone("Europe/Warsaw"))

class ReminderCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.guild = self.bot.get_guild(get_test_server_id())
        self.task_taxes_reminder.start()
        self.task_sponsorship_reminder.start()
        #self.task_events_reminder.start()
    
    @tasks.loop(time=datetime.time(hour=12, tzinfo=dt_pl.tzinfo))  # Loop uruchamiany codziennie o 12
    async def task_taxes_reminder(self, ctx):
        #guild = self.bot.get_guild(get_test_server_id()) #Podmienić na serwer tawerniany
        
        announcment_channel = self.guild.get_channel(1247523612215218267) #podmienić na odpowiedni channel tawerniany
        tax_channel = self.guild.get_channel(1247523612215218267) #Podmienić na odpowiedni channel tawerniany
        
        target_channel = await self.guild.fetch_channel(get_channel_id("TEST_CHANNEL_ID")) #podmienić na channel tawerniany
        club_member_role_id: int = 1243257402766397541 #podmienić ID roli na odpowiednią rolę tawernianą

        value1: str = f":one: Możliwość rezerwowania stołów\n\
                    :two: Zniżka u naszych sponsorów\n\
                    :three: Możliwość odbierania samodzielnie klucza do lokalu\n\
                    \n\
                    :arrow_right: Jeśli chcesz dołączyć do klubu wejdź na ten kanał {announcment_channel.mention}. Tam dowiesz się więcej."

        todayDate = datetime.datetime.now(tz=dt_pl.tzinfo)
        
        embed=discord.Embed(title="Comiesięczna przypominajka o składkach!", color=0x04ff00)
        embed.add_field(name=f"Numer konta znajdziecie tu: {tax_channel.mention}", value="", inline=False)
        embed.add_field(name="A dla zainteresowany czemu warto zostać członkiem:", value=value1, inline=False)

        if todayDate.day == 1:  #Pierwszy dzień miesiąca
            await target_channel.send(f"<@&{club_member_role_id}> Przypominajka o składkach")
            await target_channel.send(embed=embed)
    
    @task_taxes_reminder.before_loop
    async def task_taxes_reminder_before_loop(self):
        await self.bot.wait_until_ready()

    #@commands.command(aliases = ['sponsor'])
    @tasks.loop(time=datetime.time(hour=12, tzinfo=dt_pl.tzinfo))  # Loop uruchamiany codziennie o 12
    async def task_sponsorship_reminder(self, ctx):
        #guild = self.bot.get_guild(get_test_server_id()) #zmienić później na serwer tawerny
        target_channel = await self.guild.fetch_channel(get_channel_id("TEST_CHANNEL_ID")) #Zmienić później na jakiś channel tawerniany

        day = datetime.datetime.now(tz=dt_pl.tzinfo)
        
        value: str = "https://mgc.com.pl/ \n\
                    Dla członków klubu jest x procentowa zniżka!"
        
        embed=discord.Embed(title = "Przypominamy o naszych cudownych sponsorach!", color = 0x04ff00)
        embed.add_field(name = "Matisoft Gaming Club", value = value , inline=False)
        
        if day.isoweekday() in [2, 4]: #Wtorek lub czwartek
            await target_channel.send(embed=embed)
            
    @task_sponsorship_reminder.before_loop
    async def task_sponsorship_reminder_before_loop(self):
        await self.bot.wait_until_ready()

    @commands.command(aliases = ['event'])
    #@tasks.loop(time=datetime.time(hour=12, tzinfo=dt_pl.tzinfo))  # Loop uruchamiany codziennie o 12
    async def task_events_reminder(self, ctx):
        data = calendar.load_json()
        target_channel = await self.guild.fetch_channel(get_channel_id("TEST_CHANNEL_ID")) #TO ZAMIENIĆ NA ODPOWIEDNI channel tawerniany
        #guild = self.bot.get_guild(get_test_server_id())
        
        embed = discord.Embed(title="Najbliższe zaplanowane wydarzenia", color=0x04ff00)

        day = datetime.datetime.now(tz=dt_pl.tzinfo)
        
        for key, value in data.items():
            if value['Nazwa']:
                nazwa = value['Nazwa']
                termin = value['Termin']
                embed.add_field(name=nazwa, value=termin)

        if day.isoweekday() in [2, 4]: #Wtorek i czwartek
            await target_channel.send(embed=embed)
            
    #@task_events_reminder.before_loop
    #async def task_events_reminder_before_loop(self):
        #await self.bot.wait_until_ready()


async def setup(bot:commands.Bot) -> None:
    await bot.add_cog(ReminderCog(bot), guild=TEST_SERVER)