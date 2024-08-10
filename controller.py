import os
import json
from classes import EstadioPartida,generate_id,dateTimeLib
from pint import UnitRegistry

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

# Ruta del archivo JSON
DATA_FILE = 'data.json'

# Función para cargar datos desde un archivo JSON
def cargar_datos():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as file:
            datos = json.load(file)
            try:
                usuarios = datos.get('usuarios', {})
                estadios_partida = [EstadioPartida(**clase) for clase in datos.get('estadios_partida', [])]
                return usuarios, estadios_partida
            except Exception as e:
                print(f"Error datos.get(): {e}")
    return {
        'master1': {'id':generate_id(),'nick':'nicknamemaster1','password': 'master1', 'role': 'admin','status':'offline','ip':''},
        'player1': {'id':generate_id(),'nick':'nicknameplayer1','password': 'player1', 'role': 'player','status':'offline','ip':''},
        'player2':{'id':generate_id(),'nick':'nicknamemplayer2','password': 'player2','role':'player','status':'offline','ip':''}
    }, [EstadioPartida({'master1': {'id':generate_id(),'nick':'nicknamemaster1','password': 'master1', 'role': 'admin','status':'offline','ip':''}})] #usuarios['master1'] if usuarios is not None else 

# Función para guardar datos en un archivo JSON
def guardar_datos(usuarios,estadios_partida):
    with open(DATA_FILE, 'w') as file:
        json.dump({
            'usuarios': usuarios,
            'estadios_partida': [clase.to_dict() for clase in estadios_partida]
        }, file, indent=4)

# Exportar las clases (equivalente a export en JavaScript)
__all__ = [guardar_datos, cargar_datos,EstadioPartida,dateTimeLib]