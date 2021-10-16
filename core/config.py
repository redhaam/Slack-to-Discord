import os
import sys
from core.utils import loads_to_object


def load_config():
    global config
    if not os.path.isfile("config.json"):
        sys.exit("'config.json' not found! Please add it and try again.")
    else:
        config = loads_to_object("config.json")
    return config


def load_from_env(name):
    if name in os.environ :
        WEBHOOK_URL = os.getenv(name)  
    if WEBHOOK_URL == None:
        raise f"{name}  not found"
    return WEBHOOK_URL
