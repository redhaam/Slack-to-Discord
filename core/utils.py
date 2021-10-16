import io
from io import BytesIO, FileIO
import re
import discord
import json
from types import SimpleNamespace
from urllib.request import urlopen
from datetime import datetime
from discord.embeds import Embed

def import_posts_from_path(path):
    return None


def loads_to_object(json_file):
    return json.loads(open(json_file, "r").read(),object_hook=lambda d: SimpleNamespace(**d))

def loads_to_array(json_file,callback_fn= lambda x: (x), parse_float=None):
    return json.load(open(json_file, "r"),object_hook=lambda x: callback_fn(x),parse_float= parse_float )

def get_file_url(file) ->str:
    return file["url_private"]

def get_file_name(file) -> str:
    return file["name"]

def resolve_files(files):
    attachements= []
    for f in files:
        file_url= get_file_url(f)
        data = read_file_url(file_url)
        attachements.append(
        discord.File(data,filename=get_file_name(f)))
    return attachements

def resolve_embeds(embeds):
    attach =[]
    for em in embeds:
        description= "--"
        if 'text' in em:
            description = em['text'][:4096]
        elif 'original_url' in em:
            description= em['original_url']
        embed_title= em['title'][:256] if 'title' in em else Embed.Empty
        embed_title_link = em['title_link'] if 'title_link' in em else Embed.Empty
        embed = Embed(title=embed_title,description=description,url=embed_title_link)
        if 'image_url' in em:
            embed= embed.set_image(url=em['image_url'])
        attach.append(embed)
    return attach

def create_text_embed(text):
    return Embed(description=text)

def timestamp_to_date(timestamps):
    return datetime.fromtimestamp(timestamps)

def date_to_timestamp(stime):
    return datetime.strptime(stime, "%d-%m-%Y").timestamp()

def append_date_footer(embeds:list, date):
    date_time = timestamp_to_date(date)
    embeds.append(Embed(description= date_time))


def read_file_url(url) -> BytesIO:
    f= urlopen(url)
    data= f.read()
    return io.BytesIO(data)

