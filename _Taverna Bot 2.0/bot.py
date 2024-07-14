import discord
from discord.ext import commands
from utils.config import TEST_SERVER, get_application_id, get_token
from cogs.reservationCog import ReservationTableView
from cogs.wh40kCog import GenerateMissionView

class TavernaBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=commands.when_mentioned_or("tav "), 
            intents=discord.Intents.all(),
            application_id = get_application_id())
        
        self.ext = [    
            "cogs.memeCog",
            "cogs.reservationCog",
            "cogs.wh40kCog",
            "cogs.reminderCog",
            "cogs.eventCog",
            "cogs.calendarCog"
            ]
    
    async def setup_hook(self):
        for ext in self.ext:
            await self.load_extension(ext)
            #print(f"Loaded {ext}")
        
        self.add_view(ReservationTableView(self))
        self.add_view(GenerateMissionView(self))

        self.tree.copy_global_to(guild=TEST_SERVER)
        synced = await self.tree.sync(guild=TEST_SERVER) 
        
        print(f"Load {str(len(synced))} slash commands on {TEST_SERVER.name}")
        #for cmd in synced:
            #print(f"Synced slash commands: {cmd}")        

    async def on_ready(self):
        print(f'{self.user} is now running')


bot = TavernaBot()
bot.run(get_token())