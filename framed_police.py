import os
import time
import random
import asyncio
import datetime
from threading import Timer

from vars import *
from app_commands import *
from functions import *
from wordle import *
from guess_the_vp import *

# pip install -U git+https://github.com/Rapptz/discord.py

# https://discord.com/api/oauth2/authorize?client_id=873628046194778123&permissions=543582186560&scope=bot

@bot.event
async def on_ready():
    print(f"{bot.user} logged in")
    if not os.path.isfile('./tempBingo.png'):
        recreateBingo(emptyBingo)
    bot.dispatch("today_gallery")
    bot.dispatch("new_day")

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
    elif message.channel.id == HOFChannel:
        await notifyHOFedUser(message)
    elif message.content.lower() == "good bot":
        await message.add_reaction(random.choice(goodReaction))
        await react(message, "good", bot.user.avatar)
    elif message.content.lower() == "bad bot":
        await message.add_reaction(random.choice(badReaction))
        await react(message, "bad", bot.user.avatar)
    elif message.content.lower() == "horny bot":
        await message.add_reaction(random.choice(hornyReaction))
        await react(message, "horny", bot.user.avatar)
    elif "https://framedsc.com/HallOfFramed/?" in message.content:
        await loadImagesFromHOF(message.content, message.channel)
    elif isGVPRunning and guessVpThread != None and message.channel.id == guessVpThread.id:
        await checkGVPWinner(message, currentAuthor)
    elif message.content.lower() in trigger_words:
        await message.reply(trigger_responses[trigger_words.index(message.content.lower())])
    # elif "https://twitter.com/" in message.content.lower():
    #     await replaceTwitterLink(message)
    # elif message.channel.id == HOFunChannel:
    #     await saveHOFun(message)
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
            print('---------------------------------------- Shots from ' + message.author.name + "#" + message.author.discriminator + ' deleted')
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

@bot.event
async def on_reaction_add(reaction, user):
    if reaction.message.channel.id != SYSChannel:
        return
    if (reaction.is_custom_emoji() and reaction.emoji.id in banned_custom_emojis) or (not reaction.is_custom_emoji() and reaction.emoji in banned_unicode_emojis):
        if user.id != reaction.message.author.id:
            await reaction.remove(user)

# @bot.event
# async def on_command_error(event_method, *args, **kwargs):
#     print(event_method)
#     print(args)
#     print(kwargs)

@bot.event
async def on_error(ctx, error, *args):
    if isinstance(error, discord.ext.commands.errors.MissingAnyRole):
        await ctx.send(f"Sorry but you can't use that command <@{ctx.author.id}>")
    if isinstance(error, discord.app_commands.errors.MissingRole):
        await ctx.send(f"Sorry but you can't use that command <@{ctx.author.id}>")

@bot.hybrid_command(name='change_delay', help='Change the delay after reaching the limit for posting shots, with number of seconds')
@app_commands.rename(arg='delay')
@app_commands.describe(arg='The delay to wait before uploading other shots')
@commands.has_any_role(549988038516670506, 549988228737007638, 874375168204611604)
async def changeDelay(ctx, arg):
    changeCurrentDelay(ctx, arg)
    await ctx.send(f"Delay has been changed to {arg}")

@bot.hybrid_command(name='change_limit', help='Change the limit for posting shots')
@app_commands.rename(arg='limit')
@app_commands.describe(arg='The limit of shot to upload within the current delay, 86400 = 24h, 43200 = 12h')
@commands.has_any_role(549988038516670506, 549988228737007638, 874375168204611604)
async def changeLimit(ctx, arg):
    changeCurrentLimit(ctx, arg)
    await ctx.send(f"Limit has been changed to {arg}")

@bot.hybrid_command(name='current_value', help='Shows the current values for DELAY and LIMIT')
@commands.has_any_role(549988038516670506, 549988228737007638, 874375168204611604)
async def currentValue(ctx):
    print(f"'currentValue' command has been used by {ctx.author.name}#{ctx.author.discriminator}")
    limit, delay = getCurrentValue()
    await ctx.send(f"LIMIT = {limit}\nDELAY = {delay}")

