import uuid
from collections import defaultdict
from pint import UnitRegistry

ACTIVE_ROUTES = defaultdict(set)

DEAFAULT_USERS = {
    'user0': {'user_id':str(uuid.uuid4()),'user_nickname':'nicknamemaster1','password': 'user0', 'role': 'master','competitor_id':0},
    'user1': {'user_id':str(uuid.uuid4()),'user_nickname':'nicknameplayer1','password': 'user1', 'role': 'player','competitor_id':0},
    'user2':{'user_id':str(uuid.uuid4()),'user_nickname':'nicknamemplayer2','password': 'user2','role':'player','competitor_id':0},
    'user3':{'user_id':str(uuid.uuid4()),'user_nickname':'nicknamemspectator1','password': 'user3','role':'spectator','competitor_id':0}
}

SERVER_USER ={}

######################################################
class Ct:                #CHIPS TYPES
    # Military Types
    MILITARY_BUILDING = 'military building'
    MILITARY_UNIT = 'military unit'
    LOGISTIC_UNIT = 'logistic unit'
    ARMOR_UNIT = 'armor unit'
    SHIP_UNIT = 'ship unit'
    AIR_UNIT = 'air unit'
    AIRPORT = 'airport'
    SHIPYARD = 'shipyard'
    MILITARY_BASE = 'military base'
    FORTRESS = 'fortress'
    BUNKER = 'bunker'
    SHOOTING_RANGE = 'shooting range'
    RADAR_STATION = 'radar station'
    COMMAND_AND_CONTROL_CENTER = 'command and control center'
    MILITARY_RESEARCH_AND_DEVELOPMENT_CENTER = 'military research and development center'
    MILITARY_TRAINING_CENTER = 'military training center'
    AMMUNITION_STORAGE = 'ammunition storage'
    
    # Industrial Types
    REFINERY = 'refinery'
    TANK_FACTORY = 'tank factory'
    POWER_PLANT = 'power plant'
    NUCLEAR_PLANT = 'nuclear plant'
    SILO = 'silo'
    WATER_TREATMENT_PLANT = 'water treatment plant'
    WAREHOUSE = 'warehouse'
    MANUFACTURING_PLANT = 'manufacturing plant'
    INDUSTRIAL_ZONE = 'industrial zone'
    RAILWAY_NETWORK = 'railway network'
    SERVICE_STATION = 'service station'
    
    # Civil Types
    BUILDING = 'building'
    PORT = 'port'
    HOSPITAL = 'hospital'
    SCHOOL = 'school'
    ROAD_NETWORK = 'road network'
    BRIDGE = 'bridge'
    WATER_SUPPLY_SYSTEM = 'water supply system'
    SEWAGE_SYSTEM = 'sewage system'
    LIBRARY = 'library'
    RESIDENTIAL_BUILDING = 'residential building'
    COMMERCIAL_BUILDING = 'commercial building'
    PARK = 'park'
    PUBLIC_TRANSPORT_STATION = 'public transport station'
    STADIUM = 'stadium'
    
    # Resource Extraction Infrastructure Types
    OIL_RIG = 'oil rig'
    OIL_FIELD = 'oil field'
    GAS_FIELD = 'gas field'
    MINE = 'mine'
    COAL_MINE = 'coal mine'
    URANIUM_MINE = 'uranium mine'
    QUARRY = 'quarry'
    PROCESSING_PLANT = 'processing plant'
    EXPLORATION_SITE = 'exploration site'
######################################################
class Wv:     #QUANTITY WORLDS VALUES
    # small_well in bbl (EXT : extraction)
    SMALL_WELL_QTY = 3e10
    SMALL_WELL_BASE_EXT = 1
    SMALL_WELL_MAX_CONST_EXT = 10
######################################################
STRINGS = {                  #STRINGS
    "save":"saved game stage"
}
######################################################