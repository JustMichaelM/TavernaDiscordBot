import discord
from discord.ext import commands
from utils.config import TEST_SERVER
from discord.ui import View
import utils.wh40k as wh40k
import asyncio

class WH40KCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @commands.command(aliases = ['game'])
    async def new_game(self,ctx):
        deploy: str = ""
        primary: str = ""
        rule: str = ""

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
        
        await ctx.send("# Deployment")
        await ctx.send(file=discord.File(wh40k.show_deplo(deploy)))
        
        #await ctx.send("Wasz Primary Mission")
        await ctx.send(wh40k.show_primary(primary))

        await ctx.send(wh40k.show_primary(rule))

    @commands.command()
    async def random_game(self,ctx):
        deplo, primary, rule = wh40k.return_random_game()

        await ctx.send("# Deployment")
        await ctx.send(file=discord.File(deplo))
        await ctx.send(primary)
        await ctx.send(rule)

    @commands.command()
    @commands.is_owner()
    async def show_view(self, ctx):
        await ctx.message.delete()
        embed = discord.Embed(title="Wygeneruj sobie misję", description="", color=discord.Color.blue())
        view = GenerateMissionView(self.bot)
        await ctx.send(embed=embed, view=view)
    
    @commands.is_owner()
    @commands.command(aliases = ['addB'])
    async def add_battle_to_tournament(self, ctx):
        deployment, primary, mission_rule = wh40k.return_random_game()
        time = ""
        wh40k.add_battle_to_tournament(time,deployment,primary,mission_rule)
    
    @commands.command()
    async def show_tournamnet_battles(self, ctx):
        battles_list = wh40k.show_battles()

        for elem in battles_list:
            if elem.endswith('.webp'): 
                await ctx.send(file=discord.File(elem))
            elif elem != "":
                await ctx.send(elem)
            else:
                await ctx.send("Tu będzie godzinka bitwy")

async def setup(bot:commands.Bot) -> None:
    await bot.add_cog(WH40KCog(bot), guild=TEST_SERVER)

class GenerateMissionView(View):
    def __init__(self,bot):
        super().__init__(timeout=None)
        self.bot = bot
        self.members_clicked_list: list[int] = []
        self.command_list: list[str] = []

    @discord.ui.button(label="Losowa Misja", style=discord.ButtonStyle.blurple, custom_id="1", row = 0)
    async def random_mission(self, interaction: discord.Interaction, button: discord.ui.Button):
        clicking_person = interaction.user
        deplo: str = ""
        primary: str = ""
        rule: str = ""
        
        await interaction.response.defer()


        if clicking_person.id in self.members_clicked_list:
            await interaction.user.send("NO NIE KLIKAJ TYLE TYPIE!!!")
            return
        else:
            self.members_clicked_list.append(clicking_person.id)
            try:
                deplo, primary, rule = wh40k.return_random_game()
                self.command_list.append(deplo)
                self.command_list.append(primary)
                self.command_list.append(rule)
                #await interaction.user.send("# Deployment")
                #await interaction.user.send(file=discord.File(deplo))
                #await interaction.user.send(primary)
                #await interaction.user.send(rule)

            except asyncio.TimeoutError:
                self.members_clicked_list.remove(clicking_person.id)
                await interaction.user.send("Zbyt długo czekałeś.")

        for time in range(2, 0, -1):
            await asyncio.sleep(1)
            if time == 1:
                self.members_clicked_list.remove(clicking_person.id)
                for command in self.command_list:
                    #if not command.endswith('.webp'):
                        #await interaction.user.send(command)
                    #else:
                    await interaction.user.send(file=discord.File(command))
                self.members_clicked_list = []
                self.command_list = []
    

    @discord.ui.button(label="Ustawiana Misja", style=discord.ButtonStyle.blurple, custom_id="2", row = 0)
    async def custom_mission(self, interaction: discord.Interaction, button: discord.ui.Button):
        deplo = None
        primary = None
        rule = None
        clicking_person:discord.Member = interaction.user

        selectDeployView: View = Deploy()
        selectPrimaryView: View = Primary()
        selectRuleView: View = Rule()

        await interaction.response.defer()
        
        if clicking_person.id in self.members_clicked_list:
            await interaction.user.send("NO NIE KLIKAJ TYLE TYPIE!!!")
            return
        #await click_check(self.members_clicked_list,interaction)


        self.members_clicked_list.append(clicking_person.id)
        try:
            await interaction.user.send("Wybierz Deployment:",view = selectDeployView)
            await interaction.user.send("Wybierz Primary Mission:",view = selectPrimaryView)
            await interaction.user.send("Wybierz Mission Rule:",view = selectRuleView)
            await selectDeployView.wait()
            await selectPrimaryView.wait()
            await selectRuleView.wait()
            deplo = str(selectDeployView.deploy)
            primary = str(selectPrimaryView.primary)
            rule = str(selectRuleView.rule)

            #await interaction.user.send("# Deployment")
            await interaction.user.send(file=discord.File(wh40k.return_deplo(deplo)))
            await interaction.user.send(file=discord.File(wh40k.return_primary(primary)))
            await interaction.user.send(file=discord.File(wh40k.return_mission_rule(rule)))
            
            #await ctx.send("Wasz Primary Mission")
            #await interaction.user.send(wh40k.return_primary(primary))

            #await interaction.user.send(wh40k.return_primary(rule))
            self.members_clicked_list.remove(clicking_person.id)
        
        except asyncio.TimeoutError:
            self.members_clicked_list.remove(clicking_person.id)
            await interaction.user.send("Zbyt długo czekałeś.")


