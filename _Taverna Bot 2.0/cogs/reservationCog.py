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

class TableReservationCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        '''
        self.ctx_menu = app_commands.ContextMenu(
            name='Zerezerwujcie sobie stół',
            callback=self.book_table_callback 
        )
        self.bot.tree.add_command(self.ctx_menu)
        '''
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
    async def booked(self, ctx):
        guild = ctx.guild
        await ctx.message.delete()
        embed = embed_tables_info(guild)
        await ctx.send(embed = embed)

    @commands.command()
    @commands.is_owner()
    async def clear(self, ctx):
        await ctx.message.delete()
        table.clear_all_tables()
        await edit_msg(self.bot)

    '''
    #@app_commands.context_menu(name ="Zarezerwój stół z użytkownikiem")
    async def book_table_callback(self, interaction: discord.Interaction, member: discord.Member):
        booking_person = interaction.user
        partner_person = member

        if await tables_chcecks(booking_person,interaction) == False:
            await interaction.response.send_message("Coś poszło nie tak! Nie udało Ci się zarezerwować stołu\nNie przejmuj się, ta wiadomość zniknie po 5 sekundach", ephemeral=True)
            for time in range(4, 0, -1):
                await asyncio.sleep(1)
                await interaction.edit_original_response(content = f"Coś poszło nie tak! Nie udało Ci się zarezerwować stołu\nNie przejmuj się, ta wiadomość zniknie po {time} sekundach")
            await interaction.delete_original_response()
            return
        

        table.book_table_with_someone(booking_person.id,partner_person.id,game="")
        await edit_msg(self.bot)
        
        await interaction.response.send_message("Udało Ci się zarezerwować stół!\nTą wiadomość widzisz tylko Ty.\nWiadomość zostanie usunięta za 5 sekund", ephemeral=True)
        
        for time in range(4, 0, -1):
            await asyncio.sleep(1)
            await interaction.edit_original_response(content = f"Udało Ci się zarezerwować stół!\nTą wiadomość widzisz tylko Ty.\nWiadomość zostanie usunięta za {time}")
        
        await interaction.delete_original_response()
    '''
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
    
    @booked.error
    async def error(self, ctx, error):
        if isinstance(error, commands.NotOwner):
            await ctx.message.delete()
            await ctx.author.send("Nie jesteś właścicielem bota i nie masz dostępu do komendy: clear")

async def setup(bot:commands.Bot) -> None:
    await bot.add_cog(TableReservationCog(bot), guild=TEST_SERVER)


class SelectJoinUserView(View):
    def __init__(self,interaction: discord.Interaction):
        super().__init__()
        self.guild = interaction.guild
        self.persons_in_tables: list[int] = []
        self.games_in_tables: list[str] = []
        self.members_to_select_list: list[int] = []
        
        self.persons_in_tables, self.games_in_tables = table.return_booked_tables()
        
        self.selected_member: discord.Member = None


        for person in self.persons_in_tables:
            self.members_to_select_list.append(interaction.guild.get_member(person))

        select = Select(
            placeholder="Pozycja",
            options=[discord.SelectOption(label=f'{member.display_name} | {game}', 
                                          value=str(member.id)) for member, game in zip(self.members_to_select_list, self.games_in_tables)])
        
        select.callback = self.join_user_callback 
        self.add_item(select)

    async def join_user_callback(self, interaction: discord.Interaction):
        #interaction.data['values'][0] zwraca stringa dlatego konwertujemy na inta
        self.selected_member = self.guild.get_member(int(interaction.data['values'][0]))
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
        self.guild = interaction.guild
        self.all_members_in_guild_list: list[discord.Member] = interaction.guild.members
        self.members_to_select_list: list[discord.Member] = []
    
        self.selected_member: discord.Member = None

        for member in self.all_members_in_guild_list:
                if member != interaction.user and not member.bot:
                    self.members_to_select_list.append(member)
        
        for member in self.members_to_select_list:
            if table.is_person_in_table_check(member.id):
                self.members_to_select_list.remove(member)

        select = Select(
            placeholder="Użytkownik",
            options=[discord.SelectOption(label=member.display_name, value=member.id) for member in self.members_to_select_list]
        )
        select.callback = self.user_select_callback  # Przypisanie funkcji callback
        self.add_item(select)
    
    async def user_select_callback(self, interaction: discord.Interaction):
        #interaction.data['values'][0] zwraca stringa dlatego konwertujemy na inta
        self.selected_member = self.guild.get_member(int(interaction.data['values'][0]))
        self.children[0].disabled = True
        await interaction.message.edit(view = self)
        await interaction.response.defer()
        self.stop()
    
    
