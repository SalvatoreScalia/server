import os
import json
from classes import GameStage,generate_id,dateTimeLib, Competitor

######################################################
#                   Types of chips
######################################################
TYPE_CHIP = {
    # MILITARY
    'MILITARY_BUILDING': 'military building',
    'MILITARY_UNIT': 'military unit',
    'LOGISTIC_UNIT': 'logistic unit',
    'ARMOR_UNIT': 'armor unit',
    'SHIP_UNIT': 'ship unit',
    'AIR_UNIT': 'air unit',
    'AIRPORT': 'airport',
    'SHIPYARD': 'shipyard',
    'MILITARY_BASE': 'military base',
    'FORTRESS': 'fortress',
    'BUNKER': 'bunker',
    'SHOOTING_RANGE': 'shooting range',
    'RADAR_STATION': 'radar station',
    'COMMAND_AND_CONTROL_CENTER': 'command and control center',
    'MILITARY_RESEARCH_AND_DEVELOPMENT_CENTER': 'military research and development center',
    'MILITARY_TRAINING_CENTER': 'military training center',
    'AMMUNITION_STORAGE': 'ammunition storage',
    # INDUSTRIAL
    'REFINERY': 'refinery',
    'TANK_FACTORY': 'tank factory',
    'POWER_PLANT': 'power plant',
    'NUCLEAR_PLANT': 'nuclear plant',
    'SILO': 'silo',
    'WATER_TREATMENT_PLANT': 'water treatment plant',
    'WAREHOUSE': 'warehouse',
    'MANUFACTURING_PLANT': 'manufacturing plant',
    'INDUSTRIAL_ZONE': 'industrial zone',
    'RAILWAY_NETWORK': 'railway network',
    'SERVICE_STATION': 'service station',
    # CIVIL
    'BUILDING': 'building',
    'AIRPORT': 'airport',
    'PORT': 'port',
    'HOSPITAL': 'hospital',
    'SCHOOL': 'school',
    'ROAD_NETWORK': 'road network',
    'BRIDGE': 'bridge',
    'WATER_SUPPLY_SYSTEM': 'water supply system',
    'SEWAGE_SYSTEM': 'sewage system',
    'LIBRARY': 'library',
    'RESIDENTIAL_BUILDING': 'residential building',
    'COMMERCIAL_BUILDING': 'commercial building',
    'PARK': 'park',
    'PUBLIC_TRANSPORT_STATION': 'public transport station',
    'STADIUM': 'stadium',
    # INFRASTRUCTURE DE EXTRACCIÓN DE RECURSOS
    'OIL_RIG': 'oil rig',
    'OIL_FIELD': 'oil field',
    'GAS_FIELD': 'gas field',
    'MINE': 'mine',
    'COAL_MINE': 'coal mine',
    'URANIUM_MINE': 'uranium mine',
    'QUARRY': 'quarry',
    'PROCESSING_PLANT': 'processing plant',
    'EXPLORATION_SITE': 'exploration site',
    'REFINERY': 'refinery'
}
######################################################
#               QUANTITY WORLDS VALUES
######################################################
# small_well in bbl (EXT : extraction)
SMALL_WELL_QTY = 3e10
SMALL_WELL_BASE_EXT = 1
SMALL_WELL_MAX_CONST_EXT = 10

######################################################
#                    Strings 
######################################################
STRINGS = {
    "save":"saved game stage"
}

# Ruta del archivo JSON
DATA_FILE = 'data.json'
DEAFAULT_USERS = {
    'user0': {'data_id':generate_id(),'nick_name':'nicknamemaster1','password': 'user0', 'role': 'master','status':'offline'},
    'user1': {'data_id':generate_id(),'nick_name':'nicknameplayer1','password': 'user1', 'role': 'player','status':'offline'},
    'user2':{'data_id':generate_id(),'nick_name':'nicknamemplayer2','password': 'user2','role':'player','status':'offline'},
    'user3':{'data_id':generate_id(),'nick_name':'nicknamemspectator1','password': 'user3','role':'spectator','status':'offline'}
}

# Función para cargar datos desde un archivo JSON
def cargar_datos():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as file:
            datos = json.load(file)
            try:
                users = datos.get('users', {})
                game_stages = [GameStage(**clase) for clase in datos.get('game_stages', [])]
                print("saved successfully!")
                return users, game_stages
            except Exception as e:
                print(f"Error datos.get(): {e}")
    return DEAFAULT_USERS, [GameStage(competitor_creator=Competitor(role=DEAFAULT_USERS['user0']['role'],nick_name=DEAFAULT_USERS['user0']['nick_name'],properties_kwargs={"url":"https://www.youtube.com/watch?v=tH2w6Oxx0kQ&ab_channel=kansasVEVO"}))] 

# Función para guardar datos en un archivo JSON
def guardar_datos(users,list_of_game_stages):
    try:
        with open(DATA_FILE, 'w') as file:
            json.dump({
                'users': users,
                'game_stages': [clase.to_dict() for clase in list_of_game_stages]
            }, file, indent=4)
        print("saved successfully!")
    except Exception as e:
        print(f"Error when save the json: {e}")

# Exportar las clases (equivalente a export en JavaScript)
__all__ = ['guardar_datos', 'cargar_datos','GameStage','dateTimeLib','Competitor',generate_id]