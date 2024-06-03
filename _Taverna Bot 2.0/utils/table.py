import json
from datetime import datetime

def load_json():
    file = '_Taverna Bot 2.0/res/jsons/table.json'
    with open(file, 'r', encoding='utf-8') as data:
        dane = json.load(data)
    return dane

def save_json(data):
    file = '_Taverna Bot 2.0/res/jsons/table.json'
    with open(file, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=2)

def in_table_check(personID: str):
    #Funkcja sprawdza czy jesteś już gdzieś zapisany i zwraca stosowny wynik nie przepuszczając Cie dalej w
    #rezerwacji stołu.
    data = load_json()
    return any(personID in value_dict.values() for value_dict in data.values())

def book_check(bookingPersonID: str):
    #Funkcja sprawdza czy użytkownik jest już wpisany w słownik ergo zarezerwował już stół.
    data = load_json()
    areYouBookedYet = False

    for key,value in data.items():
        if value['Osoba 1'].lower() == bookingPersonID.lower():
            areYouBookedYet = True
            return areYouBookedYet
    return areYouBookedYet    

def booked_table_check():
    #Funkcja sprawdzająca czy wszystkie stoły są już zabookowane. Jeśli tak to discord wyśle stosowną wiadomość
    #do użytkownika który chce zabookować stół.
    data = load_json()
    allBooked = all(value['Osoba 1'] for key, value in data.items())
    return allBooked

def book_table(bookingPersonID: str, bookedPersonID: str, game: str):
    #Funkcja wpisyjąca użytkownika, oponenta i grę do słownika. "Rezerwująca stół"
    data = load_json()
    for key,value in data.items():
        if not value['Osoba 1']:
            value['Osoba 1'] = bookingPersonID
            value['Osoba 2'] = bookedPersonID
            value['Gra'] = game 

            save_json(data)
            return

def book_table_myself(bookingPersonID: str,game: str):
    #Funkcja wpisyjąca użytkownika i grę. Służy gdy ktoś chce rezerwować stół tylko dla siebie.
    data = load_json()
    for key,value in data.items():
        if not value['Osoba 1']:
            value['Osoba 1'] = bookingPersonID
            value['Osoba 2'] = ""
            value['Gra'] = game 

            save_json(data)
            return

def show_booked() -> list:
    data = load_json()
    persons = []
    games = []

    for key,value in data.items():
        if value['Osoba 1'] != "":
            persons.append(value['Osoba 1'])
            games.append(value['Gra'])
    
    return persons, games

def join_table(bookingPersonID: str, bookedPersonID: str):
    #Funkcja wpisyjąca dołączanie do innego użytkownika.
    data = load_json()
    for key,value in data.items():
        if value['Osoba 1'] == bookedPersonID:
            value['Osoba 2'] = bookingPersonID
            save_json(data)    
            return
        
def join_table_check() -> bool:
    #Funkcja sprawdzająca czy wszystkie stoły są już zabookowane. Jeśli tak to discord wyśle stosowną wiadomość
    #do użytkownika który chce zabookować stół.
    data = load_json()
    allJoined = all(value['Osoba 2'] for key, value in data.items())
    return allJoined

def cancel_table_check(personID: str):
    #Sprawdza czy ktoś rezerwował stół. Jeśli tak to jest w słowniku. Jesli nie to Discord wyśle wiadomość że
    #osoba nie rezerwowała żadnego stołu.
    data = load_json()
    return any(personID in value_dict.values() for value_dict in data.values())

def cancel_table(personID: str):
    #Jeśli cancle_table_chceck zwróci True to uruchamia się ta funkcja czyszcząca słownik
    data = load_json()
    for key, value in data.items():
        if value['Osoba 1'].lower() == personID.lower():
            value['Osoba 1'] = value['Osoba 2']
            value['Osoba 2'] = ""
            #value.update({'Osoba 1': '', 'Osoba 2': '', 'Gra': ''})
            save_json(data)
        else:
            value['Osoba 2'] = ""
            save_json(data)

#TO BĘDZIE TASKIEM W DISCORDZIE
def clear_all_tables():
    data = load_json()
    #if datetime.today().day == 1:
    for value in data.values():
        value.update({'Osoba 1': '', 'Osoba 2': '', 'Gra': ''})
    save_json(data)
