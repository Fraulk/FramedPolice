import re
import time
import json
import pickle
import random
import discord
import datetime
from discord.ext import commands
from discord.ext.commands import Bot
import requests
from PIL import Image, ImageDraw
from discord.ui import button, View, Button, view
from discord.interactions import Interaction

from vars import *

# bot = commands.Bot(command_prefix='')

usersMessages = []

class UserMessage:
    def __init__(self, id, name, time, count, reachedLimit):
        self.id = id
        self.name = name
        self.time = time
        self.count = count
        self.reachedLimit = reachedLimit

async def checkMessage(message):
    userId = message.author.id
    print(message.created_at)
    embeds = message.embeds
    attachmentCount = message.attachments
    DMChannel = await message.author.create_dm()
    # if message.content != '':
    #     rightTitle = next((i for i, item in enumerate(titleAlts) if message.content in next(iter(item))), None)
    #     if rightTitle is None:
    #         altTitle = next((i for i, item in enumerate(titleAlts) if message.content in item[next(iter(item))]), None)
    #         if altTitle is None:
    #             # await DMChannel.send("It looks like the name of that game isn't registered on my database, could you ask to one of the moderator to add it please")
    #             pass
    #         else:
    #             goodTitle = next(iter(titleAlts[altTitle]))
    #             await DMChannel.send(f"The name you used isn't very clear, could you rename it with : **{goodTitle}**")
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

def saveBingo():
    with open('bingo.pkl', 'wb') as f:
        pickle.dump(emptyBingo, f)

def saveTitleAlts():
    with open('titleAlts.pkl', 'wb') as f:
        pickle.dump(titleAlts, f)

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

async def secondLook(message):
    userDict = {}
    links = re.findall("(https:\/\/discord.com\/channels\/.*\/.*\d)(?:| )", message.content)
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

async def loadImagesFromHOF(msg, channel):
    async with channel.typing():
        epoch = re.findall(r"https:\/\/framedsc\.com\/HallOfFramed\/\?imageId=(\d*)", msg)
        shotsDb = requests.get('https://raw.githubusercontent.com/originalnicodrgitbot/hall-of-framed-db/main/shotsdb.json')
        assert shotsDb.status_code == 200, 'Wrong status code'
        shotsDict = json.loads(shotsDb.content)
        foundShot = []
        for shot in shotsDict["_default"].values():
            for epch in epoch:
                if str(epch) == str(shot["epochTime"]):
                    foundShot.append(shot)
        messageContent = ""
        for fShot in foundShot:
            messageContent += f"{fShot['shotUrl']}\n"
    await channel.send(messageContent)

class BingoPoints:
    def __init__(self, id, name) -> None:
        self.id = id
        self.name = name
        # self.pointMap = pointMap

class EphemeralBingo(View):

    def __init__(self, ctx, timeout = None):
        super().__init__(timeout=timeout)
        self.chanId = ctx.channel.id
        
    @discord.ui.button(label='Check', style=discord.ButtonStyle.blurple)
    async def checkCompact(self, button: discord.ui.Button, interaction: discord.Interaction):
        try:
            padawan = interaction.user.guild.get_role(PadawanRole)
        except AttributeError:
            await interaction.response.send_message("Sorry but you can only play bingo in the Framed server", ephemeral=True)
            return
        if padawan is None:
            await interaction.response.send_message("Sorry but you can only play bingo in the Framed server", ephemeral=True)
        else:
            if padawan in interaction.user.roles:
                await interaction.response.send_message("Sorry! Members with padawan role aren't currently eligible to play the bingo right now.", ephemeral=True)
            else:
                await interaction.response.send_message("Choose a box", view=BingoView(params={'compact': True, 'user': interaction.user, 'channel': self.chanId}), ephemeral=True)

class BingoView(View):

    def __init__(self, params, timeout = None):
        super().__init__(timeout=timeout)
        if not params.get('compact'): params['compact'] = False
        self.user = params['user']
        self.channel = params['channel']
        self.board = self.getScore()
        for x in range(5):
            for y in range(5):
                if params['compact']: self.add_item(BingoViewButton(x, y, f"{x+1}-{y+1}", self.board, self.user.avatar))
                if not params['compact']: self.add_item(BingoViewButton(x, y, bingoText[y][x], self.board, self.user.avatar))

    def getScore(self):
        # for bp in bingoPoints:
        #     if bp.id == self.user.id:
        #         return bp.pointMap
        # bingoPoints.append(BingoPoints(self.user.id, self.user.name))
        return emptyBingo

    def setScore(self, x, y):
        print(f"{self.user.name} checked the {x+1}-{y+1} case")
        emptyBingo[x][y] = 1
        for bp in bingoPoints:
            if bp.id == self.user.id:
                # bp.pointMap[x][y] = 1
                return True
        bingoPoints.append(BingoPoints(self.user.id, self.user.name))

    def checkWinner(self):
        for horizontal in self.board:
            value = sum(horizontal)
            if value == 5:
                return self.user
        for vertical in range(5):
            value = self.board[0][vertical] + self.board[1][vertical] + self.board[2][vertical] + self.board[3][vertical] + self.board[4][vertical]
            if value == 5:
                return self.user
        diagBLTR = self.board[0][4] + self.board[1][3] + self.board[2][2] + self.board[3][1] + self.board[4][0]
        if diagBLTR == 5:
            return self.user
        diagTLBR = self.board[0][0] + self.board[1][1] + self.board[2][2] + self.board[3][3] + self.board[4][4]
        if diagTLBR == 5:
            return self.user
        return None
    # https://github.com/Rapptz/discord.py/blob/45d498c1b76deaf3b394d17ccf56112fa691d160/examples/views/tic_tac_toe.py