class Deploy(View):
    deploy = ""

    @discord.ui.select(
        placeholder="Jakie deplo wariacie?",
        options=[
            discord.SelectOption(label="SEARCH AND DESTROY",value="1"),
            discord.SelectOption(label="SWEEPING ENGAGEMENT",value="2"),
            discord.SelectOption(label="DAWN OF WAR",value="3"),
            discord.SelectOption(label="CRUCIBLE OF BATTLE",value="4"),
            discord.SelectOption(label="HAMMER AND ANVIL",value="5"),
            discord.SelectOption(label="TIPPING POINT",value="6"),
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
            discord.SelectOption(label="BURDEN OF TRUST",value="1"),
            discord.SelectOption(label="LINCHPIN",value="2"),
            discord.SelectOption(label="PURGE THE FOE",value="3"),
            discord.SelectOption(label="SCORCHED EARTH",value="4"),
            discord.SelectOption(label="SUPPLY DROP",value="5"),
            discord.SelectOption(label="TAKE AND HOLD",value="6"),
            discord.SelectOption(label="TERRAFORM",value="7"),
            discord.SelectOption(label="THE RITUAL",value="8"),
            discord.SelectOption(label="UNEXPLODED ORDNANCE",value="9")
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
            discord.SelectOption(label="ADAPT OR DIE",value="1"),
            discord.SelectOption(label="FOG OF WAR",value="2"),
            discord.SelectOption(label="HIDDEN SUPPLIES",value="3"),
            discord.SelectOption(label="INSPIRED LEADERSHIP",value="4"),
            discord.SelectOption(label="PREPARED POSITIONS",value="5"),
            discord.SelectOption(label="RAISE BANNERS",value="6"),
            discord.SelectOption(label="RAPID ESCALATION",value="7"),
            discord.SelectOption(label="SMOKE AND MIRRORS",value="8"),
            discord.SelectOption(label="STALWARTS",value="9"),
            discord.SelectOption(label="SWIFT ACTION",value="10")
        ]
    )
    async def rule_callback(self, interaction: discord.Interaction, select_item : discord.ui.Select):
        self.rule = select_item.values[0]
        self.children[0].disabled = True
        await interaction.message.edit(view = self)
        await interaction.response.defer()
        self.stop()

async def click_check(members_clicked_list: list[int], interaction: discord.Interaction) -> None:
    member: int = interaction.user.id
    if member in members_clicked_list:
        await interaction.response.send_message("Nie klikaj tyle!\nOchłoń sobie przez 5 sekund",ephemeral=True)
        for time in range(4, 0, -1):
            await asyncio.sleep(1)
            await interaction.edit_original_response(content = f"Nie klikaj tyle!\nOchłoń sobie przez {time} sekund")
        await interaction.delete_original_response() 