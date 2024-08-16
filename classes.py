import random
import uuid
from datetime import datetime as dateTimeLib

strings = {
    
}

# Función para generar IDs únicos
def generate_id():
    return str(uuid.uuid4())

class BaseEntity:
    def __init__(self, player_creator,data_id=None,date_time_creation=None):
        self.data_id = data_id if data_id else generate_id()
        self.last_edit_by = player_creator
        self.date_time_creation = date_time_creation if date_time_creation else dateTimeLib.now().strftime("%Y-%m-%d %H:%M:%S")

    def to_dict(self):
        return vars(self)

class TemporalEntity(BaseEntity):
    def __init__(self, player_creator, **kwargs):
        super().__init__(player_creator, **kwargs)

    def game_time(self):
        return dateTimeLib.now() - dateTimeLib.strptime(self.date_time_creation, '%Y-%m-%d %H:%M:%S')

class EstadioPartida(TemporalEntity):
    def __init__(self, player_creator, data_state=True, data_players=None, world_name='World Names', state='', properties='', **kwargs):
        super().__init__(player_creator, **kwargs)
        self.data_state = data_state
        self.data_players = data_players if data_players else []
        self.world_name = world_name
        self.state = state
        self.properties = properties

    def update_state_datetime(self):
        self.state = f"Estado actualizado a las {dateTimeLib.now()}"

    def basic_sample(self):
        return {"id": self.data_id, "world name": self.world_name, "state": self.state}

    def save_state(self):
        print(f"Guardando estado de la clase {self.data_id}: {self.state}")

    def change_tile_owner(self, tile, new_owner):
        # Remove tile from current owner
        for player in self.data_players:
            if tile in player.own_tiles:
                player.own_tiles.remove(tile)
                break
        # Assign tile to new owner
        new_owner.own_tiles.append(tile)

class Resource(BaseEntity):
    def __init__(self, creator_player, name, unit_type, quantity, base_extraction, max_constant_extraction, position=None, **kwargs):
        super().__init__(creator_player, **kwargs)
        self.name = name
        self.unit_type = unit_type
        self.quantity = quantity
        self.base_ext = base_extraction
        self.max_constant_ext = max_constant_extraction
        self.position = position if position is not None else {}

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

class Item(BaseEntity):
    def __init__(self, creator_player, name, description, properties=None, **kwargs):
        super().__init__(creator_player, **kwargs)
        self.name = name
        self.description = description
        self.properties = properties if properties is not None else {}

class Player(BaseEntity):
    def __init__(self, name, points=None, nick_name="", own_tiles=None, own_chips=None, **kwargs):
        super().__init__(None, **kwargs)  # Los jugadores no tienen creador
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
        else:
            self.points["resource"] = {"name": resource.name, "unit": resource.unit_type, "quantity": resource.quantity}

        return self.points["resource"]["quantity"]

class Chip(BaseEntity):
    def __init__(self, creator_player, position=None, custom_name="", type="", properties=None, **kwargs):
        super().__init__(creator_player, **kwargs)
        self.position = position if position is not None else {}
        self.custom_name = custom_name
        self.type = type
        self.properties = properties if properties is not None else {}

class Tile(BaseEntity):
    def __init__(self, creator_player, position=None, custom_name="", chips=None, properties=None, **kwargs):
        super().__init__(creator_player, **kwargs)
        self.position = position if position is not None else {}
        self.custom_name = custom_name
        self.chips = chips if chips is not None else []
        self.properties = properties if properties is not None else {}

    def generate_resource(self, name):
        pass  # Implementación necesaria si es requerida

# Exportar las clases (equivalente a export en JavaScript)
__all__ = ['Resource', 'Item', 'Player', 'Chip', 'Tile', 'EstadioPartida', generate_id, dateTimeLib]
