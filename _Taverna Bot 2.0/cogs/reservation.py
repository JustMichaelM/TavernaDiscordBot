import discord
from discord.ext import commands, tasks
from utils.config import TEST_SERVER, get_test_server_id,get_channel_id
import asyncio
import utils.table as table
from discord.ui import Select, View
import datetime
import pytz

dt_utcnow = datetime.datetime.now(tz=pytz.utc)
dt_pl = dt_utcnow.astimezone(pytz.timezone("Europe/Warsaw"))

class TableReservationCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.task_clear_tables.start()
        self.task_table_reminder.start()
        
    @tasks.loop(time=datetime.time(hour=23, tzinfo=dt_pl.tzinfo)) #loop uruchamiany codziennie o 23
    async def task_clear_tables(self):
        day = datetime.datetime.now(tz=dt_pl.tzinfo)
        if day.isoweekday() == 7:
            table.clear_all_tables() #w niedziele o 23 czyścimy stoły.
    
    @task_clear_tables.before_loop
    async def task_clear_tables_before_loop(self):
        await self.bot.wait_until_ready()

    @tasks.loop(time=datetime.time(hour=12, tzinfo=dt_pl.tzinfo))  # Loop uruchamiany codziennie o 12
    async def task_table_reminder(self):
        guild = self.bot.get_guild(get_test_server_id())
        day = datetime.datetime.now(tz=dt_pl.tzinfo)
        if day.isoweekday() in [1, 3, 5]:  # Poniedziałek (1), Środa (3) i Piątek (5)
            channel = await guild.fetch_channel(get_channel_id("TEST_CHANNEL_ID")) #TO ZAMIENIĆ NA ODPOWIEDNI CHANNEL ID
            embed = embed_tables_info(guild)
            await channel.send(embed=embed)
    
    @task_table_reminder.before_loop
    async def task_table_reminder_before_loop(self):
        await self.bot.wait_until_ready()

    @commands.command()
    @commands.is_owner()
    async def table(self, ctx):
        await ctx.message.delete()
        embed = discord.Embed(title="Rezerwacja stołów", description="Jeśli chcesz zarezerwować stół na najbliższą sobotę.\nTYLKO DLA CZŁONKÓW KLUBU.", color=discord.Color.blue())
        view = ReservationTableView(self.bot)
        await ctx.send(embed=embed, view=view)

    @commands.command()
    @commands.is_owner()
    async def clear(self, ctx):
        await ctx.message.delete()
        table.clear_all_tables()

    @table.error
    async def error(self, ctx, error):
        if isinstance(error, commands.NotOwner):
            await ctx.message.delete()
            await ctx.author.send("Nie jesteś właścicielem bota i nie masz dostępu do komendy: table")
    
    @clear.error
    async def error(self, ctx, error):
        if isinstance(error, commands.NotOwner):
            await ctx.message.delete()
            await ctx.author.send("Nie jesteś właścicielem bota i nie masz dostępu do komendy: clear")

async def setup(bot:commands.Bot) -> None:
    await bot.add_cog(TableReservationCog(bot), guild=TEST_SERVER)


class SelectJoinUserView(View):
    def __init__(self,interaction: discord.Interaction):
        super().__init__()
        self.persons, self.games = table.show_booked()
        self.membersList = []
        self.bookedPersonID = ""

        for person in self.persons:
            self.membersList.append(interaction.guild.get_member(int(person)))

        select = Select(
            placeholder="Pozycja",
            options=[discord.SelectOption(label=f'{member.display_name} | {game}', value=str(member.id)) for member,game in zip(self.membersList, self.games)]
        )
        select.callback = self.join_user_callback  # Przypisanie funkcji callback
        self.add_item(select)

    async def join_user_callback(self, interaction: discord.Interaction):
        self.bookedPersonID = interaction.data['values'][0]
        self.children[0].disabled = True
        await interaction.message.edit(view = self)
        await interaction.response.defer()
        self.stop()

