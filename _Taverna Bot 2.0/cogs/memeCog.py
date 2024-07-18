import discord
from discord.ext import commands
from discord import app_commands
from utils.config import TEST_SERVER


class MemeCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="ile", description="ile socha")
    async def ile(self, interaction: discord.Interaction):
        await interaction.response.send_message(content="https://tenor.com/bovsi.gif")

    @app_commands.command(name="more", description="more kylo")
    async def more(self, interaction: discord.Interaction):
        await interaction.response.send_message(content="https://tenor.com/bDR3P.gif")

    @app_commands.command(name="gooooood", description="good palpatine")
    async def gooooood(self, interaction: discord.Interaction):
        await interaction.response.send_message(content="https://tenor.com/ty6u.gif")   

    @app_commands.command(name="nooooooo", description="noooo vader")
    async def nooooooo(self, interaction: discord.Interaction):
        await interaction.response.send_message(content="https://tenor.com/bs5je.gif")

    @app_commands.command(name="unlimited", description="unlimited POWER!!!")
    async def unlimited(self, interaction: discord.Interaction):
        await interaction.response.send_message(content="https://tenor.com/be2Ir.gif")                   


async def setup(bot:commands.Bot) -> None:
    await bot.add_cog(MemeCog(bot), guild=TEST_SERVER)



