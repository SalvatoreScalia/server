import uuid
from datetime import datetime as dateTimeLib

def generate_id():
    return str(uuid.uuid4())

class BaseEntity:
    def __init__(self, creator_competitor_id, base_entity_id=None, data_datetime_creation=None, **properties_kwargs):
        self.base_entity_id = base_entity_id if base_entity_id else generate_id()
        self.creator_competitor_id = creator_competitor_id or 0
        self.data_datetime_creation = data_datetime_creation if data_datetime_creation else dateTimeLib.now().strftime("%Y-%m-%d %H:%M:%S")
        self.data_is_visible = True
        self.data_properties = properties_kwargs if properties_kwargs is not None else {}

    def new_id(self):
        """Generate a new ID for the entity."""
        self.base_entity_id = generate_id()

    def to_dict(self):
        """Convert the instance to a dictionary, including class and module information."""
        result = {
            "__class__": self.__class__.__name__,
            "__module__": self.__class__.__module__,
        }
        for key, value in vars(self).items():
            if isinstance(value, BaseEntity):
                result[key] = value.to_dict()
            elif isinstance(value, list):
                result[key] = [item.to_dict() if isinstance(item, BaseEntity) else item for item in value]
            else:
                result[key] = value
        return result

    def game_time(self):
        """Calculate the time since the creation of the entity."""
        return dateTimeLib.now() - dateTimeLib.strptime(self.data_datetime_creation, '%Y-%m-%d %H:%M:%S')

    def update_properties(self, **new_properties):
        """Update the properties of the entity."""
        self.data_properties.update(new_properties)

    def _validate_and_set_list(self, items, item_type):
        """Validate and set a list of items ensuring they are of the correct type."""
        if isinstance(items, list) and all(isinstance(item, item_type) for item in items):
            return items
        else:
            raise TypeError(f"All items must be instances of {item_type.__name__}.")

    def read_properties(self, *keys):
        """Get a value from a nested dictionary using a list of keys."""
        d = self.data_properties
        for key in keys:
            if isinstance(d, dict):
                d = d.get(key, d)
            else:
                return d
        return d    

    def update_attributes(self, attributes, recursive=False):
        """Update attributes of the entity. Recursively update nested dictionaries if recursive is True."""
        for key, value in attributes.items():
            if hasattr(self, key):
                attr = getattr(self, key)
                if recursive and isinstance(attr, dict) and isinstance(value, dict):
                    self.merge_dicts_recursive(attr, value)
                else:
                    setattr(self, key, value)
            else:
                print(f"Warning: The attribute '{key}' does not exist in the {self.__class__.__name__} class.")

    @staticmethod
    def merge_dicts_recursive(original, updates):
        """Recursively merge updates into the original dictionary."""
        for key, value in updates.items():
            if isinstance(value, dict) and key in original and isinstance(original[key], dict):
                BaseEntity.merge_dicts_recursive(original[key], value)
            else:
                original[key] = value

class Competitor(BaseEntity):
    def __init__(self, creator_competitor_id, competitor_name=None, **properties_kwargs):
        super().__init__(creator_competitor_id=creator_competitor_id, **properties_kwargs)
        self.competitor_name = competitor_name or "default_name"
        self.list_of_tiles = []  # Initialize the list of tiles
        self.list_of_chips = []  # Initialize the list of chips
        self.list_of_actions = []  # Initialize the list of Action

    def add_tile(self, tile):
        """Add a Tile instance to the list of tiles."""
        if isinstance(tile, Tile):
            self.list_of_tiles.append(tile)
        else:
            raise TypeError("The added element must be an instance of Tile.")

    def add_chip(self, chip):
        """Add a Chip instance to the list of chips."""
        if isinstance(chip, Chip):
            self.list_of_chips.append(chip)
        else:
            raise TypeError("The added element must be an instance of Chip.")
    
    def add_action(self, action):
        """Add a Action instance to the list of actions."""
        if isinstance(action, Action):
            self.list_of_actions.append(action)
        else:
            raise TypeError("The added element must be an instance of Chip.")

class GameStage(BaseEntity):
    def __init__(self, creator_competitor_id, is_active=True, list_of_competitors=None, world_name=None, state='', **properties_kwargs):
        super().__init__(creator_competitor_id=creator_competitor_id, **properties_kwargs)
        self.last_edit_by = 0
        self.is_active = is_active
        self.world_name = world_name or 'world_name_default'
        self.state = state
        if list_of_competitors:
            self.list_of_competitors = self._validate_and_set_list(
                [Competitor(**competitor_data) if isinstance(competitor_data, dict) else competitor_data for competitor_data in list_of_competitors],
                Competitor
            )
        else:
            self.list_of_competitors = []


class Tile(BaseEntity):
    def __init__(self, position=None, custom_name=None, **properties_kwargs):
        super().__init__(creator_competitor_id=None, **properties_kwargs)
        self.position = position if position is not None else {}
        self.custom_name = custom_name if custom_name is not None else "name tile"

class Chip(BaseEntity):
    def __init__(self, position=None, custom_name=None, chip_type=None, **properties_kwargs):
        super().__init__(creator_competitor_id=None, **properties_kwargs)
        self.position = position if position is not None else {}
        self.custom_name = custom_name if custom_name is not None else "name chip"
        self.chip_type = chip_type

class Action(BaseEntity):
    def __init__(self, condition, result=False, challenger=None, globals_dict=None, **properties_kwargs):
        super().__init__(creator_competitor_id=None, **properties_kwargs)
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
        
class Item(BaseEntity):
    def __init__(self, name, description, **properties_kwargs):
        super().__init__(creator_competitor_id=None, **properties_kwargs)
        self.name = name
        self.description = description

class Resource(BaseEntity):
    def __init__(self, name, unit_type, quantity, base_extraction, max_constant_extraction, position=None, **properties_kwargs):
        super().__init__(creator_competitor_id=None, **properties_kwargs)
        self.name = name
        self.unit_type = unit_type
        self.quantity = quantity
        self.base_extraction = base_extraction
        self.max_constant_extraction = max_constant_extraction
        self.position = position if position is not None else {}

# Function to reconstruct the class instance from a dictionary
def from_dict(class_dict):
    """Reconstruct an instance of a class from a dictionary."""
    # Import the module of the class
    module_name = class_dict.pop("__module__", "")
    class_name = class_dict.pop("__class__", "")
    
    # Get the class reference
    module = __import__(module_name, fromlist=[class_name])
    class_ = getattr(module, class_name)
    
    # Convert nested dictionaries to BaseEntity instances
    for key, value in class_dict.items():
        if isinstance(value, dict) and "__class__" in value:
            class_dict[key] = from_dict(value)
        elif isinstance(value, list):
            class_dict[key] = [
                from_dict(item) if isinstance(item, dict) and "__class__" in item else item
                for item in value
            ]
    
    # Create and return the class instance
    return class_(**class_dict)
