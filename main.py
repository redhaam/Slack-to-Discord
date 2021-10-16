import asyncio
from core.utils import  date_to_timestamp
from core.message import  Messages_List
from core.config import load_config,load_from_env




if __name__ =="__main__":
    messages = Messages_List()
    config= load_config()
    channel=config.channel
    messages.load_messages_list(channel)
    webhook_url=load_from_env("WEBHOOK_URL")
    start_date_ts= date_to_timestamp(config.START_DATE)
    end_date_ts= date_to_timestamp(config.END_DATE)
    asyncio.run(messages.to_server(webhook_url,start_date_ts,end_date_ts))