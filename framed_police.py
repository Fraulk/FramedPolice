import os
import re
import time
import datetime
import pickle
import requests
import discord
from discord.ext import commands
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

load_dotenv()
API_KEY = os.getenv("API_KEY")
DB_URL = os.getenv("DB_URL")
cred = credentials.Certificate("./secret.json")
SLapp = firebase_admin.initialize_app(cred, {'databaseURL': DB_URL})
ref = db.reference("/")
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)
PROD = True
# 86400 : 24h
# 43200 : 12h
# Test channel : 873627093840314401
# Framed channel : 549986930071175169
DELAY = 43200
LIMIT = 5
WelcomeRole = 873297069715099721 if PROD else 898969812254990367
PadawanRole = 872825204869582869 if PROD else 899266723906220042
JoinedChannel = 873242046675169310 if PROD else 874368324023255131
LeftChannel = 873242046675169310 if PROD else 874368324023255131
SYSChannel = 549986930071175169 if PROD else 873627093840314401
SLChannel = 859492383845646346 if PROD else 889793521106714634
IntroChannel = 872825951011082291 if PROD else 898977778039390268


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
                    await DMChannel.send(f"Sorry but you can't post more than **{LIMIT}** shots per day.\nThe next time you can post is **<t:{round(endTime)}:F>** so in **{datetime.timedelta(seconds=round(remainingTime))}**")
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

async def secondLook(message):
    userDict = {}
    links = re.findall("(https:\/\/discord.com\/channels\/.*\/.*\d) ", message.content)
    if len(links) == 0: return
    print("---------------------------------------- Building second-look message for " + message.author.name + "#" + message.author.discriminator)
    async with message.channel.typing():
        for link in links:
            slink = link.split("/")
            original_message = await bot.get_guild(int(slink[-3])).get_channel(int(slink[-2])).fetch_message(int(slink[-1]))
            # print(original_message.author.name + "#" + original_message.author.discriminator)
            # print(original_message.attachments[0].url)
            tempDict = {}
            tempDict['name'] = original_message.author.name + "#" + original_message.author.discriminator
            tempDict['imageUrl'] = original_message.attachments[0].url
            tempDict['width'] = original_message.attachments[0].width
            tempDict['height'] = original_message.attachments[0].height
            tempDict['messageUrl'] = link
            userDict[str(original_message.id)] = tempDict
    await bot.get_channel(SLChannel).send(f"Here is your link : https://second-look.netlify.app?id={message.author.id}")
    print("---------------------------------------- Building ended")
    ref.child(str(message.author.id)).set(userDict)

async def getCams(args):
    response = requests.get('https://docs.google.com/spreadsheet/ccc?key=1lnM2SM_RBzqile870zG70E39wuuseqQE0AaPW-P1p5E&output=csv')
    assert response.status_code == 200, 'Wrong status code'
    # print(response.content)
    spreadData = str(response.content).split('\\r\\n')
    spreadData.pop(0)
    matched_lines = []
    line_index = 0
    args = ' '.join(args)
    args = args.replace("'", "\\'")
    for line in spreadData:
        if str(args).lower() in line.lower().split(',')[0]:
            next_index = 1
            if line.find(',') > -1:
                matched_lines += [line]
            if(spreadData[line_index + next_index] == ''): next_index += 1
            while (line_index + next_index < len(spreadData) 
                    and spreadData[line_index + next_index].split(',')[0] == ''):
                if spreadData[line_index + next_index].split(',')[1].startswith('http'):
                    matched_lines += [spreadData[line_index + next_index]]
                next_index += 1
        line_index += 1
    data = ''
    for item in matched_lines:
        line_note = ""
        if item.split(',')[2] != "":
            first_two_length = len(item.split(',')[0]) + len(item.split(',')[1])
            line_note = " *(" + item[item.find('"', first_two_length + 1):-1] + ")*" if '"' in item.split(',')[2] else " *(" + item.split(',')[2] + ")*"
            line_note = line_note.replace("\\n", "\n\t")
            line_note = line_note.replace('"', "")
        if item.split(',')[1].startswith('"'):
            for el in item.split(',')[1].strip('"').split('\\n'):
                data += item.split(',')[0] + " : " + el + line_note + "\n"
            continue
        data += "**" + item.split(',')[0] + "** : <" + item.split(',')[1] + ">" + line_note + "\n" if item.split(',')[0] != "" else "**╘** : <" + item.split(',')[1] + ">" + line_note + "\n"
    return data

