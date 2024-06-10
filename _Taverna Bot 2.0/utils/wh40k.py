import json
import random

def load_json(file: str):
    file = file
    with open(file, 'r', encoding='utf-8') as data:
        dane = json.load(data)
    return dane

def save_json(data):
    file = '_Taverna Bot 2.0/res/jsons/tournament.json'
    with open(file, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=2)

def return_deplo(key: str) -> str:
    dane = load_json('_Taverna Bot 2.0/res/jsons/deployment.json')
    return dane[key]

def return_primary(key: str) -> str:
    dane = load_json("_Taverna Bot 2.0/res/jsons/primary.json")
    primary: str = " ".join(dane[key])
    return primary

def return_mission_rule(key: str) -> str:
    dane = load_json('_Taverna Bot 2.0/res/jsons/rule.json')
    rule: str = " ".join(dane[key])
    return rule

def return_random_game() -> tuple:
    data = load_json('_Taverna Bot 2.0/res/jsons/deployment.json')
    deplo = random.choice(list(data.values()))
    
    data = load_json("_Taverna Bot 2.0/res/jsons/primary.json")    
    primary = " ".join(random.choice(list(data.values())))

    data = load_json('_Taverna Bot 2.0/res/jsons/rule.json')
    rule = " ".join(random.choice(list(data.values()))) 
    
    return deplo, primary, rule

def add_battle_to_tournament(time: str = "", deployment: str = "", primary: str = "", mission_rule: str = "") -> None:
    dane = load_json("_Taverna Bot 2.0/res/jsons/tournament.json")
    t_rounds = dane["Roster"]
    rounds = len(t_rounds) + 1
    battle = f"Battle_{rounds}"
    t_rounds[battle] = {"Time": time, "Deployment": deployment, "Primary": primary, "Mission_Rule": mission_rule}
    save_json(dane)

def show_rounds_in_tournament() -> None:
    dane = load_json("_Taverna Bot 2.0/res/jsons/tournament.json")
    

def clear_tournament() -> None:
    dane = load_json("_Taverna Bot 2.0/res/jsons/tournament.json")
    dane["Competitors"] = []
    dane["Data"] = ""
    dane["Roster"] = {}
    save_json(dane)

def show_battles() -> list:
    dane: dict = load_json("_Taverna Bot 2.0/res/jsons/tournament.json")
    data_list: list[str] = []
    roster: dict = dane["Roster"]
    for key,value in roster.items():
        data_list.append(key)
        battle: dict = roster[key]
        for key, value in battle.items():
            data_list.append(value)

    return data_list