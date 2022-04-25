import discord
import requests
import json
import random

from vars import *

async def getHofShot():
    response = requests.get("https://raw.githubusercontent.com/originalnicodrgitbot/hall-of-framed-db/main/shotsdb.json", allow_redirects=True)
    assert response.status_code == 200, 'Wrong status code'
    resJson = json.loads(response.content)
    # print(resJson["_default"][str(random.randint(1, len(resJson["_default"])))])
    try:
        return resJson["_default"][str(random.randint(1, len(resJson["_default"])))]
    except KeyError:
        return resJson["_default"][str(random.randint(1, len(resJson["_default"])))]

async def checkGVPWinner(msg, authorId):
    member = discord.utils.find(lambda m: m.name.lower() == msg.content.lower() or m.display_name.lower() == msg.content.lower(), msg.guild.members)
    if member != None and member.id == int(authorId):
        bot.dispatch("guess_vp_winner", member, msg.author)
        print(msg.author.name + " found the VP, " + member.name)