async def getUUU(args):
    args = ' '.join(args)
    args = args.replace("'", "\\'")
    response = requests.get('https://framedsc.github.io/GeneralGuides/universal_ue4_consoleunlocker.htm')
    assert response.status_code == 200, 'Wrong status code'
    # print(response.content)
    gamesListPage = re.findall(r'(?s)known to work with the unlocker.*Additionally, mos', str(response.content), flags=re.S | re.M)
    normalizedList = re.sub(r'<code>|<\/code>', '', gamesListPage[0])
    normalizedList = re.sub(r'\\t\\n', '', normalizedList)
    normalizedList = re.sub(r'timestop/pause', 'timestop & pause', normalizedList)
    normalizedList = re.sub(r'Gamepass / MS', 'Gamepass & MS', normalizedList)
    normalizedList = re.sub(r'console/timestop', 'console & timestop', normalizedList)
    games = re.finditer(r'<td>([\(\)&\+\,\.\':-`-\w\s^\\t]*)<\/td>', normalizedList, flags=0)
    gameList = []
    data = ""
    for matchNum, match in enumerate(games, start=1):
        gameList.append(match.group(1))
        arg = args.lower()
    for index, game in enumerate(gameList):
        if arg in game.lower() and index % 2 == 0:
            data += "**" + gameList[index] + "** works with UUU. Notes : " + gameList[index+1] if gameList[index+1] != '' else "**" + gameList[index] + "** works with UUU\n"
    return data

async def getGuides(args):
    args = ' '.join(args)
    args = args.replace("'", "\\'")
    responseAL = requests.get('https://framedsc.github.io/A-L.htm')
    responseMZ = requests.get('https://framedsc.github.io/M-Z.htm')
    assert responseAL.status_code == 200, 'Wrong status code'
    assert responseMZ.status_code == 200, 'Wrong status code'
    responses = str(responseAL.content) + str(responseMZ.content)
    normalizedList = re.sub(r'\\t|\\n|\\r', '\n', responses)
    guides = re.finditer(r'"><a href="(GameGuides\/.*\.htm)">(.*)<\/a>', normalizedList, flags=re.M)
    guideLinks = []
    guideNames = []
    for matchNum, match in enumerate(guides, start=1):
        guideLinks.append(match.group(1))
        guideNames.append(match.group(2))
    arg = args.lower()
    data = ""
    for index, game in enumerate(guideNames):
        if arg in game.lower():
            data += "**" + guideNames[index] + "** : <https://framedsc.github.io/" + guideLinks[index] + ">\n"
    return data

async def getCheats(args):
    args = ' '.join(args)
    # args = args.replace("'", "\\'")
    response = requests.get("https://framedsc.github.io/cheattablearchive.htm", allow_redirects=True)
    assert response.status_code == 200, 'Wrong status code'
    cheats = re.finditer(r'^<h3.*?>(.*?)<.*?<\/ul', response.text, flags=re.S | re.M)
    cheatsName = []
    cheatsContent = []
    data = ""
    for matchNum, match in enumerate(cheats, start=1):
        cheatsName.append(match.group(1))
        cheatsContent.append(match.group(0))
    arg = args.lower()
    for index, cheat in enumerate(cheatsName):
        if arg in cheat.lower():
            if cheat.find("(") > -1:
                cheat = cheat[:-2]
            data += "**" + cheat + "** : "
            cheatsRegex = re.finditer(r'(CheatTables\/Archive\/.*\.(?:CT|ct))">', cheatsContent[index])
            for matchNum2, match2 in enumerate(cheatsRegex, start=1):
                data += "<https://framedsc.github.io/" + match2.group(1) + ">\n" if matchNum2 == 1 else "\t**╘** : <https://framedsc.github.io/" + match2.group(1) + ">\n"
    return data