@bot.hybrid_command(name='dumpr', help='Shows data about those who reached the limit and have been dm\'d by the bot')
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

@bot.hybrid_command(name='dump', help='Shows data about everybody')
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

@bot.hybrid_command(name='check', help='Shows data about you')
async def check(ctx: commands.Context):
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

# App commands equivalent in app_commands.py 
@bot.command(name='reset', help='Resets the count for a person, with his ID as parameter')
@commands.has_any_role(549988038516670506, 549988228737007638, 874375168204611604)
async def reset(ctx, arg):
    response = await resetUser(arg)
    print(f"'reset' command has been used by {ctx.author.name}#{ctx.author.discriminator}")
    await ctx.send(response)

@bot.hybrid_command(name='reset_all', help='Resets the count for everyone')
@commands.has_any_role(549988038516670506, 549988228737007638, 874375168204611604)
async def resetAll(ctx):
    await resetAllUsers()
    print(f"'resetAll' command has been used by {ctx.author.name}#{ctx.author.discriminator}")
    await ctx.send("Everyone has been reset")

# @bot.command(name='countShots', help='Count the last 7 days shots or from a certain date')
# @commands.has_any_role(549988038516670506, 549988228737007638, 874375168204611604)
# async def countShots(ctx, *args):
#     week_ago = datetime.datetime.today() - datetime.timedelta(days=7)
#     print(week_ago)
#     channel = bot.get_channel(SYSChannel)
#     messages = await channel.history(limit=None, after=week_ago).flatten()
#     print(len(messages))

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
        e = FramedEmbed
        data = await over2000(data, gameNames, args)
    await ctx.send(content=data, embed=e) if len(data) < 2000 else await ctx.send("Search query is too vague, there are too many results to show")

@bot.command(name='guide', help='Checks if a game have a guide on the site. ex: !guide cyberpunk')
async def guide(ctx, *args):
    async with ctx.typing():
        data, gameNames = await getGuides(args)
        if len(data) == 0: data = random.choice(notFound).format(' '.join(args))
        e = FramedEmbed
        data = await over2000(data, gameNames, args)
    await ctx.send(content=data, embed=e) if len(data) < 2000 else await ctx.send("Search query is too vague, there are too many results to show")

@bot.command(name='cheat', help='Checks if a game have cheat tables on the site. ex: !cheat alien')
async def cheat(ctx, *args):
    async with ctx.typing():
        data, gameNames = await getCheats(args)
        if len(data) == 0: data = random.choice(notFound).format(' '.join(args))
        e = FramedEmbed
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
        if random.randint(0, 100) <= 1:
            data += "\n**╘** : <https://discord.com/channels/549986543650078722/549986543650078725/802956969824092188>"
            # https://discord.com/channels/549986543650078722/549986930071175169/562313767656882217 # > jim's
        e = FramedEmbed
        data = await over2000(data, camGameNames + uuuGameNames + guideGameNames + cheatGameNames, args)
    await ctx.send(content=data, embed=e) if len(data) < 2000 else await ctx.send("Search query is too vague, there are too many results to show") # + str(len(data))

@bot.command(name='tools', help='Alias for !tool, because a lotta people does the mistake lol')
async def tools(ctx, *args):
    await tool(ctx, *args)

@bot.command(name="bingo", help="Play to the framed bingo !")
@commands.cooldown(1, 30, commands.BucketType.guild)
async def bingo(ctx, *args):
    bingoView = EphemeralBingo(ctx.channel.id) # ctx as param
    # e = discord.Embed(title="Bingo card",
    #                   url="https://discord.com/channels/549986543650078722/549986543650078725/914511447176921098",
    #                   description="",
    #                   color=0x9a9a9a
    # )
    # e.set_image(url="https://cdn.discordapp.com/attachments/549986543650078725/914511446975582218/bingo2.png")
    await ctx.send("", view=bingoView, file=discord.File('tempBingo.png'))

