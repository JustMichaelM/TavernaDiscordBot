import discord
from discord.ext import commands
import config
from discord.ui import Select, View


class SelectUserView(View):
    def __init__(self,members,bot,ctx):
        super().__init__()
        self.bot = bot
        self.members = []
        
        for member in members:
            if member != ctx.author:
                self.members.append(member)
        
        self.select = Select(
            placeholder="Select a user",
            options=[discord.SelectOption(label=member.name, value=str(member.id)) for member in self.members]
        )
        self.select.callback = self.select_callback
        self.add_item(self.select)

    async def select_callback(self, interaction: discord.Interaction):
        print(interaction.data)
        selected_user_id = interaction.data['values'][0]
        selected_user_name = discord.utils.get(self.members, id=int(selected_user_id))
        await interaction.message.edit(content=f"Selected user name: {selected_user_name}\nSelected user ID: {selected_user_id}", view=None)

class UtilsCog(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
    
    @commands.command()
    async def ping(self, ctx):
        await ctx.send("Pong")
        
    @commands.command()
    async def user(self, ctx):
        guild = ctx.guild
        members = guild.members
        select_view = SelectUserView(members, self.bot, ctx)
        await ctx.author.send("Please select a user from the server:", view=select_view)
            
async def setup(bot:commands.Bot) -> None:
    await bot.add_cog(UtilsCog(bot), guild=config.TEST_SERVER)