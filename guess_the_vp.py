import discord
import requests
import json
import random

from vars import *

lastShots = []
blacklist = ["158655628531859456", "411108650720034817"]
bufferSize = 20
async def getHofShot(ctx):
    response = requests.get("https://raw.githubusercontent.com/originalnicodrgitbot/hall-of-framed-db/main/shotsdb.json", allow_redirects=True)
    assert response.status_code == 200, 'Wrong status code'
    resJson = json.loads(response.content)
    # print(resJson["_default"][str(random.randint(1, len(resJson["_default"])))])
    while True:
        print("loop")
        try:
            shot = resJson["_default"][str(random.randint(1, len(resJson["_default"])))]
        except:
            continue
        author = shot['author']
        if author in blacklist or author in lastShots:
            print(f"author ({author}) either is blacklisted or was already shown in the last {bufferSize} games")
            continue
        member = discord.utils.find(lambda m: m.id == int(author) or m.id == int(author), ctx.guild.members)
        if member != None:
            break
    lastShots.insert(0, author)
    if len(lastShots) > bufferSize:
        lastShots.pop()
    return shot

message_count = 0
async def checkGVPWinner(msg, author):
    global message_count
    message_count += 1
    member = author
    if message_count == 20:
        await msg.channel.send(f"Name: {member.name[:1]}\nDisplay name: {member.display_name[:1]}\nGlobal name: {member.global_name[:1]}\nNick: {member.nick[:1] if member.nick != None else 'None'}")
    if message_count == 35:
        await msg.channel.send(f"Name: {member.name[:2]}\nDisplay name: {member.display_name[:2]}\nGlobal name: {member.global_name[:1]}\nNick: {member.nick[:1] if member.nick != None else 'None'}")
    if member != None \
      and member.name.lower() == msg.content.lower() \
      or member.display_name.lower() == msg.content.lower() \
      or member.global_name.lower() == msg.content.lower() \
      or member.nick.lower() == msg.content.lower():
        message_count = 0
        bot.dispatch("guess_vp_winner", member, msg.author)
        print(msg.author.name + " found the VP, " + member.name)

specialNames = {"Romаn": "Roman", "MAXPΞR": "MAXPER", "Catuṣkoṭi": "Catuskoti", "bohdan🇺🇦": "bohdan", "Loyd✦": "Loyd"}
def compareNames(member, msgContent):
    if member.name in specialNames.keys() and msgContent.lower() == specialNames[member.name].lower(): return True
    return member.name.lower() == msgContent.lower() or member.display_name.lower() == msgContent.lower()