@bot.hybrid_command(name="reset_bingo", help="Manually reset the bingo")
@commands.has_any_role(549988038516670506, 549988228737007638, 874375168204611604)
async def resetBingo(ctx):
    resetBingoBoard()
    await ctx.send("The bingo card has been reset")

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
    lastBingo = Image.open('./tempBingo.png')
    lastBingo.save('./lastBingo.png')
    resetBingoBoard()
    saveBingo()
    channel = bot.get_channel(channelId)
    await channel.send("The bingo has been completed !", file=discord.File('./lastBingo.png'))

# @commands.has_any_role(549988038516670506, 549988228737007638, 874375168204611604)
# @bot.command(name="addTitle", help="Add a game title and all his alts")
# async def addTitle(ctx, *args):
#     global titleAlts
#     simpleArg = None
#     simpleName = None
#     args = ' '.join(args)
#     args = args.replace("'", "\\'")
#     if args == '': return
#     if args.find(';') > -1:
#         simpleArg = args.split(';')[1].lstrip(' ')
#         simpleName = args.split(';')[0].rstrip(' ')
#         if simpleArg == '' or simpleName == '': return
#         if simpleArg.find(',') > -1:
#             simpleArg = simpleArg.split(',')
#             simpleArg = [e.lstrip(' ').rstrip(' ') for e in simpleArg]
#         index = next((i for i, item in enumerate(titleAlts) if item.get(simpleName) is not None), None)
#         if index is not None:
#             titleAlts[index][simpleName].append(simpleArg) if isinstance(simpleArg, str) else titleAlts[index][simpleName].extend(simpleArg)
#         else:
#             alts = {}
#             alts[simpleName] = [simpleArg] if isinstance(simpleArg, str) else simpleArg
#             titleAlts.append(alts)
#         saveTitleAlts()
#         await ctx.message.add_reaction('✅')
#         # print(titleAlts)
#         # print(next((i for i, item in enumerate(titleAlts) if simpleArg in item[simpleName]), None))

# @commands.has_any_role(549988038516670506, 549988228737007638, 874375168204611604)
# @bot.command(name="removeTitle", help="Remove a game title and all his alts")
# async def removeTitle(ctx, *args):
#     global titleAlts
#     args = ' '.join(args)
#     args = args.replace("'", "\\'")
#     if args == '': return
#     titleAlts[:] = [d for d in titleAlts if d.get(args) is None]
#     saveTitleAlts()
#     await ctx.message.add_reaction('✅')

# @bot.command(name="showTitle", help="Shows a game title and all his alts")
# async def showTitle(ctx, *args):
#     global titleAlts
#     content = ""
#     args = ' '.join(args)
#     args = args.replace("'", "\\'")
#     if args == '':
#         i = 0
#         for d in titleAlts:
#             gameTitle = next(iter(d))
#             content += f"**{gameTitle}** : {', '.join(d.get(gameTitle))}\n"
#             if i % 15 == 0:
#                 await ctx.send(content if len(content) < 2000 else "Too much data to send, <@192300712049246208> failed his job so please bully him and make him fix me")
#                 content = ""
#             i += 1
#     else:
#         index = next((i for i, item in enumerate(titleAlts) if item.get(args) is not None), None)
#         if index is not None:
#             gameTitle = next(iter(titleAlts[index]))
#             content += f"**{gameTitle}** : {', '.join(titleAlts[index].get(args))}"
#         else:
#             content = "Unknown game"
#     await ctx.send(content if len(content) < 2000 else "Too much data to send, <@192300712049246208> failed his job so please bully him and make him fix me")

# @bot.command(name="connect")
# async def connect(ctx, arg, arg2 = None, arg3 = None):
#     view = Confirm([ctx.message.author.id, ctx.message.mentions[0].id], arg2, arg3)
#     await ctx.send(content=f"{ctx.message.author.mention} wants to play connect4 with you {ctx.message.mentions[0].mention}, will you accept ?", view=view)
#     # Wait for the View to stop listening for input...
#     await view.wait()

@bot.hybrid_command(name='framedle', help="Play framedle ! A Framed rip-off of the Wordle game")
@commands.cooldown(1, 60, commands.BucketType.guild)
async def framedle(ctx):
    framedleView = PlayFramedle()
    await ctx.send("Play Framedle", view=framedleView)

