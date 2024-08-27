import uuid
from datetime import datetime as dateTimeLib

def generate_id():
    return str(uuid.uuid4())

def recursive_update(original, updates):
        for key, value in updates.items():
            if isinstance(value, dict) and key in original and isinstance(original[key], dict):
                recursive_update(original[key], value)
            else:
                original[key] = value

class BaseEntity:
    def __init__(self, creator_competitor_id, base_entity_id=None, data_datetime_creation=None, **properties_kwargs):
        self.base_entity_id = base_entity_id if base_entity_id else generate_id()
        self.creator_competitor_id = creator_competitor_id or 0
        self.data_datetime_creation = data_datetime_creation if data_datetime_creation else dateTimeLib.now().strftime("%Y-%m-%d %H:%M:%S")
        self.data_is_visible = True
        self.data_properties = properties_kwargs if properties_kwargs is not None else {}

    def new_id(self):
        self.base_entity_id = generate_id()

    def to_dict(self):
        result = {}
        for key, value in vars(self).items():
            if isinstance(value, BaseEntity):
                result[key] = value.to_dict()
            elif isinstance(value, list):
                result[key] = [item.to_dict() if isinstance(item, BaseEntity) else item for item in value]
            else:
                result[key] = value
        return result

    def game_time(self):
        return dateTimeLib.now() - dateTimeLib.strptime(self.data_datetime_creation, '%Y-%m-%d %H:%M:%S')
    
    def update_properties(self, **new_properties):
        self.data_properties.update(new_properties)
    
    def _validate_and_set_list(self, items, item_type):
        """Validate and set a list of items ensuring they are of the correct type."""
        if isinstance(items, list) and all(isinstance(item, item_type) for item in items):
            return items
        else:
            raise TypeError(f"All items must be instances of {item_type.__name__}.")
    
    def read_properties(self,*keys):
        """Get a value from a nested dictionary using a list of keys."""
        d=self.data_properties
        for key in keys:
            if isinstance(d, dict):
                d = d.get(key,d)
            else:
                return d
        return d    
    
    def update_attributes(self, attributes):
        for key, value in attributes.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                print(f"Warning: The attribute '{key}' does not exist in the User class.")
                
    def update_attributes_recursive(self, attributes):
        for key, value in attributes.items():
            if hasattr(self, key):
                attr = getattr(self, key)
                if isinstance(attr, dict) and isinstance(value, dict):
                    # Recursively update nested dictionaries
                    recursive_update(attr, value)
                    #attr.update(value)
                else:
                    setattr(self, key, value)
            else:
                print(f"Warning: The attribute '{key}' does not exist in the User class.")
    
class GameStage(BaseEntity):
    def __init__(self,creator_competitor_id,is_active=True, list_of_competitors=None, world_name=None, state='', **properties_kwargs):
        super().__init__(creator_competitor_id=creator_competitor_id,id=None,data_datetime_creation=None,**properties_kwargs)
        self.last_edit_by = 0
        self.is_active = is_active
        self.world_name = world_name or 'world_name_default'
        self.state = state
        self.list_of_competitors = list_of_competitors if self._is_valid_competitor_list(list_of_competitors) else [Competitor(**competitor_data) for competitor_data in list_of_competitors] if list_of_competitors else TypeError("The list_of_competitors is not a list of Competitor")

    def _is_valid_competitor_list(self, competitors):
        """Check if the provided list contains only Competitor instances."""
        return isinstance(competitors, list) and all(isinstance(item, Competitor) for item in competitors)
    
    def add_competitor(self, competitor):
        """Add a Competitor instance to the list."""
        if isinstance(competitor, Competitor):
            self.list_of_competitors.append(competitor)
        else:
            raise TypeError("The added element must be an instance of Competitor.")

    def get_competitors(self):
        return self.list_of_competitors

    def update_state_(self,text=None):
        self.state = f"State updated at {dateTimeLib.now()}" if text is None else text

    def update_last_edit_by_competitor_id(self,id):
        for competitor in self.list_of_competitors: #if self._is_valid_competitor_list(self.list_of_competitors) else TypeError("The list must contein only Competitor class or is viod"):# Find and update the specific competitor
            if id == competitor.base_entity_id:
                 self.last_edit_by = competitor
                 break  # No need to continue once the competitor is found

    def print_data_of_game_stage(self):
        print(f"Saving class game stage {self.base_entity_id}: {self.state}")

