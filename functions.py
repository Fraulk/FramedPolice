import re
import time
import json
import pickle
import random
import discord
import datetime
import shutil
from discord.ext import commands
from discord import Embed
from discord.ext.commands import Bot
import requests
from PIL import Image, ImageDraw
from discord.ui import button, View, Button, view
from discord.interactions import Interaction

from vars import *

# bot = commands.Bot(command_prefix='')

# 86400 : 24h
# 43200 : 12h
# Test channel : 873627093840314401
# Framed channel : 549986930071175169
DELAY = 7200
LIMIT = 5
usersMessages = []

class UserMessage:
    def __init__(self, id, name, time, count, reachedLimit):
        self.id = id
        self.name = name
        self.time = time
        self.count = count
        self.reachedLimit = reachedLimit

async def checkMessage(message):
    if (message.author.bot):
        print("bot message ignored")
        return
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
        return
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

def saveConfig():
    with open('./config.ini', 'w') as configfile:
        config.write(configfile)

def removeFilesInFolder(folder = './todaysGallery'):
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))

def changeCurrentLimit(ctx, arg):
    print(f"'changeLimit' command has been used by {ctx.author.name}#{ctx.author.discriminator}")
    global LIMIT
    LIMIT = int(arg)
    config['DEFAULT']['limit'] = str(LIMIT)
    saveConfig()
    print("Limit has been changed to", arg)

def changeCurrentDelay(ctx, arg):
    print(f"'changeDelay' command has been used by {ctx.author.name}#{ctx.author.discriminator}")
    global DELAY
    DELAY = int(arg)
    config['DEFAULT']['delay'] = str(DELAY)
    saveConfig()
    print("Delay has been changed to", arg)

def getCurrentValue(): return (LIMIT, DELAY)

async def resetUser(arg):
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
    return response

async def resetAllUsers():
    global usersMessages
    for msg in usersMessages:
        msg.count = 0
        msg.reachedLimit = False
    await save()