guessVpThread = None
isGVPRunning = False
currentShot = None
currentAuthor = None
GVPChannel = None
@bot.hybrid_command(name='gvp', help="Play GVP, aka Guess the Virtual Photographer")
async def gvp(ctx):
    if PROD == False: return
    global isGVPRunning
    global guessVpThread
    global currentShot
    global currentAuthor
    global GVPChannel
    if isGVPRunning:
        await ctx.send(f"An instance of the game is already running here : <#{guessVpThread.id}>")
        return
    isGVPRunning = True
    GVPChannel = ctx.channel
    currentShot = await getHofShot(ctx)
    print(currentShot)
    if type(currentShot) is not dict or type(currentShot['author']) is not str or type(currentShot['colorName']) is not str or type(currentShot['thumbnailUrl']) is not str:
        print("gvp error")
        isGVPRunning = False
    currentAuthor = discord.utils.find(lambda m: m.id == int(currentShot['author']), ctx.guild.members)
    print(currentAuthor.name, currentAuthor.display_name, currentAuthor.nick, currentAuthor.global_name)
    print(currentShot['author'])
    e = discord.Embed(title="Guess the VP !",
                      description="Who's that ~~pokemon~~ VP !?",
                      color=colorNames[currentShot['colorName']])
    e.set_image(url=currentShot['thumbnailUrl'])
    message = await ctx.send(embed=e)
    guessVpThread = await message.create_thread(name="Guess the VP!", auto_archive_duration=60)

@bot.event
async def on_guess_vp_winner(vp, winner):
    global guessVpThread
    global isGVPRunning
    isGVPRunning = False
    await guessVpThread.delete()
    guessVpThread = None
    gamename = currentShot['gameName'] if currentShot != None else "unknown"
    await GVPChannel.send(f"<@{winner.id}> found the vp! It was {vp.display_name} ({vp.name}) on the game: {gamename}")

@bot.event
async def on_thread_delete(thread):
    global guessVpThread
    if guessVpThread != None and thread.id == guessVpThread.id:
        global isGVPRunning
        isGVPRunning = False
        guessVpThread = None

@bot.event
async def on_thread_remove(thread):
    global guessVpThread
    if guessVpThread != None and thread.id == guessVpThread.id:
        await guessVpThread.delete()
        global isGVPRunning
        isGVPRunning = False
        guessVpThread = None

@bot.event
async def on_thread_update(before, after):
    global guessVpThread
    if guessVpThread != None and after.id == guessVpThread.id and after.archived:
        await guessVpThread.delete()
        global isGVPRunning
        isGVPRunning = False
        guessVpThread = None

@commands.has_any_role(549988038516670506, 549988228737007638, 874375168204611604)
@bot.hybrid_command(name='reset_gvp', help="Reset last GVP game")
async def resetGVP(ctx):
    global isGVPRunning
    isGVPRunning = False
    if guessVpThread != None:
        await guessVpThread.delete()
        await ctx.send("Last GVP game has been reset")

@commands.has_any_role(549988038516670506, 549988228737007638, 874375168204611604)
@bot.command(name='getScore')
async def getScore(ctx, *args):
    if len(args) == 0:
        await ctx.send("No ID specified")
        return
    async with ctx.typing():
        channel = bot.get_channel(SYSChannel)
        if len(args) == 1:
            await ctx.send(await getShotReactions(await channel.fetch_message(args[0])))
        elif len(args) > 1:
            reactList = [await getShotReactions(await channel.fetch_message(r)) for r in args]
            await ctx.send(reactList)

# Test command for HOF notify
# @commands.has_any_role(549988038516670506, 549988228737007638, 874375168204611604)
# @bot.command(name='embed')
# async def embed(ctx, *args):
#     e = FramedEmbed
#     e.set_author(name="Shot by Fraulk#6318")
#     channel = bot.get_channel(HOFChannel)
#     await channel.send(embed=e)

# Test command for today's gallery, don't forget to hardcode the output channel id to something else than framed second look channel
@commands.has_any_role(549988038516670506, 549988228737007638, 874375168204611604)
@bot.command(name='tg')
async def tg(ctx):
    await todaysGallery()

