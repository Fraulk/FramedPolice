import re
import random
import discord
from discord.ext import commands
from discord.ext.commands import Bot
import requests
from PIL import Image, ImageDraw
from discord.ui import button, View, Button, view
from discord.interactions import Interaction

from vars import *

# bot = commands.Bot(command_prefix='')

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
    gameNames = []
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
        gameNames.append(item.split(',')[0])
    gameNames[:] = ["**" + x + "**" for x in gameNames if x]
    return data, gameNames

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
    gameNames = []
    for matchNum, match in enumerate(games, start=1):
        gameList.append(match.group(1))
        arg = args.lower()
    for index, game in enumerate(gameList):
        if arg in game.lower() and index % 2 == 0:
            data += "**" + gameList[index] + "** works with UUU. Notes : " + gameList[index+1] + "\n" if gameList[index+1] != '' else "**" + gameList[index] + "** works with UUU\n"
            gameNames.append("**" + gameList[index] + "**")
    return data, gameNames

async def getGuides(args):
    args = ' '.join(args)
    args = args.replace("'", "\\'")
    responseAL = requests.get('https://framedsc.github.io/A-L.htm')
    responseMZ = requests.get('https://framedsc.github.io/M-Z.htm')
    responseGeneralGuides = requests.get('https://framedsc.github.io/GeneralGuides/index.htm')
    responseGeneralGuidesAdv = requests.get('https://framedsc.github.io/GeneralGuidesAdvanced.htm')
    responseReshadeGuides = requests.get('https://framedsc.github.io/ReshadeGuides/index.htm')
    responseReshadeShaderGuides = requests.get('https://framedsc.github.io/ReshadeGuidesShaderguides.htm')
    assert responseAL.status_code == 200, 'Wrong status code'
    assert responseMZ.status_code == 200, 'Wrong status code'
    assert responseGeneralGuides.status_code == 200, 'Wrong status code'
    assert responseGeneralGuidesAdv.status_code == 200, 'Wrong status code'
    assert responseReshadeGuides.status_code == 200, 'Wrong status code'
    assert responseReshadeShaderGuides.status_code == 200, 'Wrong status code'
    responses = str(responseAL.content)
    responses += str(responseMZ.content)
    responses += str(responseGeneralGuides.content)
    responses += str(responseGeneralGuidesAdv.content)
    responses += str(responseReshadeGuides.content)
    responses += str(responseReshadeShaderGuides.content)
    normalizedList = re.sub(r'\\t|\\n|\\r', '\n', responses)
    guidesRegex = r'"><a href="(GameGuides\/.*\.htm|..\/ReshadeGuides\/.*\.htm|..\/GeneralGuides\/.*\.htm|ReshadeGuides\/Shaders\/.*\.htm)">(.*)<\/a>'
    guides = re.finditer(guidesRegex, normalizedList, flags=re.M)
    guideLinks = []
    guideNames = []
    for matchNum, match in enumerate(guides, start=1):
        guideLinks.append(match.group(1))
        guideNames.append(match.group(2))
    arg = args.lower()
    data = ""
    gameNames = []
    for index, game in enumerate(guideNames):
        if arg in game.lower():
            data += "**" + guideNames[index] + "** : <https://framedsc.github.io/" + guideLinks[index] + ">\n"
            gameNames.append("**" + guideNames[index] + "**")
    return data, gameNames

async def getCheats(args):
    args = ' '.join(args)
    # args = args.replace("'", "\\'")
    response = requests.get("https://framedsc.github.io/cheattablearchive.htm", allow_redirects=True)
    assert response.status_code == 200, 'Wrong status code'
    cheats = re.finditer(r'^<h3.*?>(.*?)<.*?<\/ul', response.text, flags=re.S | re.M)
    cheatsName = []
    cheatsContent = []
    data = ""
    gameNames = []
    for matchNum, match in enumerate(cheats, start=1):
        cheatsName.append(match.group(1))
        cheatsContent.append(match.group(0))
    arg = args.lower()
    for index, cheat in enumerate(cheatsName):
        if arg in cheat.lower():
            if cheat.find("(") > -1:
                cheat = cheat[:-2]
            data += "**" + cheat + "** : "
            gameNames.append("**" + cheat + "**")
            cheatsRegex = re.finditer(r'(CheatTables\/Archive\/.*\.(?:CT|ct))">', cheatsContent[index])
            for matchNum2, match2 in enumerate(cheatsRegex, start=1):
                data += "<https://framedsc.github.io/" + match2.group(1) + ">\n" if matchNum2 == 1 else "\t**╘** : <https://framedsc.github.io/" + match2.group(1) + ">\n"
    return data, gameNames

