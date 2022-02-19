import os
import time
import random
# import asyncio
import datetime

from vars import *
from functions import *
from wordle import *

# pip install -U git+https://github.com/Rapptz/discord.py

@bot.event
async def on_ready():
    print(f"{bot.user} logged in")
    if not os.path.isfile('./tempBingo.png'):
        recreateBingo(emptyBingo)

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
        e = discord.Embed(title="FRAMED. Screenshot Community",
                          url="https://framedsc.github.io/index.htm",
                          description="© 2019-2021 FRAMED. All rights reserved. ",
                          color=0x9a9a9a)
        e.set_thumbnail(url="https://cdn.discordapp.com/emojis/575642684006334464.png?size=128")
        data = await over2000(data, camGameNames + uuuGameNames + guideGameNames + cheatGameNames, args)
    await ctx.send(content=data, embed=e) if len(data) < 2000 else await ctx.send("Search query is too vague, there are too many results to show") # + str(len(data))

@bot.command(name='tools', help='Alias for !tool, because a lotta people does the mistake lol')
async def tools(ctx, *args):
    await tool(ctx, *args)

commandCooldown = 1000
cooldownEnd = 0
@bot.command(name="bingo", help="Play to the framed bingo !")
@commands.cooldown(1, 30, commands.BucketType.guild)
async def bingo(ctx, *args):
    bingoView = EphemeralBingo(ctx) # ctx as param
    # e = discord.Embed(title="Bingo card",
    #                   url="https://discord.com/channels/549986543650078722/549986543650078725/914511447176921098",
    #                   description="",
    #                   color=0x9a9a9a
    # )
    # e.set_image(url="https://cdn.discordapp.com/attachments/549986543650078725/914511446975582218/bingo2.png")
    await ctx.send("", view=bingoView, file=discord.File('tempBingo.png'))

@bot.command(name="resetBingo", help="Manually reset the bingo")
@commands.has_any_role(549988038516670506, 549988228737007638, 874375168204611604)
async def resetBingo(ctx):
    resetBingoBoard()

@commands.has_any_role(549988038516670506, 549988228737007638, 874375168204611604)
@bot.command(name="changeBingo", help="Change the bingo image (change takes effect at the next round)")
async def changeBingo(ctx):
    if hasattr(ctx.message, 'attachments') and len(ctx.message.attachments) == 1 and ctx.message.attachments[0].url[-3:] == "png":
        async with ctx.typing():
            newBingoRaw = requests.get(ctx.message.attachments[0].url, stream=True).raw
            newBingo = Image.open(newBingoRaw)
            newBingo.save('images/bingo.png')
        await ctx.send("The new bingo image has been set !\nThe new bingo will be used for the next round")
    else:    
        await ctx.send("Oops, something went wrong...\nPlease send a valid **PNG** file attached to the command message")

@bot.event
async def on_bingo_winner(user, channelId):
    resetBingoBoard()
    saveBingo()
    lastBingo = Image.open('./tempBingo.png')
    lastBingo.save('./lastBingo.png')
    channel = bot.get_channel(channelId)
    await channel.send("The bingo has been completed !", file=discord.File('./lastBingo.png'))

@commands.has_any_role(549988038516670506, 549988228737007638, 874375168204611604)
@bot.command(name="addTitle", help="Add a game title and all his alts")
async def addTitle(ctx, *args):
    global titleAlts
    simpleArg = None
    simpleName = None
    args = ' '.join(args)
    args = args.replace("'", "\\'")
    if args == '': return
    if args.find(';') > -1:
        simpleArg = args.split(';')[1].lstrip(' ')
        simpleName = args.split(';')[0].rstrip(' ')
        if simpleArg == '' or simpleName == '': return
        if simpleArg.find(',') > -1:
            simpleArg = simpleArg.split(',')
            simpleArg = [e.lstrip(' ').rstrip(' ') for e in simpleArg]
        index = next((i for i, item in enumerate(titleAlts) if item.get(simpleName) is not None), None)
        if index is not None:
            titleAlts[index][simpleName].append(simpleArg) if isinstance(simpleArg, str) else titleAlts[index][simpleName].extend(simpleArg)
        else:
            alts = {}
            alts[simpleName] = [simpleArg] if isinstance(simpleArg, str) else simpleArg
            titleAlts.append(alts)
        saveTitleAlts()
        await ctx.message.add_reaction('✅')
        # print(titleAlts)
        # print(next((i for i, item in enumerate(titleAlts) if simpleArg in item[simpleName]), None))