class BingoViewButton(Button):
    def __init__(self, x, y, label, board, avatar):
        if board[x][y] == 1:
            super().__init__(label=label, style=discord.ButtonStyle.success, disabled=True, row=y)
        if board[x][y] == 0:
            super().__init__(label=label, style=discord.ButtonStyle.secondary, row=y)
        self.x = x
        self.y = y
        self.label = label if label != "3-3" else "Free"
        self.avatar = avatar
    
    async def callback(self, interaction: discord.Interaction):
        assert self.view is not None
        view = self.view
        view.setScore(self.x, self.y)
        userAvatar = self.avatar.with_size(256) if self.avatar != None else None
        saveBingo()
        crossBingo(self.x, self.y, False, userAvatar)

        self.style = discord.ButtonStyle.success
        self.disabled = True
        for child in view.children:
            child.disabled = True
        await interaction.response.edit_message(view=view)

        winner = view.checkWinner()
        if winner is not None:
            bot.dispatch("bingo_winner", view.user, view.channel)

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

def resetBingoBoard():
    bingoPoints.clear()
    global emptyBingo
    emptyBingo = [[0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0]]
    crossBingo(-2, -1, True)

class Confirm(View):
    def __init__(self, players: list[str], customEmoji = None):
        super().__init__()
        self.connect4 = [
            [-1, -1, -1, -1, -1, -1, -1],
            [-1, -1, -1, -1, -1, -1, -1],
            [-1, -1, -1, -1, -1, -1, -1],
            [-1, -1, -1, -1, -1, -1, -1],
            [-1, -1, -1, -1, -1, -1, -1],
            [-1, -1, -1, -1, -1, -1, -1],
        ]
        self.players = players
        self.emoji = customEmoji

    # When the confirm button is pressed, set the inner value to `True` and
    # stop the View from listening to more input.
    # We also send the user an ephemeral message that we're confirming their choice.
    @discord.ui.button(label='Confirm', style=discord.ButtonStyle.green)
    async def confirm(self, button: discord.ui.Button, interaction: discord.Interaction):
        if interaction.user.id == self.players[1]:
            await interaction.response.edit_message(content=toDiscordString(self.connect4, 3, self.players[1], 1, customEmoji=self.emoji), view=Connect4(self.connect4, players=self.players, customEmoji=self.emoji))
            self.stop()
        else:
            await interaction.response.edit_message(content=f"<@{self.players[0]}> wants to play connect4 with you <@{self.players[1]}>, will you accept ? PS: Only the mentionned person can respond")

    # This one is similar to the confirmation button except sets the inner value to `False`
    @discord.ui.button(label='Cancel', style=discord.ButtonStyle.grey)
    async def cancel(self, button: discord.ui.Button, interaction: discord.Interaction):
        if interaction.user.id == self.players[1]:
            button.disabled = True
            for child in self.children:
                child.disabled = True
            await interaction.response.edit_message(content='Sorry, but the offer got rejected', view=self)
            self.stop()
        else:
            await interaction.response.edit_message(content=f"<@{self.players[0]}> wants to play connect4 with you <@{self.players[1]}>, will you accept ? PS: Only the mentionned person can respond")

