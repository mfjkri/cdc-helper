import re
from typing import Any

attribute_templates = [
    ["available_days", list],
    ["available_days_in_view", list],
    ["available_times", list],
    ["available_sessions", dict],
    ["earlier_sessions", dict],
    ["booked_sessions", dict],
    ["lesson_name", str]
]

class Types:
    SIMULATOR = "simulator"
    PRACTICAL = "practical"
    ROAD_REVISION = "rr"
    ETT = "ett"
    BTT = "btt"
    RTT = "rtt"
    PT = "pt"

class CDCAbstract:
    def __init__(self, username, password, headless=False):
        self.username = username
        self.password = password
        self.headless = headless
        
        field_types = [attr for attr in dir(Types) if not callable(getattr(Types, attr)) and not attr.startswith("__")]
        for _, field_type in enumerate(field_types):
            field_type_str = getattr(Types, field_type)
            
            for i in range(0, len(attribute_templates)):
                attribute_template = attribute_templates[i]
                setattr(self, f"{attribute_template[0]}_{field_type_str}", attribute_template[1]())
                
         # Simulator
        self.can_book_next_simulator = True
        self.has_auto_reserved_simulator = False

        # Practical
        self.can_book_next_practical_lesson = True
        self.has_auto_reserved_practical = False

        # PT
        self.can_book_pt = True
        

    def __str__(self):
        #members = [attr for attr in dir(self) if not callable(getattr(self, attr)) and not attr.startswith("__")]
        blacklist_attr_names = "captcha_solver,"
        abstract_str = "# ------------------------------------- - ------------------------------------ #\n"
        abstract_str += "CDC_ABSTRACT\n"
        
        abstract_str += f"user = {str(self.username)}"
        abstract_str += f"password = {str(self.password)}"
        abstract_str += f"headless = {str(self.headless)}"

        abstract_str += "\n"
        
        field_types = [attr for attr in dir(Types) if not callable(getattr(Types, attr)) and not attr.startswith("__")]
        abstract_attr = [attr for attr in dir(self) if not callable(getattr(self, attr)) and not attr.startswith("__")]
        for _, field_type in enumerate(field_types):
            abstract_str += f"# {str(field_type)}\n"

            field_type_str = getattr(Types, field_type)
            for _, attr in enumerate(abstract_attr):
                if (field_type_str in attr) and (not attr in blacklist_attr_names):
                    abstract_str += f"# {str(attr)} = {str(getattr(self, attr))}\n"
            abstract_str += "\n"
        abstract_str += "# ------------------------------------- - ------------------------------------ #"
        return abstract_str
        
    def get_attribute(self, attribute:str):
        return getattr(self, attribute)
    
    def set_attribute(self, attribute:str, value:Any):
        setattr(self, attribute, value)

    def get_attribute_with_fieldtype(self, attribute:str, field_type:str):
        return getattr(self, f"{attribute}_{field_type}")
    
    def set_attribute_with_fieldtype(self, attribute:str, field_type:str, value:Any):
        setattr(self, f"{attribute}_{field_type}", value)

