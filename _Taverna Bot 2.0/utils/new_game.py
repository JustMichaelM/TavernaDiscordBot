import json
import random

def load_json(file: str):
    file = file
    with open(file, 'r', encoding='utf-8') as data:
        dane = json.load(data)
    return dane

def return_deplo(key: str) -> str:
    dane = load_json('_Taverna Bot 2.0/res/jsons/deployment.json')
    return dane[key]

def return_primary(key: str) -> str:
    dane = load_json("_Taverna Bot 2.0/res/jsons/primary.json")
    #primary: list[str] = []
    #for element in dane[key]:
        #primary.extend(element)
    primary = " ".join(dane[key])
    return primary

def return_mission_rule(key: str) -> str:
    dane = load_json('_Taverna Bot 2.0/res/jsons/rule.json')
    #rule: list[str] = []
    #for element in dane[key]:
        #rule.extend(element)
    rule = " ".join(dane[key])
    return rule

def return_random_game() -> tuple:
    data = load_json('_Taverna Bot 2.0/res/jsons/deployment.json')
    deplo = random.choice(list(data.values()))
    
    data = load_json("_Taverna Bot 2.0/res/jsons/primary.json")    
    primary = " ".join(random.choice(list(data.values())))

    data = load_json('_Taverna Bot 2.0/res/jsons/rule.json')
    rule = " ".join(random.choice(list(data.values()))) 
    
    return deplo, primary, rule