# @commands.has_any_role(549988038516670506, 549988228737007638, 874375168204611604)
# @bot.command(name='getLastYearMessages')
# async def getLastYearMessages(ctx):
#     channel = bot.get_channel(HOFChannel)
#     # print(datetime.datetime(2022, 1, 1, 0, 0, 0))
#     # messages = [message async for message in channel.history(limit=None, after=datetime.datetime(2022, 1, 1, 0, 0, 0))]
#     async for message in channel.history(limit=None, after=datetime.datetime(2022, 1, 1, 0, 0, 0)):
#         print(message)

@bot.tree.command(description='Shows the list of commands the bot can execute. The bot\'s response will be visible only to you')
async def help(interaction: discord.Interaction):
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
    if interaction.guild is not None:
        FoudersEd = discord.utils.get(interaction.guild.roles, id=549988038516670506)
        mods = discord.utils.get(interaction.guild.roles, id=549988228737007638)
        testFoudersEd = discord.utils.get(interaction.guild.roles, id=874375168204611604)
        if FoudersEd in interaction.user.roles or mods in interaction.user.roles or testFoudersEd in interaction.user.roles:
            e.add_field(name=helpMsg['getScore']['name'], value=helpMsg['getScore']['description'], inline=False)
            e.add_field(name=helpMsg['changeDelay']['name'], value=helpMsg['changeDelay']['description'], inline=False)
            e.add_field(name=helpMsg['changeLimit']['name'], value=helpMsg['changeLimit']['description'], inline=False)
            e.add_field(name=helpMsg['currentValue']['name'], value=helpMsg['currentValue']['description'], inline=False)
            e.add_field(name=helpMsg['dump']['name'], value=helpMsg['dump']['description'], inline=False)
            e.add_field(name=helpMsg['dumpR']['name'], value=helpMsg['dumpR']['description'], inline=False)
            e.add_field(name=helpMsg['reset']['name'], value=helpMsg['reset']['description'], inline=False)
            e.add_field(name=helpMsg['resetAll']['name'], value=helpMsg['resetAll']['description'], inline=False)
            e.add_field(name=helpMsg['resetBingo']['name'], value=helpMsg['resetBingo']['description'], inline=False)
            e.add_field(name=helpMsg['resetGVP']['name'], value=helpMsg['resetGVP']['description'], inline=False)
            e.add_field(name=helpMsg['changeBingo']['name'], value=helpMsg['changeBingo']['description'], inline=False)
    e.add_field(name=helpMsg['bingo']['name'], value=helpMsg['bingo']['description'], inline=False)
    e.add_field(name=helpMsg['connect']['name'], value=helpMsg['connect']['description'], inline=False)
    e.add_field(name=helpMsg['framedle']['name'], value=helpMsg['framedle']['description'], inline=False)
    e.add_field(name=helpMsg['gvp']['name'], value=helpMsg['gvp']['description'], inline=False)
    e.add_field(name=helpMsg['special']['name'], value=helpMsg['special']['description'], inline=False)
    # e.set_image(url="https://cdn.discordapp.com/emojis/575642684006334464.png?size=40")
    # e.set_footer(text="Made by Fraulk", icon_url="https://cdn.discordapp.com/avatars/192300712049246208/0663e3577e2759aa2ee0b75a4ec8f0cc.webp?size=128")
    # does the gif version of my pfp still exists after nitro ends ? https://cdn.discordapp.com/avatars/192300712049246208/a_c7d1c089c53b152ed0b3b00304fa3307.gif?size=40
    await interaction.response.send_message(embed=e, ephemeral=True)

@bot.event
async def on_today_gallery():
    await asyncio.sleep(secs)
    await todaysGallery()

@bot.event
async def on_today_gallery_end():
    await asyncio.sleep(datetime.timedelta(days=1).total_seconds())
    await todaysGallery()

@bot.event
async def on_new_day():
    await checkBirthdayNames()
    x = datetime.datetime.today()
    y = x.replace(day=x.day, hour=0, minute=0, second=0, microsecond=0) + datetime.timedelta(days=1)
    delta_t = y - x
    secs = delta_t.total_seconds()
    await asyncio.sleep(secs)
    print("new day")
    await checkBirthdayNames()