async def startThread(message):
    title = f"Hello There, {message.author.name}"
    thread = await message.channel.create_thread(name=title, message=message, reason="Thread created for new member")
    await thread.send("https://tenor.com/view/hello-there-general-kenobi-gif-18841535")
    await message.author.remove_roles(message.author.guild.get_role(WelcomeRole))
    await message.author.add_roles(message.author.guild.get_role(PadawanRole))

async def over2000(data, gameNames, query):
    isOver2000 = len(data) > 2000
    if(isOver2000):
        # response = "Search query is too vague, there are too many results to show.\n" + str(len(gameNames)) + " games corresponds to your query, please retype the command with one of them : \n"
        response = random.choice(tooVague).format(' '.join(query))
        response += "  |  ".join([name for name in gameNames])
        if(len(gameNames) > 15):
            response = "I found too many results for `{}` ! Please be more specific !".format(' '.join(query))
        return response
    return data

async def react(message, reason, botAvatar):
    percentage = 2 if reason == "bad" else 5 if reason == "good" else 6 if reason == "horny" else 2
    if random.randint(0, 9) < percentage:
        gifs = badGifs if reason == "bad" else goodGifs if reason == "good" else hornyGifs
        await message.reply(random.choice(gifs))
    else:
        badGuy = requests.get(message.author.avatar, stream=True).raw
        botPfp = requests.get(botAvatar, stream=True).raw
        botImg = badBot if reason == "bad" else goodBot if reason == "good" else hornyBot
        memePath, memeInfo = random.choice(list(botImg.items()))
        meme = Image.open('images/' + memePath + '.jpg').convert('RGB')
        botImg = Image.open(botPfp)
        botImg.thumbnail(memeInfo['size'], Image.ANTIALIAS)
        badGuy = Image.open(badGuy)
        badGuy.thumbnail(memeInfo['size'], Image.ANTIALIAS)
        memeCopy = meme.copy()
        memeCopy.paste(botImg, memeInfo['botPosition'])
        memeCopy.paste(badGuy, memeInfo['badPosition'])
        memeCopy.save('./temp.jpg', quality=95)
        await message.reply(file=discord.File('temp.jpg'))

class BingoPoints:
    def __init__(self, id, name) -> None:
        self.id = id
        self.name = name
        # self.pointMap = pointMap

def crossBingo(caseX, caseY, reset, avatar = None):
    caseSize = 285
    X, Y = (119, 260)
    X += caseSize * caseX
    Y += caseSize * caseY
    if avatar == None:
        botPfp = requests.get("https://cdn.discordapp.com/avatars/873628046194778123/bb780540a15f10e3c5250a8e6c77dd1e.webp?size=240", stream=True).raw
    else:
        botPfp = requests.get(avatar, stream=True).raw
    bingo = Image.open('images/bingo.png') if reset == True else Image.open('./tempBingo.png')
    botImg = Image.open(botPfp)
    botMask = Image.new("L", botImg.size, 0)
    draw = ImageDraw.Draw(botMask)
    draw.ellipse((0, 0, 240, 240), fill=120)
    botImg.putalpha(botMask)
    bingoCopy = bingo.copy()
    try:
        bingoCopy.paste(botImg, (X, Y), botImg) # (119, 260)
    except ValueError:
        botPfp = requests.get("https://cdn.discordapp.com/avatars/873628046194778123/bb780540a15f10e3c5250a8e6c77dd1e.webp?size=240", stream=True).raw
        botImg = Image.open(botPfp)
        botMask = Image.new("L", botImg.size, 0)
        draw = ImageDraw.Draw(botMask)
        draw.ellipse((0, 0, 240, 240), fill=120)
        botImg.putalpha(botMask)
        bingoCopy.paste(botImg, (X, Y), botImg)
    bingoCopy.save('./tempBingo.png', quality=95)

def recreateBingo(bingo):
    for i in range(len(bingo)):
        for j in range(len(bingo[i])):
            if bingo[i][j] == 1:
                crossBingo(i, j, False)