class Connect4(View):
    def __init__(self, board, players: list[str], customEmoji = None):
        super().__init__()
        self.cursor = 3
        self.c4Board = board
        self.emoji = customEmoji
        self.players = players
        self.turns = 2
        self.playerTurn = 1
        self.blockedCol = False
        self.replay = []

    def addTurn(self):
        self.playerTurn = self.turns % 2
        self.turns += 1

    def checkConnect4Winner(self, player):
        for y in range(len(self.c4Board)):
            for x in range(len(self.c4Board[y])):
                # having an negative index doesn't give an indexError but check from the list's end, but an index superior to the list's length throw an exception, so first check is
                # ifx or y superior to their max length and checking at the end if they're negative
                try:
                    if x + 3 < 7 and self.c4Board[y][x] == player and self.c4Board[y][x + 1] == player and self.c4Board[y][x + 2] == player and self.c4Board[y][x + 3] == player:
                        self.markWinningBoard([[y, x], [y, x + 1], [y, x + 2], [y, x + 3]], player)
                        return True
                    if x + 3 < 7 and y + 3 < 6 and self.c4Board[y][x] == player and self.c4Board[y + 1][x + 1] == player and self.c4Board[y + 2][x + 2] == player and self.c4Board[y + 3][x + 3] == player:
                        self.markWinningBoard([[y, x], [y + 1, x + 1], [y + 2, x + 2], [y + 3, x + 3]], player)
                        return True
                    if y + 3 < 6 and self.c4Board[y][x] == player and self.c4Board[y + 1][x] == player and self.c4Board[y + 2][x] == player and self.c4Board[y + 3][x] == player:
                        self.markWinningBoard([[y, x], [y + 1, x], [y + 2, x], [y + 3, x]], player)
                        return True
                    if y + 3 < 6 and self.c4Board[y][x] == player and self.c4Board[y + 1][x - 1] == player and self.c4Board[y + 2][x - 2] == player and self.c4Board[y + 3][x - 3] == player and x - 3 > -1:
                        self.markWinningBoard([[y, x], [y + 1, x - 1], [y + 2, x - 2], [y + 3, x - 3]], player)
                        return True
                    if self.c4Board[y][x] == player and self.c4Board[y][x - 1] == player and self.c4Board[y][x - 2] == player and self.c4Board[y][x - 3] == player and x - 3 > -1:
                        self.markWinningBoard([[y, x], [y, x - 1], [y, x - 2], [y, x - 3]], player)
                        return True
                    if self.c4Board[y][x] == player and self.c4Board[y - 1][x - 1] == player and self.c4Board[y - 2][x - 2] == player and self.c4Board[y - 3][x - 3] == player and x - 3 > -1 and y - 3 > -1:
                        self.markWinningBoard([[y, x], [y - 1, x - 1], [y - 2, x - 2], [y - 3, x - 3]], player)
                        return True
                    if self.c4Board[y][x] == player and self.c4Board[y - 1][x] == player and self.c4Board[y - 2][x] == player and self.c4Board[y - 3][x] == player and y - 3 > -1:
                        self.markWinningBoard([[y, x], [y - 1, x], [y - 2, x], [y - 3, x]], player)
                        return True
                    if x + 3 < 7 and self.c4Board[y][x] == player and self.c4Board[y - 1][x + 1] == player and self.c4Board[y - 2][x + 2] == player and self.c4Board[y - 3][x + 3] == player and y - 3 > -1:
                        self.markWinningBoard([[y, x], [y - 1, x + 1], [y - 2, x + 2], [y - 3, x + 3]], player)
                        return True
                except IndexError:
                    print("got an indexError on", x, y)
                    continue
        return False

    def checkTie(self):
        for y in self.c4Board:
            tie = all(dot != -1 for dot in y)
            if not tie: return False
        return tie

    def markWinningBoard(self, dots: list[list], player):
        for dot in dots:
            self.c4Board[dot[0]][dot[1]] = 2 if player == 0 else 3

    @discord.ui.button(label='', style=discord.ButtonStyle.gray, emoji="⏪")
    async def maxLeft(self, button: discord.ui.Button, interaction: discord.Interaction):
        if interaction.user.id == self.players[self.playerTurn]:
            if self.children[2].disabled: self.children[2].disabled = False
            self.cursor = 0
            self.replay.append("maxLeft")
            if self.c4Board[5][self.cursor] != -1:
                self.children[2].disabled = True
            await interaction.response.edit_message(content=toDiscordString(self.c4Board, self.cursor, self.players[self.playerTurn], self.playerTurn, customEmoji=self.emoji), view=self)

    @discord.ui.button(label='', style=discord.ButtonStyle.gray, emoji="◀️")
    async def left(self, button: discord.ui.Button, interaction: discord.Interaction):
        if interaction.user.id == self.players[self.playerTurn]:
            if self.children[2].disabled: self.children[2].disabled = False
            self.cursor -= 1 if self.cursor > 0 else 0
            self.replay.append("left")
            if self.c4Board[5][self.cursor] != -1:
                self.children[2].disabled = True
            await interaction.response.edit_message(content=toDiscordString(self.c4Board, self.cursor, self.players[self.playerTurn], self.playerTurn, customEmoji=self.emoji), view=self)

    @discord.ui.button(label='', style=discord.ButtonStyle.blurple, emoji="🔽")
    async def add(self, button: discord.ui.Button, interaction: discord.Interaction):
        if interaction.user.id == self.players[self.playerTurn]:
            if self.children[2].disabled: self.children[2].disabled = False
            self.addTurn()
            self.c4Board = addToken(self.c4Board, self.cursor, self.playerTurn)
            hasWin = self.checkConnect4Winner(self.playerTurn)
            tie = self.checkTie()
            if not hasWin and not tie:
                if self.c4Board[5][self.cursor] != -1:
                    self.children[2].disabled = True
                self.replay.append("add")
                await interaction.response.edit_message(content=toDiscordString(self.c4Board, self.cursor, self.players[self.playerTurn], self.playerTurn, customEmoji=self.emoji), view=self)
            else:
                self.playerTurn = not self.playerTurn
                for child in self.children:
                    child.disabled = True
                self.replay.append("add")
                await interaction.response.edit_message(content=toDiscordString(self.c4Board, self.cursor, self.players[self.playerTurn], self.playerTurn, customEmoji=self.emoji, hasWon=hasWin, hasTied=tie, replay=self.replay), view=self)
                self.stop()

    @discord.ui.button(label='', style=discord.ButtonStyle.gray, emoji="▶️")
    async def right(self, button: discord.ui.Button, interaction: discord.Interaction):
        if interaction.user.id == self.players[self.playerTurn]:
            if self.children[2].disabled: self.children[2].disabled = False
            self.cursor += 1 if self.cursor < 6 else 0
            self.replay.append("right")
            if self.c4Board[5][self.cursor] != -1:
                self.children[2].disabled = True
            await interaction.response.edit_message(content=toDiscordString(self.c4Board, self.cursor, self.players[self.playerTurn], self.playerTurn, customEmoji=self.emoji), view=self)

    @discord.ui.button(label='', style=discord.ButtonStyle.gray, emoji="⏩")
    async def maxRight(self, button: discord.ui.Button, interaction: discord.Interaction):
        if interaction.user.id == self.players[self.playerTurn]:
            if self.children[2].disabled: self.children[2].disabled = False
            self.cursor = 6
            self.replay.append("maxRight")
            if self.c4Board[5][self.cursor] != -1:
                self.children[2].disabled = True
            await interaction.response.edit_message(content=toDiscordString(self.c4Board, self.cursor, self.players[self.playerTurn], self.playerTurn, customEmoji=self.emoji), view=self)

