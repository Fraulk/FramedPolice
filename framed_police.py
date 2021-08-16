import os
import time
import datetime
import pickle
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("API_KEY")
bot = commands.Bot(command_prefix='!')
# 86400 : 24h
# 43200 : 12h
# Test channel : 873627093840314401
# Framed channel : 549986930071175169
DELAY = 86400
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
                msg.reachedLimit = False
            msg.count += 1
            print(
                f"UserId:{msg.id} Time of first message: {msg.time} Number of messages: {msg.count} By: {msg.name}\n---------------------------------------------------------------------------------------------------------------"
            )
            return
    usersMessages.append(UserMessage(userId, message.author.name + "#" + message.author.discriminator, time.time(), 1, False))
    print(f"UserId:{userId} Time of first message: {time.time()} Number of messages: {1} By: {message.author.name}#{message.author.discriminator}\n---------------------------------------------------------------------------------------------------------------")
    
async def save():
    with open('messages.pkl', 'wb') as f:
        pickle.dump(usersMessages, f)

@bot.event
async def on_ready():
    print(f"{bot.user} logged in")


@bot.event
async def on_message(message):
    await bot.process_commands(message)
    if message.channel.id != IN_CHANNEL_ID:
        return
    await checkMessage(message)
    await save()


@bot.event
async def on_message_delete(message):
    if message.channel.id != IN_CHANNEL_ID:
        return
    userId = message.author.id
    for msg in usersMessages:
        if msg.reachedLimit: return
        if msg.id == userId:
            msg.count -= 1
            await save()

@bot.command(name='changeDelay', help='Change the delay after reaching the limit for posting shots')
@commands.has_any_role(549988038516670506, 549988228737007638)
async def changeDelay(ctx, arg):
    global DELAY
    DELAY = int(arg)
    print("Delay has been changed to", arg)
    await ctx.send(f"Delay has been changed to {arg}")

@bot.command(name='changeLimit', help='Change the limit for posting shots')
@commands.has_any_role(549988038516670506, 549988228737007638)
async def changeLimit(ctx, arg):
    global LIMIT
    LIMIT = int(arg)
    print("Limit has been changed to", arg)
    await ctx.send(f"Limit has been changed to {arg}")

@bot.command(name='currentValue', help='Shows the current values for DELAY and LIMIT')
@commands.has_any_role(549988038516670506, 549988228737007638)
async def currentValue(ctx):
    await ctx.send(f"LIMIT = {LIMIT}\nDELAY = {DELAY}")

@bot.command(name='dump', help='Shows data about everybody')
@commands.has_any_role(549988038516670506, 549988228737007638)
async def dump(ctx):
    result = ""
    i = 0
    sortedResult = sorted(usersMessages, key=lambda x: x.name, reverse=False)
    for msg in sortedResult:
        remainingTime = DELAY - (time.time() - msg.time)
        remainingTime = remainingTime if remainingTime >= 0 else 0
        msgCount = msg.count if remainingTime > 0 else 0
        if msgCount > 0 and remainingTime >= 0:
            i += 1
            msgReachedLimit = msg.reachedLimit if remainingTime > 0 else False
            result += f"**{msg.name}**: Remaining time: **{datetime.timedelta(seconds=round(remainingTime))}**, Shots posted: **{msgCount}**, Has reached the limit: **{msgReachedLimit}**\n"
            if i % 15 == 0:
                await ctx.send(result if len(result) > 0 else "No data yet")
                result = ""
    await ctx.send(result if len(result) > 0 else "No data yet") # did i forgot to remove this ?

@bot.command(name='check', help='Shows data about you')
async def check(ctx):
    result = ""
    for msg in usersMessages:
        if msg.id == ctx.author.id and msg.count > 0:
            remainingTime = DELAY - (time.time() - msg.time)
            remainingTime = remainingTime if remainingTime >= 0 else 0
            msgCount = msg.count if msg.count < LIMIT else LIMIT
            msgCount = msgCount if remainingTime > 0 else 0
            msgReachedLimit = msg.reachedLimit if remainingTime > 0 else False
            result += f"**{msg.name}**: Remaining time: **{datetime.timedelta(seconds=round(remainingTime))}**, Shots posted: **{msgCount}**, Has reached the limit: **{msgReachedLimit}**\n"
    await ctx.send(result if len(result) > 0 else "No data yet")

@bot.command(name='reset', help='Resets the count for a person, with his ID as parameter')
@commands.has_any_role(549988038516670506, 549988228737007638)
async def reset(ctx, arg):
    curUser = ""
    response = ""
    global usersMessages
    for msg in usersMessages:
        if msg.id == int(arg):
            msg.count = 0
            msg.reachedLimit = False
            curUser = msg.name
    if curUser == "":
        response = "This user either don't exists or didn't posted anything yet"
    else:
        response = f"{curUser} has been reset"
        await save()
    await ctx.send(response)

@bot.command(name='resetAll', help='Resets the count for everyone')
@commands.has_any_role(549988038516670506, 549988228737007638)
async def resetAll(ctx):
    global usersMessages
    for msg in usersMessages:
        msg.count = 0
        msg.reachedLimit = False
    await save()
    await ctx.send("Everyone has been reset")

# FIXME : when multiple person spamm shots, sometime the bot ignore the event/code and some shots bypass the limit, it may be caused by the fact that 
# 1. 6th shot get deleted 2. on_message_delete event then decrease user count 3. bot can't keep up so the limit decrease without increasing first or smthng or some events are simply ignored
# embeds are sometimes ignored, so a 6th shot can also bypass

if os.path.isfile('./messages.pkl'):
    with open('messages.pkl', 'rb') as f:
        usersMessages = pickle.load(f)
else:
    with open('messages.pkl', 'wb'): pass

bot.run(API_KEY)