class ReservationTableView(View):
    def __init__(self,bot):
        super().__init__(timeout=None)
        self.bot = bot
        self.members_clicked_list: list[int] = []

    @discord.ui.button(label="Zarezerwuj Stół!", style=discord.ButtonStyle.blurple, custom_id="1", row = 0)
    async def book_table(self, interaction: discord.Interaction, button: discord.ui.Button):
        booking_person: discord.Member = interaction.guild.get_member(interaction.user.id)
        partner_person: discord.Member = None
        game: str = ""

        select_user_view: View = SelectUserView(interaction=interaction)
        select_game_view: View = SelectGameView()     
        
        await interaction.response.defer()

        
        if await click_check(self.members_clicked_list,booking_person.id,interaction) == False:
            return

        if await tables_chcecks(booking_person,interaction) == False:
            return
        
        self.members_clicked_list.append(booking_person.id)
        try:     
            await interaction.user.send("Rezerwujesz teraz stół dla siebie i kogoś")
            await interaction.user.send("Wybierz użytkownika z którym chcesz zarezerwować stół", view=select_user_view)
            await interaction.user.send("Wybierz grę w którą chcecie grać",view=select_game_view) 
            await select_user_view.wait()
            await select_game_view.wait()   
            
            partner_person = select_user_view.selected_member
            
            game = select_game_view.game

            await interaction.user.send(f"{booking_person.display_name} zarezerwowałeś stół dla siebie i {partner_person.display_name}\nBędziecie grać w grę {game}")
            table.book_table_with_someone(booking_person.id,partner_person.id,game)   
            await edit_msg(self.bot)
            self.members_clicked_list.remove(booking_person.id)

        
        except asyncio.TimeoutError:
            await interaction.user.send("Zbyt długo czekałeś.")
            self.members_clicked_list.remove(booking_person.id)


    @discord.ui.button(label="Tylko Dla Siebie", style=discord.ButtonStyle.blurple, custom_id="2", row = 0)
    async def book_table_me(self, interaction: discord.Interaction, button: discord.ui.Button):
        booking_person: discord.Member = interaction.user
        select_game_view: View = SelectGameView()   
        game: str = ""
        
        await interaction.response.defer()
        
        if await click_check(self.members_clicked_list,booking_person.id,interaction) == False:
            return
        
        if await tables_chcecks(booking_person,interaction) == False:
            return

        self.members_clicked_list.append(booking_person.id)
        try:
            await interaction.user.send("Wybierz grę w którą chcesz zagrać",view=select_game_view) 
            await select_game_view.wait()   
            game = select_game_view.game

            await interaction.user.send(f"{booking_person.display_name} zarezerwowałeś stół!\nChcesz grać w grę: {game}")
            
            table.book_table_for_myself(booking_person.id,game)
            await edit_msg(self.bot)
            self.members_clicked_list.remove(booking_person.id)

        except asyncio.TimeoutError:
            self.members_clicked_list.remove(booking_person.id)
            await interaction.user.send("Zbyt długo czekałeś.")

    @discord.ui.button(label="Dołącz Do Kogoś", style=discord.ButtonStyle.blurple, custom_id="3", row = 0)
    async def join_table(self, interaction: discord.Interaction, button: discord.ui.Button):
        booking_person: discord.Member = interaction.user
        partner_person: discord.Member = None
        
        select_join_user_view: View = SelectJoinUserView(interaction=interaction)

        await interaction.response.defer()

        if await click_check(self.members_clicked_list,booking_person.id,interaction) == False:
            return
        
        if await tables_chcecks(booking_person,interaction) == False:
            return
        
        if table.are_all_tables_empty_check():
            await interaction.user.send("Wszystkie stoły są puste. Zarezerwuj stół dla siebie albo z kimś")
            return
    
        
        self.members_clicked_list.append(booking_person.id)
        
        try:
            await interaction.user.send("Rezerwujesz teraz stół dla siebie i kogoś")
            await interaction.user.send("Wybierz użytkownika z którym chcesz zarezerwować stół", view=select_join_user_view)
            await select_join_user_view.wait()
            
            partner_person = select_join_user_view.selected_member
            
            table.join_table(booking_person.id, partner_person.id)
            
            await interaction.user.send(f"{booking_person.display_name} dołączyłeś do: {partner_person.display_name}")
            await edit_msg(self.bot)
            self.members_clicked_list.remove(booking_person.id)
        
        except asyncio.TimeoutError:
            self.members_clicked_list.remove(booking_person.id)
            await interaction.user.send("Zbyt długo czekałeś.")

    @discord.ui.button(label="Zrezygnuj ze stołu", style=discord.ButtonStyle.red, custom_id="4", row = 1)
    async def cancel_table(self, interaction: discord.Interaction, button: discord.ui.Button):
        canceling_person = interaction.user
        
        await interaction.response.defer()

        if table.is_person_in_table_check(canceling_person.id) == False:
            await interaction.user.send("Nie rezerwowałeś żadnego stołu.")
            return

        await interaction.user.send(f"{canceling_person.display_name} zrezygnowałeś z rezerwacji stołu")
        table.cancel_table(canceling_person.id)
        await edit_msg(self.bot)
   

