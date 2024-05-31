import json
def load_json(file: str):
    file = file
    with open(file, 'r', encoding='utf-8') as data:
        dane = json.load(data)
    return dane

def show_deplo(key: str):
    dane = load_json('_Taverna Bot 2.0/res/jsons/deployment.json')
    return dane[key]

def show_primary(key: str):
    dane = load_json("_Taverna Bot 2.0/res/jsons/primary.json")
    return dane[key]

def show_mission_rule(key: str):
    dane = load_json('_Taverna Bot 2.0/res/jsons/rule.json')
    return dane[key]