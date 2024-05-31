import json
from datetime import datetime

def load_json():
    file = 'json/calendar.json'
    with open(file, 'r', encoding='utf-8') as data:
        dane = json.load(data)
    return dane

def save_json(data):
    file = 'json/calendar.json'
    with open(file, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=2)

def print_calendar():
    data = load_json()
    for key, value in data.items():
        print(f"Nazwa: {value['Nazwa']}")
        print(f"Kiedy: {value['Data']}\n")

def clear_calendar():
    data = load_json()
    data.clear()
    save_json(data)

def add_event():
    dane = load_json()
    eventNumber = len(dane) + 1
    
    nazwa = input("Podaj nazwę wydarzenia: ")
    data = input("Podaj datę wydarzenia (w formacie DD/MM) zostanie dopisany na ten rok: ")
    
    while date_check(data) == False:
        print("Podałeś złą datę. Podaj jeszcze raz")
        data = input("Podaj datę wydarzenia (w formacie DD/MM). Zostanie dopisany na ten rok: ")
    
    newEvent = {
        f"Event {eventNumber}": 
        {
            "Nazwa": f"{nazwa}",
            "Data": f"{data}/{datetime.now().year}" 
        }
    }

    dane.update(newEvent)
    save_json(dane)
    print("Dodano nowe wydarzenie.")

def date_check(data):
    try:
        datetime.strptime(data, "%d/%m")
        return True
    except ValueError:
        return False

def delete_outdated_event():
    data = load_json()
    for key, value in list(data.items()):
        if datetime.today().date().strftime('%d/%m/%Y') == value['Data']:
            del data[key] 
    save_json(data)


            

