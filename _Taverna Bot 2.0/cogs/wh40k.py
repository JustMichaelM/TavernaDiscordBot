import discord
from discord.ext import commands
from utils.config import TEST_SERVER
from discord.ui import View
import utils.new_game as newGame

class Deploy(View):
    deploy = ""

    @discord.ui.select(
        placeholder="Jakie deplo wariacie?",
        options=[
            discord.SelectOption(label="SEARCH AND DESTROY",value="1"),
            discord.SelectOption(label="SWEEPING ENGAGEMENT",value="2"),
            discord.SelectOption(label="DAWN OF WAR",value="3"),
            discord.SelectOption(label="CRUCIBLE OF BATTLE",value="4"),
            discord.SelectOption(label="HAMMER AND ANVIL",value="5")
        ]
    )
    async def deplo_callback(self, interaction: discord.Interaction, select_item : discord.ui.Select):
        self.deploy = select_item.values[0]
        self.children[0].disabled = True
        await interaction.message.edit(view = self)
        await interaction.response.defer()
        self.stop()

class Primary(View):
    primary = ""
    @discord.ui.select(
        placeholder="jaki Primary mission?",
        options=[
            discord.SelectOption(label="TAKE AND HOLD",value="1"),
            discord.SelectOption(label="THE RITUAL",value="2"),
            discord.SelectOption(label="SCORCHED EARTH",value="3"),
            discord.SelectOption(label="PURGE THE FOE",value="4"),
            discord.SelectOption(label="SUPPLY DROP",value="5"),
            discord.SelectOption(label="SITES OF POWER",value="6"),
            discord.SelectOption(label="DEPLOY SERVO-SKULLS",value="7"),
            discord.SelectOption(label="VITAL GROUND",value="8")
        ]
    )
    async def primary_callback(self, interaction: discord.Interaction, select_item : discord.ui.Select):
        self.primary = select_item.values[0]
        self.children[0].disabled = True
        await interaction.message.edit(view = self)
        await interaction.response.defer()
        self.stop()

class Rule(View):
    rule = ""
    
    @discord.ui.select(
        placeholder="Jaki mission rule?",
        options=[
            discord.SelectOption(label="CHOSEN BATTLEFIELD",value="1"),
            discord.SelectOption(label="SCRAMBLER FIELDS",value="2"),
            discord.SelectOption(label="CHILLING RAIN",value="3"),
            discord.SelectOption(label="DELAYED RESERVES",value="4"),
            discord.SelectOption(label="SWEEP AND CLEAR",value="5"),
            discord.SelectOption(label="MAELSTROM OF BATTLE",value="6"),
            discord.SelectOption(label="HIDDEN SUPPLIES",value="7"),
            discord.SelectOption(label="SUPPLY LINES",value="8"),
            discord.SelectOption(label="SECRET INTEL",value="9"),
            discord.SelectOption(label="MINEFIELDS",value="10"),
            discord.SelectOption(label="TARGETS OF OPPORTUNITY",value="11"),
            discord.SelectOption(label="VOX STATIC",value="12")
        ]
    )
    async def rule_callback(self, interaction: discord.Interaction, select_item : discord.ui.Select):
        self.rule = select_item.values[0]
        self.children[0].disabled = True
        await interaction.message.edit(view = self)
        await interaction.response.defer()
        self.stop()

class WH40KCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @commands.command(aliases = ['game'])
    async def new_game(self,ctx):
        deploy = ""
        primary = ""
        rule = ""

        selectDeployView = Deploy()
        selectPrimaryView = Primary()
        selectRuleView = Rule()

        await ctx.send("Wybierz Deployment:",view = selectDeployView)
        await ctx.send("Wybierz Primary Mission:",view = selectPrimaryView)
        await ctx.send("Wybierz Mission Rule:",view = selectRuleView)
        
        await selectDeployView.wait()
        deploy = str(selectDeployView.deploy)

        await selectPrimaryView.wait()
        primary = str(selectPrimaryView.primary)

        await selectRuleView.wait()
        rule = str(selectRuleView.rule)
        
        await ctx.send("Wasz deployment")
        await ctx.send(file=discord.File(newGame.show_deplo(deploy)))
        
        await ctx.send("Wasz Primary Mission")
        await ctx.send(newGame.show_primary(primary))

        print(f"{rule}")

async def setup(bot:commands.Bot) -> None:
    await bot.add_cog(WH40KCog(bot), guild=TEST_SERVER)