@bot.event
async def on_new_day_end():
    await asyncio.sleep(datetime.timedelta(days=1).total_seconds())
    await checkBirthdayNames()

async def checkBirthdayNames():
    for userId, birthday in birthDays.items():
        aliveFor = datetime.datetime.now().timestamp() - birthday["birthday"].timestamp()
        daysAlive = aliveFor / 60 / 60 / 24
        aliveForText = birthday["template"].replace("{XXXX}", str(round(daysAlive)))
        newName = f"{birthday['name']} {aliveForText}"
        guild = bot.get_guild(GUILD_ID)
        member = guild.get_member(userId)
        if (len(newName) > 32):
            DMChannel = await member.create_dm()
            await DMChannel.send(f"The name cannot surpass 32 characters, please make the template shorter\nName: {birthday['name']} = {len(birthday['name'])} characters\nTemplate: {aliveForText} = {len(aliveForText)} characters\nTotal: {len(birthday['name']) + len(aliveForText)} + 1 space")
            continue
        print(f"Name: {birthday['name']} = {len(birthday['name'])} characters\nTemplate: {aliveForText} = {len(aliveForText)} characters\nTotal: {len(birthday['name']) + len(aliveForText)} + 1 space")
        await member.edit(nick=newName) # needs "Manage nicknames" permission
    bot.dispatch("new_day_end")

# i should put this in a function and call it for the sleep and so i could just have one event function, but oh god i'm so lazy
x = datetime.datetime.today()
y = x.replace(day=x.day, hour=18, minute=0, second=0, microsecond=0) + datetime.timedelta(days=1)
delta_t = y - x
secs = delta_t.total_seconds()
# secs = 60

# BUG : when multiple person spamm shots, sometime the bot ignore the event/code and some shots bypass the limit, it may be caused by the fact that 
# 1. 6th shot get deleted 2. on_message_delete event then decrease user count 3. bot can't keep up so the limit decrease without increasing first or smthng or some events are simply ignored
# embeds are sometimes ignored, so a 6th shot can also bypass
# TODO : also jim said it wasn't necessary but since you said you're bored maybe a counter of shots in share-your-shot and hall-of-framed then every weekend it posts a summary of the week's numbers or something
# https://stackoverflow.com/questions/65765951/discord-python-counting-messages-from-a-week-and-save-them
# FIXME : "older shot" triggered false positive, f
# TODO : i should limit the character to 3 min in cam and uuu commands
# TODO : put things in embeds : https://leovoel.github.io/embed-visualizer/
# FIXME : catch commands used without arguments
# TODO : make the bot detect birthday on message
# TODO : i should adapt the code for tiny pfp
# TODO : remove reactions limit for today's gallery
# TODO : don't reset the past days gallery
# TODO : don't take hoffed shot

bot.run(API_KEY)

# Changelog :
# !help command have been replaced with /help, and doesn't work anymore in private message, but the response will be visible only to you
# Most commands are now working with slash command, just type "/" and let the autocompletion do his job, but the old way with "!" still works for some
# The old commands don't have uppercase letter anymore, ex: !currentValue -> !current_value
# The bot now notify you when you get HOFed
# You can now use the `/connect` command without specifying someone, and if anybody accept, the game will start with them
# Second look website images will now load faster, but message building on #second-look channel will take a bit longer
# Bot will now make a "today's gallery" every day at 16:00 UTC (<t:1658332800:t>)
# You can also use the bot to create a second look list now, by right-clicking the message in #share-your-shot, then going in the "Apps >" section and "Add to your second ..."
# Then when you want to post it, use the "/post_second_look_list" command

# TODO : before updating :
# 1. update discord.py : pip install -U git+https://github.com/Rapptz/discord.py
# 2. ask for a channel id for the "report to admin" cmd or use the channel used for saying when someone joined or left
# 3. ask a mod to update bot's right using this link : https://discord.com/api/oauth2/authorize?client_id=873628046194778123&permissions=543582186560&scope=bot
# 4. don't forget to !sync