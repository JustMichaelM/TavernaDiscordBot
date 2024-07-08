import discord
import asyncio
import datetime
import pytz
import utils.table as table
from discord import app_commands
from discord.ext import commands, tasks
from utils.config import TEST_SERVER, get_test_server_id,get_channel_id
from discord.ui import Select, View

dt_utcnow = datetime.datetime.now(tz=pytz.utc)
dt_pl = dt_utcnow.astimezone(pytz.timezone("Europe/Warsaw"))

class ReminderCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.task_taxes_reminder.start()
        self.task_sponsorship_reminder.start()
        self.task_events_reminder.start()
    
    @tasks.loop(time=datetime.time(hour=12, tzinfo=dt_pl.tzinfo))  # Loop uruchamiany codziennie o 12
    #@commands.command(aliases = ['Tax'])
    async def task_taxes_reminder(self, ctx):
        guild = self.bot.get_guild(get_test_server_id()) #Podmienić na odpowiedni channel później
        announcment_channel = guild.get_channel(1247523612215218267) #podmienić na odpowiedni channel później
        tax_channel = guild.get_channel(1247523612215218267) #Podmienić na odpowiedni channel później 
        
        value1: str = f":one: Możliwość rezerwowania stołów\n\
                    :two: Zniżka u naszych sponsorów\n\
                    :three: Możliwość odbierania samodzielnie klucza do lokalu\n\
                    \n\
                    :arrow_right: Jeśli chcesz dołączyć do klubu wejdź na ten kanał {announcment_channel.mention}. Tam dowiesz się więcej."

        todayDate = datetime.datetime.now(tz=dt_pl.tzinfo)
        
        embed=discord.Embed(title="Comiesięczna przypominajka o składkach!", color=0x04ff00)
        embed.add_field(name=f"Numer konta znajdziecie tu: {tax_channel.mention}", value="", inline=False)
        embed.add_field(name="A dla zainteresowany czemu warto zostać członkiem:", value=value1, inline=False)
        
        #await ctx.send(embed=embed)

        if todayDate.day == 1:  #Pierwszy dzień miesiąca
            channel = await guild.fetch_channel(get_channel_id("TEST_CHANNEL_ID")) #TO ZAMIENIĆ NA ODPOWIEDNI CHANNEL ID
            # NA RAZIE TESTOWO JEST TAK POTEM ZMIENIĆ WSZYSTKO NA ODPOWIEDNI CHANNEL TAWERNIANY.
            # TAK SAMO JAK ZMIENIĆ ID DLA ROLI
            club_member_role_id: int = 1243257402766397541
            await channel.send(f"<@&{club_member_role_id}> Przypominajka o składkach")

            await channel.send(embed=embed)
    
    @task_taxes_reminder.before_loop
    async def task_taxes_reminder_before_loop(self):
        await self.bot.wait_until_ready()

    @tasks.loop(time=datetime.time(hour=12, tzinfo=dt_pl.tzinfo))  # Loop uruchamiany codziennie o 12
    async def task_sponsorship_reminder(self, ctx):
        #guild = self.bot.get_guild(get_test_server_id())
        embed=discord.Embed(title="Nasi cudowni sponsorzy!")
        embed.add_field(name="Matisoft Gaming Club", value="Link do sklepu", inline=False)
        day = datetime.datetime.now(tz=dt_pl.tzinfo)
        if day.isoweekday() in [2, 4]: #Wtorek i czwartek
            #channel = await guild.fetch_channel(get_channel_id("TEST_CHANNEL_ID")) #TO ZAMIENIĆ NA ODPOWIEDNI CHANNEL ID
            #NA RAZIE TESTOWO JEST TAK POTEM ZMIENIĆ WSZYSTKO NA ODPOWIEDNI CHANNEL TAWERNIANY.
            await ctx.send(embed=embed)
            
    @task_sponsorship_reminder.before_loop
    async def task_sponsorship_reminder_before_loop(self):
        await self.bot.wait_until_ready()

    @tasks.loop(time=datetime.time(hour=12, tzinfo=dt_pl.tzinfo))  # Loop uruchamiany codziennie o 12
    async def task_events_reminder(self, ctx):
        #guild = self.bot.get_guild(get_test_server_id())
        day = datetime.datetime.now(tz=dt_pl.tzinfo)
        if day.isoweekday() in [2, 4]: #Wtorek i czwartek
            #channel = await guild.fetch_channel(get_channel_id("TEST_CHANNEL_ID")) #TO ZAMIENIĆ NA ODPOWIEDNI CHANNEL ID
            # NA RAZIE TESTOWO JEST TAK POTEM ZMIENIĆ WSZYSTKO NA ODPOWIEDNI CHANNEL TAWERNIANY.
            await ctx.send("To sa zaplanowane eventy.v")
            
    @task_events_reminder.before_loop
    async def task_events_reminder_before_loop(self):
        await self.bot.wait_until_ready()


async def setup(bot:commands.Bot) -> None:
    await bot.add_cog(ReminderCog(bot), guild=TEST_SERVER)