class Competitor(BaseEntity):
    def __init__(self,creator_competitor_id=None,role=None, competitor_nickname=None, points=None, own_tiles=None, own_chips=None,own_actions=None, **properties_kwargs):
        super().__init__(creator_competitor_id,id=None,data_datetime_creation=None,**properties_kwargs)
        self.role = role if role is not None else "player"
        self.points = points if points is not None else {}
        self.nick_name = competitor_nickname if competitor_nickname is not None else f"nickname_{self.base_entity_id}"
        self.list_of_tiles = self._validate_and_set_list(own_tiles, Tile) if own_tiles is not None else []
        self.list_of_chips = self._validate_and_set_list(own_chips, Chip) if own_chips is not None else []
        self.list_of_actions = self._validate_and_set_list(own_actions,Action)if own_actions is not None else []

    def add_tile(self, tile):
        """Add a Tile instance to the list of own_tiles."""
        if isinstance(tile, Tile):
            self.list_of_tiles.append(tile)
        else:
            raise TypeError("The added element must be an instance of Tile.")

    def add_chip(self, chip):
        """Add a Chip instance to the list of own_chips."""
        if isinstance(chip, Chip):
            self.list_of_chips.append(chip)
        else:
            raise TypeError("The added element must be an instance of Chip.")

    def get_tiles(self):
        return self.list_of_tiles

    def get_chips(self):
        return self.list_of_chips

class Resource(BaseEntity):
    def __init__(self, name, unit_type, quantity, base_extraction, max_constant_extraction, position=None, **properties_kwargs):
        super().__init__(id=None, creator_competitor_id=None,data_datetime_creation=None,**properties_kwargs)
        self.name = name
        self.unit_type = unit_type
        self.quantity = quantity
        self.base_ext = base_extraction
        self.max_constant_ext = max_constant_extraction
        self.position = position if position is not None else {}

class Tile(BaseEntity):
    def __init__(self, position=None, custom_name=None, **properties_kwargs):
        super().__init__(id=None, creator_competitor_id=None,data_datetime_creation=None,**properties_kwargs)
        self.position = position if position is not None else {}
        self.custom_name = custom_name if custom_name is not None else "name tile"

class Chip(BaseEntity):
    def __init__(self, position=None, custom_name=None, type=None,**properties_kwargs):
        super().__init__(id=None, creator_competitor_id=None,data_datetime_creation=None,**properties_kwargs)
        self.position = position if position is not None else {}
        self.custom_name = custom_name if custom_name is not None else "name chip"
        self.type = type

class Item(BaseEntity):
    def __init__(self, name, description, **properties_kwargs):
        super().__init__(id=None,creator_competitor_id=None,data_datetime_creation=None,**properties_kwargs)
        self.name = name
        self.description = description

class Action(BaseEntity):
    def __init__(self, condition, result=False, challenger=Competitor, globals_dict=None, **properties_kwargs):
        super().__init__(id=None, creator_competitor_id=None, data_datetime_creation=None, **properties_kwargs)
        self.result = result
        self.condition = condition
        self.challenger = challenger
        self.globals_dict = globals_dict or {}
        
        # Convert condition string to a callable if it's not already
        if isinstance(self.condition, str):
            self.condition = self._string_to_function(self.condition)

    def _string_to_function(self, condition_str):
        """
        Convert a string representation of a function into a callable function.
        The function must be defined in a way that it can accept 'challenger' and 'globals_dict' as arguments.
        """
        local_vars = {}
        try:
            exec(f"def condition_function(challenger, globals_dict):\n    {condition_str}", globals(), local_vars)
            return local_vars['condition_function']
        except Exception as e:
            raise ValueError(f"Failed to convert string to function: {e}")
    
    def evaluate_condition(self, return_result=False):
        """
        Evaluate the condition with the challenger and globals_dict as arguments, or return the result attribute.
        
        :param return_result: If True, return self.result instead of evaluating the condition.
        :return: The result of the condition or the self.result value.
        """
        if return_result:
            return self.result
        elif callable(self.condition):
            return self.condition(self.challenger, self.globals_dict)
        else:
            raise ValueError("Condition is not callable!")


# Exportar las clases (equivalente a export en JavaScript)
__all__ = ['Resource', 'Item', 'Competitor', 'Chip', 'Tile', 'GameStage', 'dateTimeLib', 'Action', generate_id]
