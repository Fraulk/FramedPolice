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
DELAY = 43200
LIMIT = 5
OUT_CHANNEL_ID = 697797735381860463
IN_CHANNEL_ID = 549986930071175169


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
        print('ignored')
        return
    #     await DMChannel.send(f"Please do not talk in this channel.")
    #     await message.delete()
    print("Attachment count:", len(attachmentCount))
    print("Embeds count:", len(embeds))
    for msg in usersMessages:
        if msg.id == userId:
            endTime = msg.time + DELAY
            remainingTime = DELAY - (time.time() - msg.time)
            if msg.count == LIMIT - 1: msg.reachedLimit = True
            print("Current Time:", endTime)
            if time.time() <= endTime:
                if msg.count >= LIMIT:
                    print("Deleted")
                    await DMChannel.send(f"Sorry but you can't post more than **{LIMIT}** shots per day.\nThe next time you can post is **{datetime.datetime.fromtimestamp(round(endTime))}** so in **{datetime.timedelta(seconds=round(remainingTime))}**")
                    await message.delete()
            else:
                msg.time = time.time()
                msg.count = 0
            msg.count += 1
            print(
                f"UserId:{msg.id} Time of first message: {msg.time} Number of messages: {msg.count} By: {message.author.name}\n---------------------------------------------------------------------------------------------------------------"
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
    await ctx.send(f"Delay has been changed to {arg}")

@bot.command(name='changeLimit', help='Change the limit for posting shots')
@commands.has_role('Founders Edition')
async def changeLimit(ctx, arg):
    global LIMIT
    LIMIT = int(arg)
    print("Limit has been changed to", arg)
    await ctx.send(f"Limit has been changed to{arg}")

@bot.command(name='currentValue', help='Shows the current values for DELAY and LIMIT')
@commands.has_role('Founders Edition')
async def currentValue(ctx):
    await ctx.send(f"LIMIT = {LIMIT}\nDELAY = {DELAY}")

@bot.command(name='dumpAll', help='Shows data about everybody')
@commands.has_role('Founders Edition')
async def dumpAll(ctx):
    result = ""
    for msg in usersMessages:
        remainingTime = DELAY - (time.time() - msg.time)
        remainingTime = remainingTime if remainingTime >= 0 else 0
        result += f"Name: {msg.name}, Time of first post: {datetime.datetime.fromtimestamp(round(msg.time))}, Remaining time: {datetime.timedelta(seconds=round(remainingTime))}, Shots posted (suppressed ones included): {msg.count}, Has reached the limit: {msg.reachedLimit}\n"
    await ctx.send(result if len(result) > 0 else "No data yet")

@bot.command(name='dumpMe', help='Shows data about you')
async def dumpMe(ctx):
    result = ""
    for msg in usersMessages:
        if msg.id == ctx.author.id:
            remainingTime = DELAY - (time.time() - msg.time)
            remainingTime = remainingTime if remainingTime >= 0 else 0
            result += f"Name: {msg.name}, Time of first post: {datetime.datetime.fromtimestamp(round(msg.time))}, Remaining time: {datetime.timedelta(seconds=round(remainingTime))}, Shots posted (suppressed ones included): {msg.count}, Has reached the limit: {msg.reachedLimit}\n"
    await ctx.send(result if len(result) > 0 else "No data yet")

@bot.command(name='reset', help='Resets the count for a person, with his ID as parameter')
@commands.has_role('Founders Edition')
async def reset(ctx, arg):
    curUser = ""
    global usersMessages
    for msg in usersMessages:
        if msg.id == int(arg):
            msg.count = 0
            msg.reachedLimit = False
            curUser = msg.name
    await ctx.send(f"{curUser} has been reset")

@bot.command(name='resetAll', help='Resets the count for everyone')
@commands.has_role('Founders Edition')
async def resetAll(ctx):
    global usersMessages
    for msg in usersMessages:
        msg.count = 0
        msg.reachedLimit = False
    await ctx.send("Everyone has been reset")

# FIXME : when multiple person spamm shots, sometime the bot ignore the event/code and some shots bypass the limit, it may be caused by the fact that 
# 1. 6th shot get deleted 2. on_message_delete event then decrease user count 3. bot can't keep up so the limit decrease without increasing first or smthng or some events are simply ignored
# embeds are sometimes ignored, so a 6th shot can also bypass
bot.run(API_KEY)