async def startThread(message):
    title = f"Hello There, {message.author.name}"
    thread = await message.channel.create_thread(name=title, message=message, reason="Thread created for new member")
    await thread.send("https://tenor.com/view/hello-there-general-kenobi-gif-18841535")
    await message.author.remove_roles(message.author.guild.get_role(WelcomeRole))
    await message.author.add_roles(message.author.guild.get_role(PadawanRole))

@bot.event
async def on_ready():
    print(f"{bot.user} logged in")

@bot.event
async def on_message(message):
    await bot.process_commands(message)
    if message.channel.id == SYSChannel:
        await checkMessage(message)
        await save()
    elif message.channel.id == SLChannel:
        await secondLook(message)
    elif message.channel.id == IntroChannel:
        await startThread(message)
    else:
        return

@bot.event
async def on_message_delete(message):
    if message.channel.id != SYSChannel:
        return
    if len(message.attachments) == 0:
        return
    userId = message.author.id
    for msg in usersMessages:
        # if msg.count <= LIMIT: return
        if msg.id == userId:
            # msgCreatedAt = datetime.datetime.timestamp(message.created_at)
            # if msgCreatedAt >= msg.time - (3600 * 2):   # msgCreatedAt is in UTC, but msg.time is in my timezone, so I remove 2 hours to get it to UTC, approximatively
            msg.count -= 1
            print('---------------------------------------- Shots from '+ message.author.name + "#" + message.author.discriminator +' deleted')
            await save()
            # else:
                # print('---------------------------------------- Older shots from '+ message.author.name + "#" + message.author.discriminator +' deleted')

@bot.event
async def on_member_join(member):
    await member.add_roles(member.guild.get_role(WelcomeRole))
    channel = bot.get_channel(JoinedChannel)
    await channel.send(member.mention + " has joined **FRAMED - Screenshot Community**. Welcome!")
    DMChannel = await member.create_dm()
    await DMChannel.send("""Welcome to FRAMED!\n\nNew members are limited to viewing the read-me and introductions channels. Please read through the server rules in the read-me, then let people know a little bit about yourself in the introductions channel. You don't need to say much if you're feeling shy.\n\nOnce you leave a message there, you'll be given access to the rest of the server. Framed is a community first and foremost, we want this to be a place for you to discuss virtual photography and hang out with other members of the hobby. However, if you struggle with that or don't speak English as your primary language, we won't hold that against you. You could start with little things like asking for and giving feedback on shots.\n\nHave fun and enjoy the server :)""")

@bot.event
async def on_member_remove(member):
    channel = bot.get_channel(LeftChannel)
    await channel.send(member.mention + " (" + member.name + ") has left the server")

@bot.command(name='changeDelay', help='Change the delay after reaching the limit for posting shots, with number of seconds')
@commands.has_any_role(549988038516670506, 549988228737007638, 874375168204611604)
async def changeDelay(ctx, arg):
    print(f"'changeDelay' command has been used by {ctx.author.name}#{ctx.author.discriminator}")
    global DELAY
    DELAY = int(arg)
    print("Delay has been changed to", arg)
    await ctx.send(f"Delay has been changed to {arg}")

@bot.command(name='changeLimit', help='Change the limit for posting shots')
@commands.has_any_role(549988038516670506, 549988228737007638, 874375168204611604)
async def changeLimit(ctx, arg):
    print(f"'changeLimit' command has been used by {ctx.author.name}#{ctx.author.discriminator}")
    global LIMIT
    LIMIT = int(arg)
    print("Limit has been changed to", arg)
    await ctx.send(f"Limit has been changed to {arg}")

