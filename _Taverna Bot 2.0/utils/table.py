import json

def load_json():
    file = '_Taverna Bot 2.0/res/jsons/table.json'
    with open(file, 'r', encoding='utf-8') as data:
        dane = json.load(data)
    return dane

def save_json(data):
    file = '_Taverna Bot 2.0/res/jsons/table.json'
    with open(file, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=2)

###------FLAGS------###
def is_person_in_table_check(person_ID: int) -> bool:
    #Funkcja sprawdza czy jesteś gdzieś zapisany 
    #Zwraca True lub False
    data = load_json()
    return any(person_ID in value_dict.values() for value_dict in data.values())
      
def are_all_tables_booked_check() -> bool:
    #Funkcja sprawdzająca czy wszystkie stoły są już zabookowane.
    # Zwróci True jeśli wszystkie stoły będą zajęte
    # Zwróci False jeśli choć jeden będzie wolny.
    #Funckja musi działać przy "Zarezerwój Stół!", "Zarezerwój dla siebie" oraz contex menu
    data = load_json()
    return all(value['Osoba_1_ID']!=0 for key, value in data.items()) 

def are_all_tables_empty_check() -> bool:
    #Funkcja sprawdzająca czy wszystkie stoły są już zabookowane.
    # Zwróci True jeśli wszystkie stoły będą puste
    # Zwróci False jeśli choć jeden będzie zajęty.
    #Funckja musi działać przy "Zarezerwój Stół!", "Zarezerwój dla siebie" oraz contex menu
    data = load_json()
    return all(value['Osoba_1_ID'] == 0 for key, value in data.items()) 

def book_table_with_someone(booking_person_ID: int, partner_person_ID: int, game: str) -> None:
    #Funkcja wpisyjąca użytkownika, oponenta i grę do słownika. "Rezerwująca stół"
    data = load_json()
    for key,value in data.items():
        if value['Osoba_1_ID'] == 0:
            value['Osoba_1_ID'] = booking_person_ID
            value['Osoba_2_ID'] = partner_person_ID
            value['Gra'] = game 
            save_json(data)
            return

def book_table_for_myself(booking_person_ID: int, game: str) -> None:
    #Funkcja wpisyjąca użytkownika i grę. Służy gdy ktoś chce rezerwować stół tylko dla siebie.
    #Tutaj trzeba sprawdzić chcecka czy jest się już gdzieś zapisanym
    data = load_json()
    for key,value in data.items():
        if value['Osoba_1_ID'] == 0:
            value['Osoba_1_ID'] = booking_person_ID
            value['Osoba_2_ID'] = 0
            value['Gra'] = game 
            save_json(data)
            return

def join_table(booking_person_ID: int, person_in_table_ID: int) -> None:
    #Funkcja wpisyjąca dołączanie do innego użytkownika.
    #Nie wiem czy nie dopisać chcecka do tego czy stół jest wolny czy nie.
    #Ale to chyba nie ma znaczenia.
    data = load_json()
    for key,value in data.items():
        if value['Osoba_1_ID'] == person_in_table_ID and value['Osoba_2_ID'] == 0:
            value['Osoba_2_ID'] = booking_person_ID
            save_json(data)
            return    

def cancel_table(canceling_person_ID: int) -> None:
    #Jeśli is_person_in_table_check() zwróci True to uruchamia się ta funkcja czyszcząca słownik
    data = load_json()
    for key, value in data.items():
        if value['Osoba_1_ID'] == canceling_person_ID and value['Osoba_2_ID'] == 0:
            value['Osoba_1_ID'] = 0
            value['Gra'] = ""
            save_json(data)
            return
        
        if value['Osoba_1_ID'] == canceling_person_ID:
            value['Osoba_1_ID'] = value['Osoba_2_ID']
            value['Osoba_2_ID'] = 0
            save_json(data)
            return

        if value['Osoba_2_ID'] == canceling_person_ID:
            value['Osoba_2_ID'] = 0
            save_json(data)
            return

def return_booked_tables() -> tuple:
    #Funkcja pokazuje wszystkie zabookowane dotychczas stoły.
    #Jest potrzebna do dołączania do czyjegoś stołu.
    data = load_json()
    persons_in_tables: list[int] = []
    games_in_tables: list[str] = []

    for key,value in data.items():
        if value['Osoba_1_ID'] != 0 and value['Osoba_2_ID'] == 0:
            persons_in_tables.append(value['Osoba_1_ID'])
            games_in_tables.append(value['Gra'])
    
    return persons_in_tables, games_in_tables

def clear_all_tables() -> None:
    #Czyści wszystkie stoły
    data = load_json()
    for value in data.values():
        value.update({'Osoba_1_ID': 0, 'Osoba_2_ID': 0, 'Gra': ''})
    save_json(data)
