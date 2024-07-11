import json
from datetime import datetime

def load_json():
    file = "_Taverna Bot 2.0/res/jsons/calendar.json"
    with open(file, 'r', encoding='utf-8') as data:
        dane = json.load(data)
    return dane

def save_json(data):
    file = '_Taverna Bot 2.0/res/jsons/calendar.json'
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

def add_event(nazwa: str, termin: str) -> None:
    dane = load_json()
    event_number = len(dane) + 1

    new_event = {
        f"Event {event_number}": 
        {
            "Nazwa": f"{nazwa}",
            "Data": f"{termin}/{datetime.now().year}" 
        }
    }

    dane.update(new_event)
    save_json(dane)

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


            