async def getCams(args):
    response = requests.get('https://docs.google.com/spreadsheet/ccc?key=1lnM2SM_RBzqile870zG70E39wuuseqQE0AaPW-P1p5E&output=csv')
    assert response.status_code == 200, 'Wrong status code'
    # print(response.content)
    spreadData = str(response.content).split('\\r\\n')
    spreadData.pop(0)
    matched_lines = []
    line_index = 0
    args = ' '.join(args) if type(args) is tuple else args
    args = args.replace("'", "\\'")
    for line in spreadData:
        if str(args).lower() in line.lower().split(',')[0]:
            next_index = 1
            if line.find(',') > -1:
                matched_lines += [line]
            try:
                if(spreadData[line_index + next_index] == ''): next_index += 1
            except: pass
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
    args = ' '.join(args) if type(args) is tuple else args
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
    args = ' '.join(args) if type(args) is tuple else args
    args = args.replace("'", "\\'")
    responseAL = requests.get('https://framedsc.github.io/A-L.htm')
    responseMZ = requests.get('https://framedsc.github.io/M-Z.htm')
    consoleGuide = requests.get('https://framedsc.com/Consoleguides.htm')
    responseGeneralGuides = requests.get('https://framedsc.github.io/GeneralGuides/index.htm')
    responseGeneralGuidesAdv = requests.get('https://framedsc.github.io/GeneralGuidesAdvanced.htm')
    responseReshadeGuides = requests.get('https://framedsc.github.io/ReshadeGuides/index.htm')
    responseReshadeShaderGuides = requests.get('https://framedsc.github.io/ReshadeGuidesShaderguides.htm')
    responseReshadeAddonsGuides = requests.get('https://framedsc.com/ReshadeGuidesAddonguides.htm')
    assert responseAL.status_code == 200, 'Wrong status code'
    assert responseMZ.status_code == 200, 'Wrong status code'
    assert consoleGuide.status_code == 200, 'Wrong status code'
    assert responseGeneralGuides.status_code == 200, 'Wrong status code'
    assert responseGeneralGuidesAdv.status_code == 200, 'Wrong status code'
    assert responseReshadeGuides.status_code == 200, 'Wrong status code'
    assert responseReshadeShaderGuides.status_code == 200, 'Wrong status code'
    assert responseReshadeAddonsGuides.status_code == 200, 'Wrong status code'
    responses = str(responseAL.content)
    responses += str(responseMZ.content)
    responses += str(consoleGuide.content)
    responses += str(responseGeneralGuides.content)
    responses += str(responseGeneralGuidesAdv.content)
    responses += str(responseReshadeGuides.content)
    responses += str(responseReshadeShaderGuides.content)
    responses += str(responseReshadeAddonsGuides.content)
    normalizedList = re.sub(r'\\t|\\n|\\r', '\n', responses)
    guidesRegex = r'"><a href="(GameGuides\/.*\.htm|..\/ReshadeGuides\/.*\.htm|..\/GeneralGuides\/.*\.htm|ReshadeGuides\/Shaders\/.*\.htm|ReshadeGuides\/Addons\/.*\.htm)">(.*)<\/a>'
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
    args = ' '.join(args) if type(args) is tuple else args
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
    authorName = message.author.name + "#" + message.author.discriminator
    authorId = message.author.id
    SLDchannel = bot.get_channel(SLDump)
    if message.author.bot and len(message.mentions) > 0: 
        authorName = message.mentions[0].name + "#" + message.mentions[0].discriminator
        authorId = message.mentions[0].id
    userDict = {}
    links = re.findall("(https:\/\/discord.com\/channels\/.*\/.*\d)(?:| )", message.content)
    if len(links) <= 3: return
    print("---------------------------------------- Building second-look message for " + authorName)
    async with message.channel.typing():
        for link in links:
            slink = link.split("/")
            original_message = await bot.get_guild(int(slink[-3])).get_channel(int(slink[-2])).fetch_message(int(slink[-1]))
            raw_shot = requests.get(original_message.attachments[0].url, stream=True).raw
            print(raw_shot)
            shot = Image.open(raw_shot)
            shot = shot.convert(mode="RGB")
            print(shot)
            shot.save(f'secondLook/{original_message.author.name}-{original_message.created_at.timestamp()}.jpg', format="JPEG", quality=60)
            print("shot saved")
            sent_message = await SLDchannel.send(file=discord.File(f'secondLook/{original_message.author.name}-{original_message.created_at.timestamp()}.jpg'))
            shotPath = f'secondLook/{original_message.author.name}-{original_message.created_at.timestamp()}.jpg'
            try:
                blob = bucket.blob(shotPath)
                blob.upload_from_filename(shotPath)
                blob.make_public()
                print(blob.public_url)
            except: continue
            print(sent_message)
            tempDict = {}
            tempDict['id'] = f"{original_message.author.id}"
            tempDict['name'] = original_message.author.name
            # tempDict['nickname'] = original_message.author.nick
            tempDict['displayName'] = original_message.author.display_name
            tempDict['globalName'] = original_message.author.global_name
            tempDict['isSpoiler'] = original_message.attachments[0].is_spoiler()
            tempDict['createdAt'] = original_message.created_at.timestamp()
            tempDict['imageUrl'] = blob.public_url
            tempDict['width'] = sent_message.attachments[0].width
            tempDict['height'] = sent_message.attachments[0].height
            tempDict['messageUrl'] = link
            userDict[str(original_message.id)] = tempDict
    await bot.get_channel(SLChannel).send(f"Here is your link : https://second-look.netlify.app?id={authorId}")
    print("---------------------------------------- Building ended")
    ref.child(str(authorId)).set(userDict)
    removeFilesInFolder("./secondLook")

