import os
import re
import time
import pickle
import random
import discord
import datetime
import firebase_admin
from firebase_admin import db
from dotenv import load_dotenv
from discord.ext import commands
from firebase_admin import credentials

from vars import *
from functions import *

# pip install -U git+https://github.com/Rapptz/discord.py
load_dotenv()
API_KEY = os.getenv("API_KEY")
DB_URL = os.getenv("DB_URL")
cred = credentials.Certificate("./secret.json")
SLapp = firebase_admin.initialize_app(cred, {'databaseURL': DB_URL})
ref = db.reference("/")
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

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

class EphemeralBingo(View):

    def __init__(self, ctx, timeout = None):
        super().__init__(timeout=timeout)
        self.chanId = ctx.channel.id
        # print(self.chanId)
        # print(ctx.author)

    @discord.ui.button(label='Check', style=discord.ButtonStyle.blurple)
    async def check(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.send_message("Choose a box", view=BingoView(params={'user': interaction.user, 'channel': self.chanId}), ephemeral=True)
        
    @discord.ui.button(label='Check Compact', style=discord.ButtonStyle.grey)
    async def checkCompact(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.send_message("Choose a box", view=BingoView(params={'compact': True, 'user': interaction.user, 'channel': self.chanId}), ephemeral=True)

    # @discord.ui.button(label='Show score', style=discord.ButtonStyle.grey)
    # async def showScore(self, button: discord.ui.Button, interaction: discord.Interaction):
    #     await interaction.response.send_message("Current score", ephemeral=True)

class BingoView(View):

    def __init__(self, params, timeout = None):
        super().__init__(timeout=timeout)
        if not params.get('compact'): params['compact'] = False
        # print(params['user'].id)
        self.user = params['user']
        self.channel = params['channel']
        self.board = self.getScore()
        # print(self.user)
        # print(self.board)
        for x in range(5):
            for y in range(5):
                if params['compact']: self.add_item(BingoViewButton(x, y, f"{x+1}-{y+1}", self.board))
                if not params['compact']: self.add_item(BingoViewButton(x, y, bingoText[y][x], self.board))

    def getScore(self):
        # print(self.user.id)
        for bp in bingoPoints:
            # print(bp.name)
            # print(bp.pointMap)
            if bp.id == self.user.id:
                return bp.pointMap
        # print("came here")
        bingoPoints.append(BingoPoints(self.user.id, self.user, [[0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0]]))
        return [[0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0]]

    def setScore(self, x, y):
        # print(self.user.id)
        for bp in bingoPoints:
            if bp.id == self.user.id:
                # print(bp.name)
                # print(bp.pointMap)
                bp.pointMap[x][y] = 1

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
    def __init__(self, x, y, label, board):
        if board[x][y] == 1:
            super().__init__(label=label, style=discord.ButtonStyle.success, disabled=True, row=y)
        if board[x][y] == 0:
            super().__init__(label=label, style=discord.ButtonStyle.secondary, row=y)
        self.x = x
        self.y = y
        self.label = label if label != "3-3" else "Free"
    
    async def callback(self, interaction: discord.Interaction):
        assert self.view is not None
        view = self.view
        view.setScore(self.x, self.y)

        self.style = discord.ButtonStyle.success
        self.disabled = True
        for child in view.children:
            child.disabled = True
        await interaction.response.edit_message(view=view)

        winner = view.checkWinner()
        if winner is not None:
            bot.dispatch("bingo_winner", view.user, view.channel)

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
    elif message.content.lower() == "good bot":
        await message.add_reaction(random.choice(goodReaction))
        await react(message, "good", bot.user.avatar)
    elif message.content.lower() == "bad bot":
        await message.add_reaction(random.choice(badReaction))
        await react(message, "bad", bot.user.avatar)
    elif message.content.lower() == "horny bot":
        await message.add_reaction(random.choice(hornyReaction))
        await react(message, "horny", bot.user.avatar)
    else:
        return

@bot.event
async def on_message_edit(before, after):
    await bot.process_commands(after)
    if after.content.lower() == "good bot":
        await after.add_reaction(random.choice(goodReaction))
        await react(after, "good", bot.user.avatar)
    elif after.content.lower() == "bad bot":
        await after.add_reaction(random.choice(badReaction))
        await react(after, "bad", bot.user.avatar)
    elif after.content.lower() == "horny bot":
        await after.add_reaction(random.choice(hornyReaction))
        await react(after, "horny", bot.user.avatar)
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

@bot.command(name='countShots', help='Count the last 7 days shots or from a certain date')
@commands.has_any_role(549988038516670506, 549988228737007638, 874375168204611604)
async def countShots(ctx, *args):
    week_ago = datetime.datetime.today() - datetime.timedelta(days=7)
    print(week_ago)
    channel = bot.get_channel(SYSChannel)
    messages = await channel.history(limit=None, after=week_ago).flatten()
    print(len(messages))

@bot.command(name='cam', help='Search for a freecams or a tool by string. ex: !cam cyberpunk 2077')
async def cam(ctx, *args):
    async with ctx.typing():
        data, gameNames = await getCams(args)
        if len(data) == 0: data = random.choice(notFound).format(' '.join(args))
        e = discord.Embed(title="Freecams, tools and stuff",
                          url="https://docs.google.com/spreadsheets/d/1lnM2SM_RBzqile870zG70E39wuuseqQE0AaPW-P1p5E/edit#gid=0",
                          description="Based on originalnicodr spreadsheet",
                          color=0x3498DB)
        e.set_thumbnail(url="https://cdn.discordapp.com/avatars/128245457141891072/0ab765d7c5bd8fb373dbd3627796aeec.png?size=128")
        data = await over2000(data, gameNames, args)
    await ctx.send(content=data, embed=e) if len(data) < 2000 else await ctx.send("Search query is too vague, there are too many results to show")

@bot.command(name='uuu', help='Checks if a game is compatible with UUU or have a guide on the site. ex: !uuu the ascent')
async def uuu(ctx, *args):
    async with ctx.typing():
        data, gameNames = await getUUU(args)
        if len(data) == 0: data = random.choice(notFound).format(' '.join(args))
        e = discord.Embed(title="FRAMED. Screenshot Community",
                          url="https://framedsc.github.io/index.htm",
                          description="© 2019-2021 FRAMED. All rights reserved. ",
                          color=0x9a9a9a)
        e.set_thumbnail(url="https://cdn.discordapp.com/emojis/575642684006334464.png?size=128")
        data = await over2000(data, gameNames, args)
    await ctx.send(content=data, embed=e) if len(data) < 2000 else await ctx.send("Search query is too vague, there are too many results to show")

@bot.command(name='guide', help='Checks if a game have a guide on the site. ex: !guide cyberpunk')
async def guide(ctx, *args):
    async with ctx.typing():
        data, gameNames = await getGuides(args)
        if len(data) == 0: data = random.choice(notFound).format(' '.join(args))
        e = discord.Embed(title="FRAMED. Screenshot Community",
                          url="https://framedsc.github.io/index.htm",
                          description="© 2019-2021 FRAMED. All rights reserved. ",
                          color=0x9a9a9a)
        e.set_thumbnail(url="https://cdn.discordapp.com/emojis/575642684006334464.png?size=128")
        data = await over2000(data, gameNames, args)
    await ctx.send(content=data, embed=e) if len(data) < 2000 else await ctx.send("Search query is too vague, there are too many results to show")

@bot.command(name='cheat', help='Checks if a game have cheat tables on the site. ex: !cheat alien')
async def cheat(ctx, *args):
    async with ctx.typing():
        data, gameNames = await getCheats(args)
        if len(data) == 0: data = random.choice(notFound).format(' '.join(args))
        e = discord.Embed(title="FRAMED. Screenshot Community",
                          url="https://framedsc.github.io/index.htm",
                          description="© 2019-2021 FRAMED. All rights reserved. ",
                          color=0x9a9a9a)
        e.set_thumbnail(url="https://cdn.discordapp.com/emojis/575642684006334464.png?size=128")
        data = await over2000(data, gameNames, args)
    await ctx.send(content=data, embed=e) if len(data) < 2000 else await ctx.send("Search query is too vague, there are too many results to show")

@bot.command(name='tool', help='Checks if a game have a guide, cam or works with UUU. ex: !tool cyberpunk')
async def tool(ctx, *args):
    async with ctx.typing():
        cams, camGameNames = await getCams(args)
        uuus, uuuGameNames = await getUUU(args)
        guides, guideGameNames = await getGuides(args)
        cheats, cheatGameNames = await getCheats(args)
        data = ""
        if len(cams) > 0:
            data += cams + "----\n" if len(uuus) > 0 or len(guides) > 0 or len(cheats) > 0 else cams
        if len(uuus) > 0:
            data += uuus + "----\n" if len(guides) > 0 or len(cheats) > 0 else uuus
        if len(guides) > 0:
            data += guides + "----\n" if len(cheats) > 0 else guides
        if len(cheats) > 0:
            data += cheats
        if len(data) == 0: data = random.choice(notFound).format(' '.join(args))
        if random.randint(0, 9) <= 1:
            data += "\n**╘** : <https://discord.com/channels/549986543650078722/549986543650078725/893340504719249429>"
        # e = discord.Embed(title="FRAMED. Screenshot Community",
        #                   url="https://framedsc.github.io/index.htm",
        #                   description="© 2019-2021 FRAMED. All rights reserved. ",
        #                   color=0x9a9a9a)
        # e.set_thumbnail(url="https://cdn.discordapp.com/emojis/575642684006334464.png?size=128")
        data = await over2000(data, camGameNames + uuuGameNames + guideGameNames + cheatGameNames, args)
    await ctx.send(content=data) if len(data) < 2000 else await ctx.send("Search query is too vague, there are too many results to show") # + str(len(data))

@bot.command(name='tools', help='Alias for !tool, because a lotta people does the mistake lol')
async def tools(ctx, *args):
    await tool(ctx, *args)

@bot.command(name="bingo", help="Play to the framed bingo !")
async def bingo(ctx, *args):
    bingoView = EphemeralBingo(ctx) # ctx as param
    e = discord.Embed(title="Bingo card",
                      url="https://discord.com/channels/549986543650078722/549986543650078725/914511447176921098",
                      description="",
                      color=0x9a9a9a
    )
    e.set_image(url="https://cdn.discordapp.com/attachments/549986543650078725/914511446975582218/bingo2.png")
    await ctx.send("", view=bingoView, embed=e)

@bot.event
async def on_bingo_winner(user, channelId):
    bingoPoints.clear()
    channel = bot.get_channel(channelId)
    await channel.send(f"{user.mention} won the bingo !")

@bot.command(name='help')
async def help(ctx, *args):
    e = discord.Embed(title="List of commands",
                      url="https://github.com/Fraulk/FramedPolice",
                      description="",
                      color=0x9a9a9a
    )
    e.add_field(name=helpMsg['check']['name'], value=helpMsg['check']['description'], inline=False)
    e.add_field(name=helpMsg['cam']['name'], value=helpMsg['cam']['description'], inline=False)
    e.add_field(name=helpMsg['guide']['name'], value=helpMsg['guide']['description'], inline=False)
    e.add_field(name=helpMsg['uuu']['name'], value=helpMsg['uuu']['description'], inline=False)
    e.add_field(name=helpMsg['cheat']['name'], value=helpMsg['cheat']['description'], inline=False)
    e.add_field(name=helpMsg['tool']['name'], value=helpMsg['tool']['description'], inline=False)
    if ctx.guild is not None:
        FoudersEd = discord.utils.get(ctx.guild.roles, id=549988038516670506)
        mods = discord.utils.get(ctx.guild.roles, id=549988228737007638)
        testFoudersEd = discord.utils.get(ctx.guild.roles, id=874375168204611604)
        if FoudersEd in ctx.author.roles or mods in ctx.author.roles or testFoudersEd in ctx.author.roles:
            e.add_field(name=helpMsg['changeDelay']['name'], value=helpMsg['changeDelay']['description'], inline=False)
            e.add_field(name=helpMsg['changeLimit']['name'], value=helpMsg['changeLimit']['description'], inline=False)
            e.add_field(name=helpMsg['currentValue']['name'], value=helpMsg['currentValue']['description'], inline=False)
            e.add_field(name=helpMsg['dump']['name'], value=helpMsg['dump']['description'], inline=False)
            e.add_field(name=helpMsg['dumpR']['name'], value=helpMsg['dumpR']['description'], inline=False)
            e.add_field(name=helpMsg['reset']['name'], value=helpMsg['reset']['description'], inline=False)
            e.add_field(name=helpMsg['resetAll']['name'], value=helpMsg['resetAll']['description'], inline=False)
    e.add_field(name=helpMsg['bingo']['name'], value=helpMsg['bingo']['description'], inline=False)
    e.add_field(name=helpMsg['special']['name'], value=helpMsg['special']['description'], inline=False)
    # e.set_image(url="https://cdn.discordapp.com/emojis/575642684006334464.png?size=40")
    e.set_footer(text="Made by Fraulk", icon_url="https://cdn.discordapp.com/avatars/192300712049246208/a_c7d1c089c53b152ed0b3b00304fa3307.webp?size=40")
    # does the gif version of my pfp still exists after nitro ends ? https://cdn.discordapp.com/avatars/192300712049246208/a_c7d1c089c53b152ed0b3b00304fa3307.gif?size=40
    await ctx.send(embed=e)

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
# FIXME : remove spaces from links, test with cyberpunk, bal
# FIXME : !tools la throws index out of range
# FIXME : !tools halo throws error
# FIXME : !tools watch dogs 2 has embeds, same for nier
# TODO : make the bot detect birthday on message
# TODO : add bingo command
# TODO : add dropdown and buttons to tools

if os.path.isfile('./messages.pkl'):
    with open('messages.pkl', 'rb') as f:
        usersMessages = pickle.load(f)
else:
    with open('messages.pkl', 'wb'): pass

bot.run(API_KEY)
