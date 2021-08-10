import os
import time
import datetime
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("API_KEY")
bot = commands.Bot(command_prefix='!')
# 86400 : 24h
# 43200 : 12h
DELAY = 86400
LIMIT = 5
OUT_CHANNEL_ID = 873627616064720896
IN_CHANNEL_ID = 873627093840314401


class UserMessage:
    def __init__(self, id, name, time, count, reachedLimit):
        self.id = id
        self.name = name
        self.time = time
        self.count = count
        self.reachedLimit = reachedLimit


usersMessages = []

async def checkMessage(message):
    userId = message.author.id
    print(message.created_at)
    embeds = message.embeds
    attachmentCount = message.attachments
    DMChannel = await message.author.create_dm()
    if len(attachmentCount) > 1:
        await DMChannel.send(f"Please post your shots one by one.")
        await message.delete()
    if len(attachmentCount) == 0 and len(embeds) == 0:
        print('came here')
        return
    #     await DMChannel.send(f"Please do not talk in this channel.")
    #     await message.delete()
    print("Attachment count:", len(attachmentCount))
    print("Embeds count:", len(embeds))
    for msg in usersMessages:
        if msg.id == userId:
            endTime = msg.time + DELAY
            remainingTime = DELAY - (time.time() - msg.time)
            print("Current Time:", endTime)
            if time.time() <= endTime:
                if msg.count >= LIMIT:
                    print("Deleted")
                    msg.reachedLimit = True
                    await DMChannel.send(f"Sorry but you can't post more than **{LIMIT}** shots per day.\nThe next time you can post is **{datetime.datetime.fromtimestamp(round(endTime))}** so in **{datetime.timedelta(seconds=round(remainingTime))}**")
                    await message.delete()
            else:
                msg.time = time.time()
                msg.count = 0
            msg.count += 1
            print(
                f"UserId:{msg.id} Time of first message:{msg.time} Number of messages:{msg.count} By: {message.author.name}\n---------------------------------------------------------------------------------------------------------------"
            )
            return
    usersMessages.append(UserMessage(userId, message.author.name + "#" + message.author.discriminator, time.time(), 1, False))


@bot.event
async def on_ready():
    print(f"{bot.user} logged in")


@bot.event
async def on_message(message):
    await bot.process_commands(message)
    if message.channel.id != IN_CHANNEL_ID:
        return
    await checkMessage(message)


@bot.event
async def on_message_delete(message):
    if message.channel.id != IN_CHANNEL_ID:
        return
    userId = message.author.id
    for msg in usersMessages:
        if msg.reachedLimit: return
        if msg.id == userId:
            msg.count -= 1

@bot.command(name='changeDelay', help='Change the delay after reaching the limit for posting shots')
@commands.has_role('Founders Edition')
async def changeDelay(ctx, arg):
    global DELAY
    DELAY = int(arg)
    print("Delay has been changed to", arg)

@bot.command(name='changeLimit', help='Change the limit for posting shots')
@commands.has_role('Founders Edition')
async def changeLimit(ctx, arg):
    global LIMIT
    LIMIT = int(arg)
    print("Limit has been changed to", arg)

@bot.command(name='currentValue', help='Shows the current values for DELAY and LIMIT')
@commands.has_role('Founders Edition')
async def currentValue(ctx):
    await ctx.send(f"LIMIT = {LIMIT}\nDELAY = {DELAY}")

@bot.command(name='dumpAll', help='Shows data about everybody')
@commands.has_role('Founders Edition')
async def currentValue(ctx):
    result = ""
    for msg in usersMessages:
        remainingTime = DELAY - (time.time() - msg.time)
        result += f"Name: {msg.name}, Time of first post: {datetime.datetime.fromtimestamp(round(msg.time))}, Remaining time: {datetime.timedelta(seconds=round(remainingTime))}, Shots posted(suppressed ones included): {msg.count}, Has reached the limit: {msg.reachedLimit}\n"
    await ctx.send(result if len(result) > 0 else "No data yet")

@bot.command(name='dumpMe', help='Shows data about you')
async def currentValue(ctx):
    result = ""
    for msg in usersMessages:
        if msg.id == ctx.author.id:
            remainingTime = DELAY - (time.time() - msg.time)
            result += f"Name: {msg.name}, Time of first post: {datetime.datetime.fromtimestamp(round(msg.time))}, Remaining time: {datetime.timedelta(seconds=round(remainingTime))}, Shots posted(suppressed ones included): {msg.count}, Has reached the limit: {msg.reachedLimit}\n"
    await ctx.send(result if len(result) > 0 else "No data yet")

# FIXME : when multiple person spamm shots, sometime the bot ignore the event/code and some shots bypass the limit, it may be caused by the fact that 
# 1. 6th shot get deleted 2. on_message_delete event then decrease user count 3. bot can't keep up so the limit decrease without increasing first or smthng or some events are simply ignored
bot.run(API_KEY)
