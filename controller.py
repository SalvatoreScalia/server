import os
import json
from shared_data import DEAFAULT_USERS
from classes import GameStage, Competitor, from_dict

SAVES_PATH = "saves/"
DEFAULT_FILE_NAME = 'data.json'

def read_user_list(file_name=DEFAULT_FILE_NAME):
    """Read the list of users from a JSON file."""
    file_path = os.path.join(SAVES_PATH, file_name)
    
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r') as file:
                data = json.load(file)
                users = data.get('users', DEAFAULT_USERS)
                print("Users read successfully!")
                return users
        except json.JSONDecodeError as e:
            print(f"Invalid JSON content in {file_name}. Error: {e}")
        except Exception as e:
            print(f"An unexpected error occurred while reading {file_name}: {e}")
    return DEAFAULT_USERS

def read_json_data(file_name=DEFAULT_FILE_NAME):
    """Load users and game stages from a JSON file."""
    file_path = os.path.join(SAVES_PATH, file_name)
    
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r') as file:
                data = json.load(file)
                
                users = data.get('users', DEAFAULT_USERS)
                
                game_stages = [from_dict(class_dict) for class_dict in data.get('gameStages', [])]
                print("Data read successfully!")
                return users, game_stages
        except json.JSONDecodeError as e:
            print(f"Invalid JSON content in {file_name}. Error: {e}")
        except Exception as e:
            print(f"An unexpected error occurred while reading {file_name}: {e}")
    else:
        print(f"[read_json_data]File '{file_name}' does not exist. Loading default values.")
    
    # If the file doesn't exist or an error occurs, return default values
    default_competitor = Competitor(creator_competitor_id=DEAFAULT_USERS['user0']['user_id'],
                                    competitor_name=DEAFAULT_USERS['user0']['user_nickname'])
    default_game_stage = GameStage(creator_competitor_id=default_competitor.base_entity_id,
                                   list_of_competitors=[default_competitor],
                                   world_name='default_name')
    
    return DEAFAULT_USERS, [default_game_stage]

def write_json_data(file_name, users, list_of_game_stages):
    """Save users and game stages to a JSON file."""
    file_path = os.path.join(SAVES_PATH, file_name + '.json')
    
    try:
        with open(file_path, 'w') as file:
            json.dump({
                'users': users,
                'gameStages': [class_.to_dict() for class_ in list_of_game_stages]
            }, file, indent=4)
        print("Data saved successfully!")
    except Exception as e:
        print(f"Error saving data to {file_name}: {e}")