@commands.has_any_role(549988038516670506, 549988228737007638, 874375168204611604)
@bot.command(name="removeTitle", help="Remove a game title and all his alts")
async def removeTitle(ctx, *args):
    global titleAlts
    args = ' '.join(args)
    args = args.replace("'", "\\'")
    if args == '': return
    titleAlts[:] = [d for d in titleAlts if d.get(args) is None]
    saveTitleAlts()
    await ctx.message.add_reaction('✅')

@bot.command(name="showTitle", help="Remove a game title and all his alts")
async def showTitle(ctx, *args):
    global titleAlts
    content = ""
    args = ' '.join(args)
    args = args.replace("'", "\\'")
    if args == '':
        i = 0
        for d in titleAlts:
            gameTitle = next(iter(d))
            content += f"**{gameTitle}** : {', '.join(d.get(gameTitle))}\n"
            if i % 15 == 0:
                await ctx.send(content if len(content) < 2000 else "Too much data to send, <@192300712049246208> failed his job so please bully him and make him fix me")
                content = ""
            i += 1
    else:
        index = next((i for i, item in enumerate(titleAlts) if item.get(args) is not None), None)
        if index is not None:
            gameTitle = next(iter(titleAlts[index]))
            content += f"**{gameTitle}** : {', '.join(titleAlts[index].get(args))}"
        else:
            content = "Unknown game"
    await ctx.send(content if len(content) < 2000 else "Too much data to send, <@192300712049246208> failed his job so please bully him and make him fix me")

@bot.command(name="connect")
async def connect(ctx, arg, arg2 = None):
    view = Confirm([ctx.message.author.id, ctx.message.mentions[0].id], arg2)
    await ctx.send(content=f"{ctx.message.author.mention} wants to play connect4 with you {ctx.message.mentions[0].mention}, will you accept ?", view=view)
    # Wait for the View to stop listening for input...
    await view.wait()

@bot.command(name='golf')
async def golf(ctx, *args):
    content = golfEmoji
    await ctx.send(content)

@bot.command(name='mario')
async def mario(ctx, *args):
    content = marioEmoji
    await ctx.send(content)

# @bot.command(name='shocked')
# async def shocked(ctx, *args):
#     content = shockedFrames['shocked0']
#     message = await ctx.send(content)
#     for i in range(20):
#         for key, frame in shockedFrames.items():
#             await asyncio.sleep(1)
#             await message.edit(content=frame)

@bot.command(name='framedle')
@commands.cooldown(1, 60, commands.BucketType.guild)
async def framedle(ctx, *args):
    framedleView = PlayFramedle()
    await ctx.send("Play Framedle", view=framedleView)

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
            e.add_field(name=helpMsg['resetBingo']['name'], value=helpMsg['resetBingo']['description'], inline=False)
            e.add_field(name=helpMsg['changeBingo']['name'], value=helpMsg['changeBingo']['description'], inline=False)
    e.add_field(name=helpMsg['bingo']['name'], value=helpMsg['bingo']['description'], inline=False)
    e.add_field(name=helpMsg['connect']['name'], value=helpMsg['connect']['description'], inline=False)
    e.add_field(name=helpMsg['framedle']['name'], value=helpMsg['framedle']['description'], inline=False)
    e.add_field(name=helpMsg['special']['name'], value=helpMsg['special']['description'], inline=False)
    # e.set_image(url="https://cdn.discordapp.com/emojis/575642684006334464.png?size=40")
    e.set_footer(text="Made by Fraulk", icon_url="https://cdn.discordapp.com/avatars/192300712049246208/0663e3577e2759aa2ee0b75a4ec8f0cc.webp?size=128")
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
# TODO : make the bot detect birthday on message
# TODO : i should adapt the code for tiny pfp
# TODO : when !connect without mention, let every one to be the opponent
# TODO : Would actually help if we had an automated system of sorts, maybe adding a specific reaction on images you think are nice, and then the bot posts your link in the second look channel after a couple of days

bot.run(API_KEY)