class SelectGameView(View):
    game = ""

    @discord.ui.select( 
            placeholder="Gra",
            options = [
                   discord.SelectOption(label="Wh40k", value="WH40k"),
                   discord.SelectOption(label="Age of Sigmar", value="Age of Sigmar"),
                   discord.SelectOption(label="Necromunda", value="Necromunda"),
                   discord.SelectOption(label="SWU", value="SWU"),
                   discord.SelectOption(label="Marvel", value="Marvel"),
                   discord.SelectOption(label="MTG", value="MTG")
            ]
        )
    async def game_select_callback(self, interaction: discord.Interaction, select_item : discord.ui.Select):
        self.game = select_item.values[0]
        self.children[0].disabled = True
        await interaction.message.edit(view = self)
        await interaction.response.defer()
        self.stop()

class SelectUserView(View):
    def __init__(self,interaction: discord.Interaction):
        super().__init__()
        self.membersList = interaction.guild.members
    
        self.bookedPerson = ""
        self.members_to_select = []

        for member in self.membersList:
                if member != interaction.user and not member.bot:
                    self.members_to_select.append(member)

        select = Select(
            placeholder="Użytkownik",
            options=[discord.SelectOption(label=member.display_name, value=str(member.id)) for member in self.members_to_select]
        )
        select.callback = self.user_select_callback  # Przypisanie funkcji callback
        self.add_item(select)
    
    async def user_select_callback(self, interaction: discord.Interaction):
        self.bookedPerson = interaction.data['values'][0]
        self.children[0].disabled = True
        await interaction.message.edit(view = self)
        await interaction.response.defer()
        self.stop()
    
    
