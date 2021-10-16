import re
import requests
from core.utils import loads_to_array
from core.config import load_from_env
mention_tag = re.compile('<@\w+>')
members_endpoint= load_from_env('MEMBERS_LIST_URL')
alumni_endpoint= load_from_env('ALUMNI_LIST_URL')

class User():
    def __init__(self):
        self.config= load_config()
        self.users=load_users(self.config.USERS_FILE_PATH)


def load_users(file_path):
    return loads_to_array(file_path)

def get_discord_id(slack_id):
    user= next((us for us in users_db if us["slackId"] == slack_id), None)
    if user is None or "discord_id" not in user:
        return None
    else:
        return user["discord_id"]

def load_users_from_db():
    usr=[]
    res = requests.get(members_endpoint).json()
    usr.extend(res)
    res = requests.get(alumni_endpoint).json()
    usr.extend(res)
    return usr

def resolve_mentions(message:str):
    tags = mention_tag.finditer(message)
    new_message=message
    for tag in tags:
        user_id = tag[0][2:-1]
        user=_find_user_in_file(user_id)
        if user is not None:
            username = get_discord_id(user["id"])
            if username is None:
                username= _get_display_name(user["profile"])
            new_message= new_message.replace(user_id,username)
    return new_message



def _find_user_in_file(user_id):
    return next((us for us in users if us["id"] == user_id), None)

def is_thread_broadcast(message):
    return "subtype" in message and message["subtype"]=='thread_broadcast'


def get_user_avatar(message):
    # if is_thread_broadcast(message) or not "user_profile" in message :
    user_id= message["user"] if 'user' in message else message["username"]
    user = _find_user_in_file(user_id)
    if user is None:
        return None
    return user["profile"]["image_1024"] if "image_1024" in user["profile"] else user["profile"]["image_512"]
    # else:
        # return message["user_profile"]["image_72"]

def _get_display_name(user_profile):
    return user_profile["display_name"] if user_profile["display_name"] != "" else user_profile["real_name"]


def get_user_display_name(message):
    if is_thread_broadcast(message) or not "user_profile" in message:
        user_id= message["user"] if "user" in message else message["username"]
        user = _find_user_in_file(user_id)
        if user is None:
            return None
        display_name=_get_display_name(user["profile"])
        return display_name
    else:
        return _get_display_name(message["user_profile"])


from core.config import  load_config, load_from_env

config= load_config()
users=load_users(config.USERS_FILE_PATH)
users_db= load_users_from_db()