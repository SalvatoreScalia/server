import random
import uuid
from datetime import datetime as dateTimeLib

# Función para generar IDs únicos
def generate_id():
    return str(uuid.uuid4())

# The state of all components of classes in the simulation
class EstadioPartida:
    def __init__(self, data_state = True):
        self.data_id = generate_id()
        self.date_time_creation = dateTimeLib.now().strftime("%Y-%m-%d %H:%M:%S")
        self.data_state = data_state
        self.data_type ='type'
        self.data_frame_world = 'frame'
        self.data_time_tick = 1
        self.data_rules = {'rule':'streetMaps'}
        self.data_players = []
        self.world_name = 'World Names'
        self.state = ''
        self.properties = ''

    def update_state_datetime(self):
        self.state = f"Estado actualizado a las {dateTimeLib.now()}"

    def basic_sample(self):
        return {"id": self.data_id, "world name" : self.world_name, "sate" : self.state}

    def save_state(self):
        return print(f"Guardando estado de la clase {self.data_id}: {self.state}")
    
    #no function
    def game_time(self):
        return dateTimeLib.now() - self.date_time_creation

    def to_dic(self):
        return vars(self)

# Clase Resource
class Resource:
    def __init__(self, name, unit_type, quantity, base_extraction, max_constant_extraction):
        self.id = generate_id()
        self.name = name
        self.unit_type = unit_type
        self.quantity = quantity
        self.base_ext = base_extraction
        self.max_constant_ext = max_constant_extraction  # cada 1s = 1m

    def production_rule_random_base(self, level_buildings_percent):
        random_base = random.randint(0, self.base_ext)
        extraction = self.max_constant_ext * level_buildings_percent + random_base
        if self.quantity - extraction < 0:
            last_extraction = self.quantity
            self.quantity = 0
            return last_extraction
        else:
            self.quantity -= extraction
            return extraction

    def regenerate(self, quantity):
        self.quantity += quantity

# Clase Item
class Item:
    def __init__(self, name, description, properties=None):
        self.id = generate_id()
        self.name = name
        self.description = description
        self.properties = properties if properties is not None else {}

# Clase Player
class Player:
    def __init__(self, name, points=None, nick_name="", own_tiles=None, own_chips=None):
        self.id = generate_id()
        self.name = name
        self.points = points if points is not None else {}
        self.nick_name = nick_name
        self.own_tiles = own_tiles if own_tiles is not None else []
        self.own_chips = own_chips if own_chips is not None else []

    def update_points_resource(self, resource):
        total = 0
        for tile in self.own_tiles:
            for chip in tile.chips:
                if chip.properties.get("level") is not None and chip.type == "BUILDING":
                    total += resource.production_rule_random_base(chip.properties["level"])

        if "resource" in self.points:
            self.points["resource"]["quantity"] += total
            return self.points["resource"]["quantity"]
        else:
            self.points["resource"] = {"name": resource.name, "unit": resource.unit_type, "quantity": resource.quantity}
            return self.points["resource"]["quantity"]

# Clase Chip
class Chip:
    def __init__(self, position=None, custom_name="", type="", properties=None):
        self.id = generate_id()
        self.position = position if position is not None else {}
        self.custom_name = custom_name
        self.type = type
        self.properties = properties if properties is not None else {}

# Clase Tile
class Tile:
    def __init__(self, position=None, custom_name="", chips=None, properties=None):
        self.id = generate_id()
        self.position = position if position is not None else {}
        self.custom_name = custom_name
        self.chips = chips if chips is not None else []
        self.properties = properties if properties is not None else {}

    def generate_resource(self, name):
        pass  # Implementación necesaria si es requerida

# Exportar las clases (equivalente a export en JavaScript)
__all__ = ['Resource', 'Item', 'Player', 'Chip', 'Tile', 'EstadioPartida']
