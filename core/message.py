from core.user import resolve_mentions
import glob
from discord.threads import Thread
from core.utils import  loads_to_array
import json


class Message():
    
    def __init__(self,message):
        self.content={}
        self.content.update(message)
        self.content["text"] = resolve_mentions(self.content["text"])
        self.slack_id= self.content["ts"]
        self.replies: list(Message)=[]

    def get_id(self):
        return self.slack_id

    def get_thread_id(self) -> str:
        return self.content["thread_ts"]

    def is_join_channel_message(self):
        return "subtype" in self.content and self.content["subtype"]=="channel_join"

    def is_join_channel_message(self):
        return "subtype" in self.content and self.content["subtype"]=="channel_join"

    def is_channel_purpose_message(self):
        return "subtype" in self.content and self.content["subtype"]== "channel_purpose"

    def is_update_channel_message(self):
        return "subtype" in self.content and self.content["subtype"]== "channel_name"

    def is_reply(self):
        return "parent_user_id" in self.content and (not "replies" in self.content)

    def is_posted(self):
        
        return self.posted if hasattr(self,"posted") else False

    def add_reply(self,reply):
        self.replies.append(reply)

    def has_replies(self):
        return len(self.replies) > 0
    
    def has_attachements(self):
        return "files" in self.content

    def has_embeds(self):
        return "attachments" in self.content

    def get_message_text(self):
        return self.content["text"] if "text" in self.content else ""   
    def get_trim_message_text(self,number):
        return self.content["text"][:number] if "text" in self.content else ""

    def to_json(self) -> str:
        return self.__dict__

    def dump_to_json(self,path):
        with open(path,"w") as file:
            json.dump(self,file, default= lambda m : m.to_json(),indent=4)

    async def to_server(self, webhook):
            response = await send_webhook(webhook, self)
            self.discord_id= response.id
            self.posted= True
            if self.has_replies():
                await self.attach_replies(webhook)

    async def attach_replies(self,webhook):
        message_id = self.discord_id
        message_content = self.get_message_text()
        thread_title= message_content[:100]
        if not thread_title:
            thread_title= "---"
        res = create_thread(message_id,thread_title)
        thread:Thread = json.loads(res.content.decode('utf-8'))
        self.thread_id= thread['id']
        for reply in self.replies:
            response = await send_webhook(webhook, reply,thread=thread)

    def in_date_range(self,start,end):
        ts = int(float(self.get_id()))
        return ts > start and ts < end

    def to_keep(self):
        return not (self.is_join_channel_message() or self.is_channel_purpose_message() or self.is_update_channel_message())


class Messages_List():
    def __init__(self, messages_list=[]) -> None:
        self.messages_list = messages_list

    def add_message(self, message: Message):
        if message.to_keep():
            if message.is_reply():
                self.add_reply(message)
            else:
                self.messages_list.append(message)

    def load_messages_list(self,channel_name):
        self.channel_name= channel_name
        for file in glob.glob(f"Slack-Export/{self.channel_name}/*.json"):
            posts = loads_to_array(file)
            for post in posts:
                message= Message(post)
                self.add_message(message)
        self.messages_list.sort(key= lambda m: float(m.get_id()))

    def add_reply(self, reply:Message):
        parent_message = self.find_parent_message(reply)
        if parent_message is not None:
            parent_message.replies.append(reply)

    def find_parent_message(self,reply: Message)-> Message:
        return next((msg for msg in self.messages_list if msg.get_id() == reply.get_thread_id()), None )


    def dump_to_json(self, parent_path:str):
        for message in self.messages_list:
            message_id= message.get_id()
            message.dump_to_json(f'{parent_path}/{message_id}.json')


    async def to_server(self,webhook_url,start=float('-inf'),end=float('inf')):
        webhook= await create_webhook(webhook_url)
        for message in self.messages_list:
            if not message.is_posted() and message.in_date_range(start,end) :
                await message.to_server(webhook)



from core.discord import create_thread, send_webhook, create_webhook