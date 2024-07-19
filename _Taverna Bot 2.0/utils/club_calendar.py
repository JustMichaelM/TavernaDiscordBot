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

def remove_from_calendar(day: str, id: int):
    data = load_json()
    temp_list = data[day.lower()]
    index = temp_list.index(id)
    temp_list.pop(index)
    temp_list.pop(index)
    save_json(data)

def get_days_of_user(user_id: int):
    data = load_json()
    days = []
    hours = []
    for key, values in data.items():
        for value in values:
            if value == user_id:
                hour_index = values.index(value)+1
                time = values[hour_index]
                hours.append(time)
                days.append(key.capitalize())

    return days, hours 

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
