import discord
from discord.ext import commands, tasks
from config import TEST_SERVER
import asyncio
import utils.table as table
from discord.ui import Select, View
from datetime import datetime, timedelta


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
                if member != interaction.user:
                    self.members_to_select.append(member)

        select = Select(
            placeholder="Użytkownik",
            options=[discord.SelectOption(label=member.name, value=str(member.id)) for member in self.members_to_select]
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

    @discord.ui.button(label="Zarezerwuj Stół!", style=discord.ButtonStyle.blurple, custom_id="1")
    async def book_table(self, interaction: discord.Interaction, button: discord.ui.Button):
        member = interaction.guild.get_member(interaction.user.id)
        clubMemberRoleID = 1243257402766397541 #PÓŹNIEJ ZMIENIĆ NA WŁAŚCIMY TAWERNIANY
        select_user_view = SelectUserView(interaction=interaction)
        select_game_view = SelectGameView()     
        bookingPersonID = str(interaction.user.id)
        bookedPersonID = ""
        game = ""

        await interaction.response.defer()

        try:
            if not member.get_role(clubMemberRoleID):
                await interaction.user.send("Tylko członkowie klubu mogą rezerwować stoły!")
                return 
            
            if table.book_check(bookingPersonID):
                await interaction.user.send("Zarezerwowałeś już stół!\nJeden stół na osobę lub parę!")
                return
            
            if table.in_table_check(bookingPersonID):
                await interaction.user.send("Jesteś już w zarezerwowanym stole!\nJeden stół na osobą lub parę!")
                return
            
            if table.booked_table_check() == False:
                await interaction.user.send("Rezerwujesz teraz stół")
                await interaction.user.send("Wybierz użytkownika z którym chcesz zarezerwować stół", view=select_user_view)
                await select_user_view.wait()
                bookedPersonID = str(select_user_view.bookedPerson)

                await interaction.user.send("Wybierz grę w którą chcecie grać",view=select_game_view) 
                await select_game_view.wait()   
                game = select_game_view.game

                await interaction.user.send(f"{interaction.guild.get_member(int(bookingPersonID)).display_name} zarezerwowałeś stół dla siebie i {interaction.guild.get_member(int(bookedPersonID)).display_name}\nBędziecie grać w grę {game}")
                table.book_table(bookingPersonID,bookedPersonID,game)
            else:
                await interaction.user.send("Wybacz, wszystkie stoły są już zajęte.")
        except asyncio.TimeoutError:
            await interaction.user.send("Zbyt długo czekałeś.")

    @discord.ui.button(label="Zrezygnuj ze stołu", style=discord.ButtonStyle.red, custom_id="2")
    async def cancel_table(self, interaction: discord.Interaction, button: discord.ui.Button):
        personID = interaction.user.id
        member = interaction.guild.get_member(personID)
        
        await interaction.response.defer()

        if table.cancel_table_check(str(personID)):
            await interaction.user.send(f"{member} zrezygnowałeś z rezerwacji stołu")
            table.cancel_table(str(personID))
        else:
            await interaction.user.send("Nie rezerwowałeś żadnego stołu.")
    


    
    @discord.ui.button(label="Pokaż zarezerwowane stoły", style=discord.ButtonStyle.green, custom_id="3")
    async def show_all_tables(self, interaction: discord.Interaction, button: discord.ui.Button):
        data = table.load_json()
        embed = discord.Embed(title="Status stołów", color=discord.Color.blue())
        await interaction.response.defer()

        def get_next_saturday():

            today = datetime.datetime.now()
            next_saturday = today + datetime.timedelta((5 - today.weekday() + 7) % 7)
            today = datetime.now()
            next_saturday = today + timedelta((5 - today.weekday() + 7) % 7)

            return next_saturday

        
        next_saturday = get_next_saturday()
        embed.add_field(name="Najbliższa sobota", value=next_saturday.strftime('%d.%m.%Y'), inline=False)

        for key, value in data.items():
            if not value['Osoba 1']: 
                #await interaction.user.send(f"Stół {key} jest pusty i możliwy do zarezerwowania.\n")
                embed.add_field(name=f"Stół {key}", value="Stół jest pusty i możliwy do zarezerwowania.", inline=False)
            else:
                osoba1 = interaction.guild.get_member(int(value['Osoba 1']))
                osoba2 = interaction.guild.get_member(int(value['Osoba 2'])) if value['Osoba 2'] else ""
                game = value['Gra']
                embed.add_field(name=f"Stół {key}",
                                value=f"Zarezerwowany przez: {osoba1.display_name}\n \
                                Osoba 2: {osoba2.display_name if osoba2 != "" else ""}\n \
                                Gra: {game}",
                                inline=False)
    
        await interaction.user.send(embed=embed)

class TableReservationCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.task_clear_tables.start()
        self.task_table_reminder.start()
        
    @tasks.loop(hours=24)
    async def task_clear_tables(self):
        # Pobierz aktualną datę i godzinę
        now = datetime.now()

        # Sprawdź, czy dzisiaj jest sobota
        if now.isoweekday() == 7:
            table.clear_all_tables()
            #print("To jest sobota!")
    
    @task_clear_tables.before_loop
    async def task_clear_table_before_loop(self):
        # Poczekaj aż zegar pokaże północ
        await self.bot.wait_until_ready()
        # Oblicz ile czasu pozostało do północy
        now = datetime.now()
        midnight = datetime.combine(now.date() + timedelta(days=1), datetime.min.time())
        time_until_midnight = (midnight - now).total_seconds()

        # Poczekaj do północy
        await asyncio.sleep(time_until_midnight)
    
    @tasks.loop(hours=24)  # Loop uruchamiany co 24 godziny
    async def task_table_reminder(self):
        now = datetime.datetime.now()
        if now.weekday() in [0, 2, 4]:  # Poniedziałek (0), Środa (2) i Piątek (4)
            channel = self.bot.get_channel(1202670820791427132) # TO PÓŹNIEJ ZMIENIĆ NA WŁAŚCIWY
            await channel.send("Wiadomość wysłana w poniedziałek, środę i piątek.")
    
    @task_table_reminder.before_loop
    async def task_table_reminder_before_loop(self):
        now = datetime.datetime.now()
        # Ustawianie czasu startu taska na 12:00 (południe)
        await self.wait_until_next_hour()

        target_time = datetime.time(12, 0)
        while now.time() < target_time:
            await asyncio.sleep(3600)  # Czekaj co godzinę, aż osiągniesz godzinę 12:00
            now = datetime.now()

    async def wait_until_next_hour(self):
        now = datetime.now()
        if now.minute != 0 or now.second != 0:
            # Jeśli nie jesteśmy na pełnej godzinie, poczekaj do następnej
            next_hour = now.replace(second=0, microsecond=0, minute=0, hour=(now.hour + 1) % 24)
            await asyncio.sleep((next_hour - now).total_seconds())

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
        #await ctx.send("Wyczyściłem wszystkie stoły")

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