@bot.command(name='currentValue', help='Shows the current values for DELAY and LIMIT')
@commands.has_any_role(549988038516670506, 549988228737007638, 874375168204611604)
async def currentValue(ctx):
    print(f"'currentValue' command has been used by {ctx.author.name}#{ctx.author.discriminator}")
    await ctx.send(f"LIMIT = {LIMIT}\nDELAY = {DELAY}")

@bot.command(name='dumpR', help='Shows data about those who reached the limit and have been dm\'d by the bot')
@commands.has_any_role(549988038516670506, 549988228737007638, 874375168204611604)
async def dumpR(ctx):
    print(f"'dumpR' command has been used by {ctx.author.name}#{ctx.author.discriminator}")
    result = ""
    i = 0
    sortedResult = sorted(usersMessages, key=lambda x: x.name, reverse=False)
    for msg in sortedResult:
        remainingTime = DELAY - (time.time() - msg.time)
        remainingTime = remainingTime if remainingTime >= 0 else 0
        msgCount = msg.count if remainingTime > 0 else 0
        if msgCount >= LIMIT and remainingTime >= 0:
            i += 1
            msgReachedLimit = msg.reachedLimit if remainingTime > 0 else False
            result += f"**{msg.name}**: Remaining time: **{datetime.timedelta(seconds=round(remainingTime))}**, Shots posted: **{msgCount}**, Has reached the limit: **{msgReachedLimit}**\n"
            if i % 15 == 0:
                await ctx.send(result if len(result) > 0 else "No data yet")
                result = ""
    await ctx.send(result if len(result) > 0 else "No data yet") # did i forgot to remove this ?

@bot.command(name='dump', help='Shows data about everybody')
@commands.has_any_role(549988038516670506, 549988228737007638, 874375168204611604)
async def dump(ctx):
    print(f"'dump' command has been used by {ctx.author.name}#{ctx.author.discriminator}")
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
@commands.has_any_role(549988038516670506, 549988228737007638, 874375168204611604)
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
    print(f"'reset' command has been used by {ctx.author.name}#{ctx.author.discriminator}")
    await ctx.send(response)

@bot.command(name='resetAll', help='Resets the count for everyone')
@commands.has_any_role(549988038516670506, 549988228737007638, 874375168204611604)
async def resetAll(ctx):
    global usersMessages
    for msg in usersMessages:
        msg.count = 0
        msg.reachedLimit = False
    await save()
    print(f"'resetAll' command has been used by {ctx.author.name}#{ctx.author.discriminator}")
    await ctx.send("Everyone has been reset")

@bot.command(name='cam', help='Search for a freecams or a tool by string. ex: !cam cyberpunk 2077')
async def cam(ctx, *args):
    async with ctx.typing():
        data = await getCams(args)
        if len(data) == 0: data = "Not Found"
        e = discord.Embed(title="Freecams, tools and stuff",
                          url="https://docs.google.com/spreadsheets/d/1lnM2SM_RBzqile870zG70E39wuuseqQE0AaPW-P1p5E/edit#gid=0",
                          description="Based on originalnicodr spreadsheet",
                          color=0x3498DB)
        e.set_thumbnail(url="https://cdn.discordapp.com/avatars/128245457141891072/0ab765d7c5bd8fb373dbd3627796aeec.png?size=128")
    await ctx.send(content=data, embed=e) if len(data) < 2000 else await ctx.send("Search query is too vague, there are too many results to show")

@bot.command(name='uuu', help='Checks if a game is compatible with UUU or have a guide on the site. ex: !uuu the ascent')
async def uuu(ctx, *args):
    async with ctx.typing():
        data = await getUUU(args)
        if len(data) == 0: data = "Not Found"
        e = discord.Embed(title="FRAMED. Screenshot Community",
                          url="https://framedsc.github.io/index.htm",
                          description="© 2019-2021 FRAMED. All rights reserved. ",
                          color=0x9a9a9a)
        e.set_thumbnail(url="https://cdn.discordapp.com/emojis/575642684006334464.png?size=80")
    await ctx.send(content=data, embed=e) if len(data) < 2000 else await ctx.send("Search query is too vague, there are too many results to show")

