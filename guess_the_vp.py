import discord
import requests
import json
import random

from vars import *

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
            break
        member = discord.utils.find(lambda m: m.id == int(shot['author']) or m.id == int(shot['author']), ctx.guild.members)
        if member != None:
            break
    return shot

async def checkGVPWinner(msg, authorId):
    member = discord.utils.find(lambda m: m.name.lower() == msg.content.lower() or m.display_name.lower() == msg.content.lower(), msg.guild.members)
    if member != None and member.id == int(authorId):
        bot.dispatch("guess_vp_winner", member, msg.author)
        print(msg.author.name + " found the VP, " + member.name)