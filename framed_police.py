import os
import time
import discord
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("API_KEY")
client = discord.Client()
# 86400 : 24h
DELAY = 20
LIMIT = 5
OUT_CHANNEL_ID = 873627616064720896
IN_CHANNEL_ID = 873627093840314401


class UserMessage:
    def __init__(self, id, time, count):
        self.id = id
        self.time = time
        self.count = count


messages = []


@client.event
async def on_ready():
    print(f"{client.user} logged in")


@client.event
async def on_message(message):
    if message.channel.id != IN_CHANNEL_ID:
        return
    userId = message.author.id
    print(message.created_at)
    for msg in messages:
        if msg.id == userId:
            endTime = msg.time + DELAY
            print("Current Time:", endTime)
            if time.time() <= endTime:
                if msg.count >= LIMIT:
                    print("Deleted")
                    await client.get_channel(id=OUT_CHANNEL_ID).send(
                        f"Sorry {message.author.mention} but you can't post more than 5 shots per day. {message.created_at}",
                    )
                    await message.delete()
            else:
                msg.time = time.time()
                msg.count = 0
            msg.count += 1
            print(
                f"UserId:{msg.id} Time of first message:{msg.time} Number of messages:{msg.count}"
            )
            return

    messages.append(UserMessage(userId, time.time(), 1))


@client.event
async def on_message_delete(message):
    if message.channel.id != IN_CHANNEL_ID:
        return
    userId = message.author.id
    for msg in messages:
        if msg.id == userId:
            msg.count -= 1


# TODO detect if attachment superior to one to prevent shots posted as one msg
# TODO detect removed posts
client.run(API_KEY)
