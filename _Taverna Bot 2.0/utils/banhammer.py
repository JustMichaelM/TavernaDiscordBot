import json

def load_json():
    file = '_Taverna Bot 2.0/res/jsons/banhammer.json'
    with open(file, 'r', encoding='utf-8') as data:
        dane = json.load(data)
    return dane

def save_json(data):
    file = '_Taverna Bot 2.0/res/jsons/banhammer.json'
    with open(file, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=2)

def get_banned_calendar_list():
    data = load_json()
    banned_list = data["calendar"]
    return banned_list

def banhammer_callendar(user_id: int):
    data = load_json()
    data["calendar"].append(int(user_id))
    save_json(data)

def unhammer_callendar(user_id: int):
    data = load_json()
    data["calendar"].remove(int(user_id))
    save_json(data)

def clean_banned_callendar():
    data = load_json()
    data["calendar"] = []
    save_json(data)