@bot.command(name='guide', help='Checks if a game have a guide on the site. ex: !guide cyberpunk')
async def guide(ctx, *args):
    async with ctx.typing():
        data = await getGuides(args)
        if len(data) == 0: data = "Not Found"
        e = discord.Embed(title="FRAMED. Screenshot Community",
                          url="https://framedsc.github.io/index.htm",
                          description="© 2019-2021 FRAMED. All rights reserved. ",
                          color=0x9a9a9a)
        e.set_thumbnail(url="https://cdn.discordapp.com/emojis/575642684006334464.png?size=80")
    await ctx.send(content=data, embed=e) if len(data) < 2000 else await ctx.send("Search query is too vague, there are too many results to show")

@bot.command(name='cheat', help='Checks if a game have cheat tables on the site. ex: !cheat alien')
async def cheat(ctx, *args):
    async with ctx.typing():
        data = await getCheats(args)
        if len(data) == 0: data = "Not Found"
        e = discord.Embed(title="FRAMED. Screenshot Community",
                          url="https://framedsc.github.io/index.htm",
                          description="© 2019-2021 FRAMED. All rights reserved. ",
                          color=0x9a9a9a)
        e.set_thumbnail(url="https://cdn.discordapp.com/emojis/575642684006334464.png?size=80")
    await ctx.send(content=data, embed=e) if len(data) < 2000 else await ctx.send("Search query is too vague, there are too many results to show")

@bot.command(name='tool', help='Checks if a game have a guide, cam or works with UUU. ex: !tool cyberpunk')
async def tool(ctx, *args):
    async with ctx.typing():
        cams = await getCams(args)
        uuus = await getUUU(args)
        guides = await getGuides(args)
        cheats = await getCheats(args)
        data = ""
        if len(cams) > 0:
            data += cams + "----\n" if len(uuus) > 0 or len(guides) > 0 or len(cheats) > 0 else cams
        if len(uuus) > 0:
            data += uuus + "----\n" if len(guides) > 0 or len(cheats) > 0 else uuus
        if len(guides) > 0:
            data += guides + "----\n" if len(cheats) > 0 else guides
        if len(cheats) > 0:
            data += cheats
        if len(data) == 0: data = "Not Found"
        # e = discord.Embed(title="FRAMED. Screenshot Community",
        #                   url="https://framedsc.github.io/index.htm",
        #                   description="© 2019-2021 FRAMED. All rights reserved. ",
        #                   color=0x9a9a9a)
        # e.set_thumbnail(url="https://cdn.discordapp.com/emojis/575642684006334464.png?size=80")
    await ctx.send(content=data) if len(data) < 2000 else await ctx.send("Search query is too vague, there are too many results to show") # + str(len(data))

# BUG : when multiple person spamm shots, sometime the bot ignore the event/code and some shots bypass the limit, it may be caused by the fact that 
# 1. 6th shot get deleted 2. on_message_delete event then decrease user count 3. bot can't keep up so the limit decrease without increasing first or smthng or some events are simply ignored
# embeds are sometimes ignored, so a 6th shot can also bypass
# TODO : also jim said it wasn't necessary but since you said you're bored maybe a counter of shots in share-your-shot and hall-of-framed then every weekend it posts a summary of the week's numbers or something
# https://stackoverflow.com/questions/65765951/discord-python-counting-messages-from-a-week-and-save-them
# FIXME : "older shot" triggered false positive, f
# TODO : i should limit the character to 3 min in cam and uuu commands
# TODO : create a !cheat commands that gets cheat table from framed site
# TODO : put things in embeds : https://leovoel.github.io/embed-visualizer/
# FIXME : catch commands used without arguments
# FIXME : remove spaces from links, test with cyberpunk

if os.path.isfile('./messages.pkl'):
    with open('messages.pkl', 'rb') as f:
        usersMessages = pickle.load(f)
else:
    with open('messages.pkl', 'wb'): pass

bot.run(API_KEY)
