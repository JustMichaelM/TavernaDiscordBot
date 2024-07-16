import json

def load_json():
    file = "_Taverna Bot 2.0/res/jsons/calendar.json"
    with open(file, 'r', encoding='utf-8') as data:
        dane = json.load(data)
    return dane

def save_json(data):
    file = '_Taverna Bot 2.0/res/jsons/calendar.json'
    with open(file, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=2)

def add_to_calendar(day: str, name: int, time: int):
    data = load_json()
    data[day].append(name)
    data[day].append(time)
    save_json(data)

def clear_calendar():
    data = load_json()
    for key, value in data.items():
        data[key] = []
    save_json(data)

def print_calendar():
    data = load_json()
    for key, value in data.items():
        print(f"{key}:  {value}")

def get_calndera():
    data = load_json()
    return data
