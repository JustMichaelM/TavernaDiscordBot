import discord
from discord.ext import commands
from utils.config import TEST_SERVER, get_application_id, get_token
from cogs.reservationCog import ReservationTableView
from cogs.wh40kCog import GenerateMissionView
from cogs.calendarCog import CalendarView
import os

class TavernaBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=commands.when_mentioned_or("tav "), 
            intents=discord.Intents.all(),
            application_id = get_application_id())
    
    async def setup_hook(self):
        for filename in os.listdir('_Taverna Bot 2.0/cogs'):
            if filename.endswith('.py'):
                ext = f"cogs.{filename[:-3]}"
                await self.load_extension(ext)
                print(f'{filename[:-3]} is ready!')

        self.add_view(ReservationTableView(self))
        self.add_view(GenerateMissionView(self))
        self.add_view(CalendarView(self))

        self.tree.copy_global_to(guild=TEST_SERVER)
        synced = await self.tree.sync(guild=TEST_SERVER) 
        
        print(f"Load {str(len(synced))} slash commands on {TEST_SERVER.name}")
        #for cmd in synced:
            #print(f"Synced slash commands: {cmd}")        

    async def on_ready(self):
        print(f'{self.user} is now running')

bot = TavernaBot()
bot.run(get_token())