async def todaysGallery():
    bot.dispatch("today_gallery_end")
    userDict = {}
    day_ago = datetime.datetime.today() - datetime.timedelta(days=1)
    SYSchannel = bot.get_channel(SYSChannel)
    SLDchannel = bot.get_channel(SLDump)
    if SYSchannel is None: return
    print("---------------------------------------- Building today's gallery")
    messages = [message async for message in SYSchannel.history(limit=200, after=day_ago)]
    for msg in messages:
        try:
            enough_reaction = False if await getShotReactions(msg) <= 28 else True
        except: continue
        try:
            raw_shot = requests.get(msg.attachments[0].url, stream=True).raw
        except: continue
        print(raw_shot)
        shot = Image.open(raw_shot)
        shot = shot.convert(mode="RGB")
        print(shot)
        shot.save(f'todaysGallery/{msg.author.name}-{msg.created_at.timestamp()}.jpg', format="JPEG", quality=50)
        print("shot saved")
        try:
            sent_message = await SLDchannel.send(file=discord.File(f'todaysGallery/{msg.author.name}-{msg.created_at.timestamp()}.jpg'))
        except: continue
        shotPath = f'todaysGallery/{msg.author.name}-{msg.created_at.timestamp()}.jpg'
        try:
            blob = bucket.blob(shotPath)
            blob.upload_from_filename(shotPath)
            blob.make_public()
            print(blob.public_url)
        except: continue
        print(sent_message)
        tempDict = {}
        tempDict['id'] = f"{msg.author.id}"
        tempDict['name'] = msg.author.name
        # tempDict['nickname'] = msg.author.nick
        tempDict['displayName'] = msg.author.display_name
        tempDict['createdAt'] = msg.created_at.timestamp()
        tempDict['imageUrl'] = blob.public_url
        tempDict['width'] = sent_message.attachments[0].width
        tempDict['height'] = sent_message.attachments[0].height
        tempDict['messageUrl'] = msg.jump_url
        tempDict['isHoffed'] = enough_reaction
        userDict[str(msg.id)] = tempDict
        print("next message")
    print("end")
    botsData = ref.child(str(bot.user.id)).get()
    if botsData is not None:
        global_len = len(botsData) + len(userDict)
    else:
        botsData = {}
        global_len = len(userDict)
    # adds the current gallery shot count stored in firebase to the count of today's shot and if less, does nothing, else it removes the extra shots from the start of the dict (the oldest)
    if global_len >= 1000:
        for i in range(global_len - 1000):
            botsData.pop(next(iter(botsData)))
    botsData.update(userDict)
    print(len(botsData))
    ref.child(str(bot.user.id)).set(botsData)
    # await bot.get_channel(889793521106714634).send(f"Today's gallery has been updated with today's shot : https://second-look.netlify.app?id={bot.user.id}")
    await bot.get_channel(SLChannel).send(f"Today's gallery has been updated with today's shot : https://second-look.netlify.app?id={bot.user.id}")
    removeFilesInFolder("./todaysGallery")
    print("---------------------------------------- Building ended")

async def startThread(message):
    title = f"Hello There, {message.author.name}"
    thread = await message.channel.create_thread(name=title, message=message, reason="Thread created for new member")
    await thread.send("https://tenor.com/view/hello-there-general-kenobi-gif-18841535")
    await message.author.remove_roles(message.author.guild.get_role(WelcomeRole))
    await message.author.add_roles(message.author.guild.get_role(PadawanRole))