def addToken(board: list, cursor, player):
    for i in range(len(board)):
        if board[i][cursor] == 1 or board[i][cursor] == 0:
            continue
        else: 
            board[i][cursor] = player
            return board
    return board

def toDiscordString(board: list, cursor: int, userId: int, player: int, customEmoji = None, hasWon = False, hasTied = False, replay = []):
    formattedBoard = "<:air:927935249982300251>"
    for c in range(7):
        if c == cursor:
            formattedBoard += '<a:c4_redCursor:933719793792602132>' if player == 0 else '<a:c4_yellowCursor:933719853204906125>'
        else: formattedBoard += '<:air:927935249982300251>'
    formattedBoard += '<:air:927935249982300251>\n'
    for i in range(len(board) - 1, -1, -1):
        formattedBoard += '❕'
        for j in range(len(board[i])):
            if board[i][j] == 3:
                formattedBoard += '<a:c4_redBlink:933719867469758534>'
            if board[i][j] == 2:
                formattedBoard += '<a:c4_yellowBlink:933719867360677898>'
            if board[i][j] == 1:
                formattedBoard += '🔴' if customEmoji is None else customEmoji
            elif board[i][j] == 0:
                formattedBoard += '🟡'
            elif board[i][j] == -1:
                formattedBoard += '<:air:927935249982300251>'
        formattedBoard += '❕\n'
    formattedBoard += '➖➖➖➖➖➖➖➖➖'
    if not hasTied:
        formattedBoard += f'<@{userId}>\'s turn ' if not hasWon else f"<@{userId}> has won ! "
        formattedBoard += "🟡" if player == 1 else "🔴" if customEmoji is None else customEmoji
    else: formattedBoard += "It's a tie..."
    if hasWon: formattedBoard += f"\nReplay : https://connect4-replay.netlify.app/?data={'-'.join(map(str, replay))}"
    return formattedBoard

if os.path.isfile('./messages.pkl'):
    with open('messages.pkl', 'rb') as f:
        usersMessages = pickle.load(f)
else:
    with open('messages.pkl', 'wb'): pass

if os.path.isfile('./bingo.pkl'):
    with open('bingo.pkl', 'rb') as f:
        emptyBingo = pickle.load(f)
else:
    with open('bingo.pkl', 'wb'): pass

if not os.path.isfile('./tempBingo.png'):
    crossBingo(-2, -1, True)

if os.path.isfile('./titleAlts.pkl'):
    with open('titleAlts.pkl', 'rb') as f:
        titleAlts = pickle.load(f)
else:
    with open('titleAlts.pkl', 'wb'): pass