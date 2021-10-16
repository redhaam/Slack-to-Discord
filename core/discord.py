import aiohttp
import discord
from discord import embeds
from discord.webhook.async_ import Webhook
import requests
from core.utils import append_date_footer, create_text_embed, resolve_embeds, resolve_files
from core.message import Message
from core.config import load_from_env


bot_token= load_from_env("DISCORD_TOKEN")
guild_id= int(load_from_env("GUILD_ID"))
channel_id= int(load_from_env("CHANNEL_ID"))
    


def create_thread(message_id, thread_name):
    API_ENDPOINT =f'https://discord.com/api/v9/channels/{channel_id}/messages/{message_id}/threads' 
    headers={
        'Authorization': f'Bot {bot_token}'
    }
    req={
        'name': thread_name,
        'auto_archive_duration': 1440
    } 
    # msg_obj= Object(message_id)
    return requests.post(API_ENDPOINT,json=req,headers=headers)

def make_message(message:Message):
    files=[]
    embeds= []
    text=""
    message.avatar_url= get_user_avatar(message.content)
    message.username= get_user_display_name(message.content)
    if len(message.get_message_text()) > 2000:
        text_embed= create_text_embed(message.get_message_text())
        embeds.append(text_embed)
    else:
        text= message.get_message_text() 
    if message.has_embeds():
        embeds = resolve_embeds(message.content["attachments"])
    if message.has_attachements():
        files= resolve_files(message.content["files"])
    append_date_footer(embeds,int(float(message.get_id())))
    message.text=text
    message.embeds =embeds
    message.files=files

async def send_webhook(webhook,message: Message,thread=None):
    make_message(message)
    if thread is None:
        return await webhook.send(content=message.text,username=message.username,avatar_url=message.avatar_url,files=message.files,embeds=message.embeds,wait=True)
    else:
        thread_object = discord.Object(thread['id'])
        return await webhook.send(content=message.text,username=message.username,avatar_url=message.avatar_url,files=message.files,embeds=message.embeds,thread=thread_object,wait=True)

async def send_thread(webhook,reply):
    send_webhook(webhook,reply)

async def create_webhook(webhook_url):    
    session= aiohttp.ClientSession()
    return Webhook.from_url(url=webhook_url,session=session)

from core.user import get_user_avatar,get_user_display_name

