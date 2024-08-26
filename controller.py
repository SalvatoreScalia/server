import os
import json
from shared_data import DEAFAULT_USERS
from classes import GameStage, Competitor

SAVES_PATH = "saves/"
file_name ='data.json'

def read_user_list():
    if os.path.exists(SAVES_PATH+file_name+'.json'):
        with open(SAVES_PATH+file_name+'.json', 'r') as file:
            data = json.load(file)  
            try:
                users = data.get('users', {})
                print("read successfully!")
                return users
            except Exception as e:
                print(f"Error datos.get(): {e}")
    return DEAFAULT_USERS

# Función para cargar datos desde un archivo JSON
def read_json_data(file_name=None):
    file_name_ = file_name if file_name else 'data'
    if os.path.exists(SAVES_PATH+file_name_+'.json'):
        with open(SAVES_PATH+file_name_+'.json', 'r') as file:
            data = json.load(file)  
            try:
                users = data.get('users', {})
                game_stages = [GameStage(**class_) for class_ in data.get('gameStages', [])]##Pendiente ver si **clase dentro del constructor genera una clase correcta
                print("read successfully!")
                return users, game_stages
            except Exception as e:
                print(f"Error data.get() or parse GameStage(**class): {e}")
    c = Competitor(role=DEAFAULT_USERS['user0']['role'],competitor_nickname=DEAFAULT_USERS['user0']['user_nickname'])
    list_c = [c]
    return DEAFAULT_USERS, [GameStage(creator_competitor_id=c.base_entity_id,list_of_competitors=list_c,world_name='default_name')]

# Función para guardar datos en un archivo JSON
def write_json_data(file_name,users,list_of_game_stages):
    try:
        with open(SAVES_PATH+file_name+'.json', 'w') as file:
            json.dump({
                'users': users,
                'gameStages': [class_.to_dict() for class_ in list_of_game_stages]
            }, file, indent=4)
        print("saved successfully!")
    except Exception as e:
        print(f"Error when save the json: {e}")

# Exportar las clases (equivalente a export en JavaScript)
__all__ = ['write_json_data', 'read_json_data','read_user_list']