####--FUNKCJE POMOCNICZE--####

async def tables_chcecks(booking_person: discord.Member, interaction: discord.Interaction) -> bool:
    club_member_role_ID: int = 1243257402766397541

    if not booking_person.get_role(club_member_role_ID):
        await interaction.user.send("Tylko członkowie klubu mogą rezerwować stoły!")
        return False 

    if table.is_person_in_table_check(booking_person.id):
        await interaction.user.send("Jesteś już w zarezerwowanym stole!\nJeden stół na osobą lub parę!")
        return False

    if table.are_all_tables_booked_check():
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
        if value['Osoba_1_ID'] == 0: 
            #await interaction.user.send(f"Stół {key} jest pusty i możliwy do zarezerwowania.\n")
            embed.add_field(name=f"Stół {key}", value="Stół jest pusty i możliwy do zarezerwowania.", inline=False)
        else:
            osoba1 = guild.get_member(value['Osoba_1_ID'])
            osoba2 = guild.get_member(value['Osoba_2_ID']) if value['Osoba_2_ID'] else ""
            game = value['Gra']
            embed.add_field(name=f"Stół {key}",
                            value=f"Zarezerwowany przez: {osoba1.display_name}\n \
                            Osoba 2: {osoba2.display_name if osoba2 != "" else ""}\n \
                            Gra: {game}",
                            inline=False)
    return embed

async def click_check(members_clicked_list: list, booking_person_ID: int, interaction: discord.Interaction) -> bool:
    for member in members_clicked_list:
        if member == booking_person_ID:
            await interaction.user.send("Nacisnąłeś już guzik. Zarezerwuj stół albo poczekaj na timeout wiadomości.")
            return False
        
async def edit_msg(bot: discord.Client) -> None:
    MESSAGE_ID = 1247521053585047602
    CHANNEL = bot.get_channel(1247493839795523635)
    GUILD = bot.get_guild(get_test_server_id())
    msg_to_edit = await CHANNEL.fetch_message(MESSAGE_ID)
    await msg_to_edit.edit(embed = embed_tables_info(GUILD))