class ReservationTableView(View):
    def __init__(self,bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(label="Zarezerwuj Stół!", style=discord.ButtonStyle.blurple, custom_id="1", row = 0)
    async def book_table(self, interaction: discord.Interaction, button: discord.ui.Button):
        member = interaction.guild.get_member(interaction.user.id)
        clubMemberRoleID = 1243257402766397541 #PÓŹNIEJ ZMIENIĆ NA WŁAŚCIMY TAWERNIANY
        select_user_view = SelectUserView(interaction=interaction)
        select_game_view = SelectGameView()     
        bookingPersonID = str(interaction.user.id)
        bookedPersonID = ""
        game = ""

        await interaction.response.defer()

        if await tables_chcecks(member,clubMemberRoleID,bookingPersonID,interaction) == False:
            return
        
        try:
            await interaction.user.send("Rezerwujesz teraz stół dla siebie i kogoś")
            await interaction.user.send("Wybierz użytkownika z którym chcesz zarezerwować stół", view=select_user_view)
            await select_user_view.wait()
            bookedPersonID = str(select_user_view.bookedPerson)

            await interaction.user.send("Wybierz grę w którą chcecie grać",view=select_game_view) 
            await select_game_view.wait()   
            game = select_game_view.game

            await interaction.user.send(f"{member.display_name} zarezerwowałeś stół dla siebie i {interaction.guild.get_member(int(bookedPersonID)).display_name}\nBędziecie grać w grę {game}")
            table.book_table(bookingPersonID,bookedPersonID,game)
                
        except asyncio.TimeoutError:
            await interaction.user.send("Zbyt długo czekałeś.")

    @discord.ui.button(label="Tylko Dla Siebie", style=discord.ButtonStyle.blurple, custom_id="2", row = 0)
    async def book_table_me(self, interaction: discord.Interaction, button: discord.ui.Button):
        member = interaction.guild.get_member(interaction.user.id)
        clubMemberRoleID = 1243257402766397541
        bookingPersonID = str(interaction.user.id)
        select_game_view = SelectGameView()   
        game = ""
        
        await interaction.response.defer()
        
        if await tables_chcecks(member,clubMemberRoleID,bookingPersonID,interaction) == False:
            return
        
        try:
            await interaction.user.send("Wybierz grę w którą chcesz zagrać",view=select_game_view) 
            await select_game_view.wait()   
            game = select_game_view.game

            await interaction.user.send(f"{member.display_name} zarezerwowałeś stół!\nChcesz grać w grę: {game}")
            table.book_table_myself(bookingPersonID,game)

        except asyncio.TimeoutError:
            await interaction.user.send("Zbyt długo czekałeś.")

    @discord.ui.button(label="Dołącz Do Kogoś", style=discord.ButtonStyle.blurple, custom_id="3", row = 0)
    async def join_table(self, interaction: discord.Interaction, button: discord.ui.Button):
        member = interaction.guild.get_member(interaction.user.id)
        bookingPersonID = str(member.id)
        clubMemberRoleID = 1243257402766397541
        bookedPersonID = ""
        select_join_user_view = SelectJoinUserView(interaction=interaction)

        await interaction.response.defer()

        if await tables_chcecks(member,clubMemberRoleID,bookingPersonID,interaction) == False:
            return
        
        if table.join_table_check():
            await interaction.user.send("Wszystkie stoły są puste. Zarezerwuj stół dla siebie albo z kimś")
            return

        try:
            await interaction.user.send("Rezerwujesz teraz stół dla siebie i kogoś")
            await interaction.user.send("Wybierz użytkownika z którym chcesz zarezerwować stół", view=select_join_user_view)
            await select_join_user_view.wait()
            bookedPersonID = str(select_join_user_view.bookedPersonID)
            table.join_table(bookingPersonID, bookedPersonID)
            bookedPerson = interaction.guild.get_member(int(bookedPersonID))
            await interaction.user.send(f"{member.display_name} dołączyłeś do: {bookedPerson.display_name}")

        except asyncio.TimeoutError:
            await interaction.user.send("Zbyt długo czekałeś.")

    @discord.ui.button(label="Zrezygnuj ze stołu", style=discord.ButtonStyle.red, custom_id="4", row = 1)
    async def cancel_table(self, interaction: discord.Interaction, button: discord.ui.Button):
        personID = interaction.user.id
        member = interaction.guild.get_member(personID)
        
        await interaction.response.defer()

        if table.cancel_table_check(str(personID)):
            await interaction.user.send(f"{member.display_name} zrezygnowałeś z rezerwacji stołu")
            table.cancel_table(str(personID))
        else:
            await interaction.user.send("Nie rezerwowałeś żadnego stołu.")
    

    @discord.ui.button(label="Pokaż zarezerwowane stoły", style=discord.ButtonStyle.green, custom_id="5", row = 1)
    async def show_all_tables(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        await interaction.response.defer()
        embed = embed_tables_info(guild)
        await interaction.user.send(embed=embed)


####--FUNKCJE POMOCNICZE--####


async def tables_chcecks(member: discord.Member, clubMemberRoleID: int, bookingPersonID: int, interaction: discord.Interaction) -> bool:
    if not member.get_role(clubMemberRoleID):
        await interaction.user.send("Tylko członkowie klubu mogą rezerwować stoły!")
        return False 

    if table.book_check(bookingPersonID):
        await interaction.user.send("Zarezerwowałeś już stół!\nJeden stół na osobę lub parę!")
        return False

    if table.in_table_check(bookingPersonID):
        await interaction.user.send("Jesteś już w zarezerwowanym stole!\nJeden stół na osobą lub parę!")
        return False

    if table.join_table_check():
        await interaction.user.send("Wybacz wszystkie stoły są już zajęte.")
        return False
    

def get_next_saturday() -> datetime:
    today = datetime.datetime.now(tz=dt_pl.tzinfo)

    if today.isoweekday() == 7:
        next_saturday = today + datetime.timedelta(int(today.isoweekday())-1)
    else:
        next_saturday = today + datetime.timedelta(int(6-today.isoweekday()))

    return next_saturday

def embed_tables_info(guild: discord.Guild) -> discord.Embed:
    data = table.load_json()
    embed = discord.Embed(title="Status stołów", color=discord.Color.blue())
    
    next_saturday = get_next_saturday()
    embed.add_field(name="Najbliższa sobota", value=next_saturday.strftime('%d.%m.%Y'), inline=False)

    for key, value in data.items():
        if not value['Osoba 1']: 
            #await interaction.user.send(f"Stół {key} jest pusty i możliwy do zarezerwowania.\n")
            embed.add_field(name=f"Stół {key}", value="Stół jest pusty i możliwy do zarezerwowania.", inline=False)
        else:
            osoba1 = guild.get_member(int(value['Osoba 1']))
            osoba2 = guild.get_member(int(value['Osoba 2'])) if value['Osoba 2'] else ""
            game = value['Gra']
            embed.add_field(name=f"Stół {key}",
                            value=f"Zarezerwowany przez: {osoba1.display_name}\n \
                            Osoba 2: {osoba2.display_name if osoba2 != "" else ""}\n \
                            Gra: {game}",
                            inline=False)
    return embed