async def over2000(data, gameNames, query):
    isOver2000 = len(data) > 2000
    query = ' '.join(query) if type(query) is tuple else query
    if(isOver2000):
        # response = "Search query is too vague, there are too many results to show.\n" + str(len(gameNames)) + " games corresponds to your query, please retype the command with one of them : \n"
        response = random.choice(tooVague).format(query)
        response += "  |  ".join([name for name in gameNames])
        if(len(gameNames) > 15):
            response = "I found too many results for `{}` ! Please be more specific !".format(query)
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
        epoch = re.findall(r"https:\/\/framedsc\.com\/HallOfFramed\/.*imageId=(\d*)", msg)
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

    def __init__(self, channelId, timeout = None):
        super().__init__(timeout=timeout)
        self.chanId = channelId
        
    @discord.ui.button(label='Check', style=discord.ButtonStyle.blurple)
    async def checkCompact(self, interaction: discord.Interaction, button: discord.ui.Button):
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
        botPfp = requests.get(bot.user.avatar, stream=True).raw
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
        botPfp = requests.get(bot.user.avatar, stream=True).raw
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
    def __init__(self, players: list[str], customEmoji1 = None, customEmoji2 = None):
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
        self.emoji1 = customEmoji1
        self.emoji2 = customEmoji2

    # When the confirm button is pressed, set the inner value to `True` and
    # stop the View from listening to more input.
    # We also send the user an ephemeral message that we're confirming their choice.
    @discord.ui.button(label='Confirm', style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.players[1] is not None:
            if interaction.user.id == self.players[1]:
                await interaction.response.edit_message(content=toDiscordString(self.connect4, 3, self.players[1], 1, customEmoji1=self.emoji1, customEmoji2=self.emoji2), view=Connect4(self.connect4, players=self.players, customEmoji1=self.emoji1, customEmoji2=self.emoji2))
                self.stop()
            else:
                await interaction.response.edit_message(content=f"<@{self.players[0]}> wants to play connect4 with you <@{self.players[1]}>, will you accept ? PS: Only the mentionned person can respond")
        else:
            self.players[1] = interaction.user.id
            await interaction.response.edit_message(content=toDiscordString(self.connect4, 3, self.players[1], 1, customEmoji1=self.emoji1, customEmoji2=self.emoji2), view=Connect4(self.connect4, players=self.players, customEmoji1=self.emoji1, customEmoji2=self.emoji2))
            self.stop()

    # This one is similar to the confirmation button except sets the inner value to `False`
    @discord.ui.button(label='Cancel', style=discord.ButtonStyle.grey)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.players[1] is not None:
            if interaction.user.id == self.players[1]:
                button.disabled = True
                for child in self.children:
                    child.disabled = True
                await interaction.response.edit_message(content='Sorry, but the offer got rejected', view=self)
                self.stop()
            else:
                await interaction.response.edit_message(content=f"<@{self.players[0]}> wants to play connect4 with you <@{self.players[1]}>, will you accept ? PS: Only the mentionned person can respond")
        else:
            button.disabled = True
            for child in self.children:
                child.disabled = True
            await interaction.response.edit_message(content='Sorry, but the offer got rejected', view=self)
            self.stop()

class Connect4(View):
    def __init__(self, board, players: list[str], customEmoji1 = None, customEmoji2 = None):
        super().__init__()
        self.cursor = 3
        self.c4Board = board
        self.emoji1 = customEmoji1
        self.emoji2 = customEmoji2
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
    async def maxLeft(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id == self.players[self.playerTurn]:
            if self.children[2].disabled: self.children[2].disabled = False
            self.cursor = 0
            self.replay.append("maxLeft")
            if self.c4Board[5][self.cursor] != -1:
                self.children[2].disabled = True
            await interaction.response.edit_message(content=toDiscordString(self.c4Board, self.cursor, self.players[self.playerTurn], self.playerTurn, customEmoji1=self.emoji1, customEmoji2=self.emoji2), view=self)

    @discord.ui.button(label='', style=discord.ButtonStyle.gray, emoji="◀️")
    async def left(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id == self.players[self.playerTurn]:
            if self.children[2].disabled: self.children[2].disabled = False
            self.cursor -= 1 if self.cursor > 0 else 0
            self.replay.append("left")
            if self.c4Board[5][self.cursor] != -1:
                self.children[2].disabled = True
            await interaction.response.edit_message(content=toDiscordString(self.c4Board, self.cursor, self.players[self.playerTurn], self.playerTurn, customEmoji1=self.emoji1, customEmoji2=self.emoji2), view=self)

    @discord.ui.button(label='', style=discord.ButtonStyle.blurple, emoji="🔽")
    async def add(self, interaction: discord.Interaction, button: discord.ui.Button):
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
                await interaction.response.edit_message(content=toDiscordString(self.c4Board, self.cursor, self.players[self.playerTurn], self.playerTurn, customEmoji1=self.emoji1, customEmoji2=self.emoji2), view=self)
            else:
                self.playerTurn = not self.playerTurn
                for child in self.children:
                    child.disabled = True
                self.replay.append("add")
                await interaction.response.edit_message(content=toDiscordString(self.c4Board, self.cursor, self.players[self.playerTurn], self.playerTurn, customEmoji1=self.emoji1, customEmoji2=self.emoji2, hasWon=hasWin, hasTied=tie, replay=self.replay), view=self)
                self.stop()

    @discord.ui.button(label='', style=discord.ButtonStyle.gray, emoji="▶️")
    async def right(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id == self.players[self.playerTurn]:
            if self.children[2].disabled: self.children[2].disabled = False
            self.cursor += 1 if self.cursor < 6 else 0
            self.replay.append("right")
            if self.c4Board[5][self.cursor] != -1:
                self.children[2].disabled = True
            await interaction.response.edit_message(content=toDiscordString(self.c4Board, self.cursor, self.players[self.playerTurn], self.playerTurn, customEmoji1=self.emoji1, customEmoji2=self.emoji2), view=self)

    @discord.ui.button(label='', style=discord.ButtonStyle.gray, emoji="⏩")
    async def maxRight(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id == self.players[self.playerTurn]:
            if self.children[2].disabled: self.children[2].disabled = False
            self.cursor = 6
            self.replay.append("maxRight")
            if self.c4Board[5][self.cursor] != -1:
                self.children[2].disabled = True
            await interaction.response.edit_message(content=toDiscordString(self.c4Board, self.cursor, self.players[self.playerTurn], self.playerTurn, customEmoji1=self.emoji1, customEmoji2=self.emoji2), view=self)

def addToken(board: list, cursor, player):
    for i in range(len(board)):
        if board[i][cursor] == 1 or board[i][cursor] == 0:
            continue
        else: 
            board[i][cursor] = player
            return board
    return board

def toDiscordString(board: list, cursor: int, userId: int, player: int, customEmoji1 = None, customEmoji2 = None, hasWon = False, hasTied = False, replay = []):
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
                formattedBoard += '🔴' if customEmoji1 is None else customEmoji1
            elif board[i][j] == 0:
                formattedBoard += '🟡' if customEmoji2 is None else customEmoji2
            elif board[i][j] == -1:
                formattedBoard += '<:air:927935249982300251>'
        formattedBoard += '❕\n'
    formattedBoard += '➖➖➖➖➖➖➖➖➖'
    if not hasTied:
        formattedBoard += f'<@{userId}>\'s turn ' if not hasWon else f"<@{userId}> has won ! "
        if player == 1:
            formattedBoard += "🟡" if customEmoji2 is None else customEmoji2
        else:
            formattedBoard += "🔴" if customEmoji1 is None else customEmoji1
    else: formattedBoard += "It's a tie..."
    if hasWon: formattedBoard += f"\nReplay : https://connect4-replay.netlify.app/?data={'-'.join(map(str, replay))}"
    return formattedBoard

# thanks nico
async def getShotReactions(message) -> int:
    users = []
    if len(message.reactions) == 0:
        return 0
    for reaction in message.reactions:
        async for user in reaction.users():
            users.append(user)
    users = list(filter(lambda u: u.id != message.author.id, dict.fromkeys(users)))
    return len(users)

async def notifyHOFedUser(message):
    embed_author = message.embeds[0].author
    author = re.findall(r"Shot by (.*)", embed_author.name)[0]
    user = discord.utils.find(lambda m: str(m) == author, message.guild.members)
    HOFAlertRoleObject = discord.utils.get(message.guild.roles, id=HOFAlertRole) # Test server: 1000794708475396176
    if user is not None:
        if HOFAlertRoleObject not in user.roles: return
        DMChannel = await user.create_dm()
        url_view = discord.ui.View()
        url_view.add_item(discord.ui.Button(label='Go to Message', style=discord.ButtonStyle.url, url=message.jump_url))
        await DMChannel.send(f"Hello {user.name}, your shot has been hoffed !", view=url_view)
    else: return

async def saveHOFun(message):
    # cdn.discordapp.com must be changed to to media.discordapp.net to use the discord default resize query params "?width=622&height=330"
    # {
    #   "gameName": message.content,
    #   "shotUrl": "https://cdn.discordapp.com/attachments/549986930071175169/550298931620216843/9294681953_19fd912d36_o.png",
    #   "height": 1079,
    #   "width": 2590,
    #   "thumbnailUrl": "https://media.discordapp.net/attachments/549986930071175169/550298931620216843/9294681953_19fd912d36_o.png?width=1295&height=538",
    #   "author": "325964388844437504",
    #   "date": "2019-02-27T12:51:29.487000",
    #   "score": 11,
    #   "ID": 1,
    #   "epochTime": 1551282689,
    #   "spoiler": false,
    #   "colorName": "brown"
    # }
    if len(message.attachments) == 0:
        return
    currentHOFun = ref.child("hall-of-fun/_default").get()
    # if i starts to 1 or 2, firebase does weird stuff, like ignoring the fact that it's a dict/object and transforms it into a list/array
    i = 1 if currentHOFun is None else len(currentHOFun) + 1
    userSubmissionDict = {}

    for item in message.attachments:
        userSubmissionDict["key-" + str(i)] = {}
        userSubmissionDict["key-" + str(i)]["gameName"] = message.content
        userSubmissionDict["key-" + str(i)]["shotUrl"] = item.url
        userSubmissionDict["key-" + str(i)]["width"] = item.width
        userSubmissionDict["key-" + str(i)]["height"] = item.height
        userSubmissionDict["key-" + str(i)]["thumbnailUrl"] = f'{item.url.replace("cdn.discordapp.com", "media.discordapp.net")}?width={round(item.width / 2)}&height={round(item.height / 2)}'
        userSubmissionDict["key-" + str(i)]["author"] = str(message.author.id)
        userSubmissionDict["key-" + str(i)]["date"] = message.created_at.strftime('%Y-%m-%dT%H:%M:%S.%f')
        userSubmissionDict["key-" + str(i)]["score"] = await getShotReactions(message)
        userSubmissionDict["key-" + str(i)]["epochTime"] = int(message.created_at.timestamp())
        userSubmissionDict["key-" + str(i)]["spoiler"] = item.is_spoiler()
        userSubmissionDict["key-" + str(i)]["colorName"] = "black"
        i += 1
    
    newHOFun = None
    if currentHOFun is None:
        newHOFun = {"_default": userSubmissionDict}
        ref.child("hall-of-fun").set(newHOFun)
    else:
        newHOFun = currentHOFun
        newHOFun.update(userSubmissionDict)
        ref.child("hall-of-fun/_default").set(newHOFun)

async def replaceTwitterLink(message):
    print("Twitter link containing video has been shared")
    print("Links video url:", message.embeds[0].video.url)
    print("Is the user a bot:", message.author.bot)
    print("Condition for the bot to post the fixed link (should be true if it's a video):", message.embeds[0].video.url is not None and message.author.bot is False)
    print("Url:", message.jump_url)
    if message.embeds[0].video.url is not None and message.author.bot is False:
        e = message.embeds[0].url
        e = e.replace("twitter.com", "fxtwitter.com")
        await message.edit(suppress=True)
        await message.reply(content=e, mention_author=False)
    else:
        print("The condition returned False")
        print("Links video url:", message.embeds[0].video.url)
        return

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

if not os.path.isfile('./config.ini'):
    config['DEFAULT'] = {
        'delay': '7200',
        'limit': '5'
    }
    saveConfig()
else:
    config.read('config.ini')
    DELAY = int(config['DEFAULT']['delay'])
    LIMIT = int(config['DEFAULT']['limit'])