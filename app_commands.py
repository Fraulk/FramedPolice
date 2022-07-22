from typing import Optional
from discord import app_commands

from vars import *
from functions import *

# OLD COMMANDS APP COMMAND EQUIVALENT >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

@bot.tree.command(name='reset', description="Resets the count for a person, with his his @name as a parameter")
@app_commands.describe(member='The member you want to reset')
@app_commands.checks.has_role([549988038516670506, 549988228737007638, 874375168204611604])
async def resetAC(interaction: discord.Interaction, member: discord.Member):
    if member is None:
        await interaction.response.send_message("Please provide the name of the user")
    response = await resetUser(member.id)
    print(f"'reset' command has been used by {interaction.user}")
    await interaction.response.send_message(response)

@bot.tree.command(name='cam', description='Search for a freecams or a tool by string. ex: !cam cyberpunk 2077')
@app_commands.describe(gamename='The name of the game')
async def camAC(interaction: discord.Interaction, gamename: str):
    data, gameNames = await getCams(gamename)
    if len(data) == 0: data = random.choice(notFound).format(gamename)
    e = discord.Embed(title="Freecams, tools and stuff",
                      url="https://docs.google.com/spreadsheets/d/1lnM2SM_RBzqile870zG70E39wuuseqQE0AaPW-P1p5E/edit#gid=0",
                      description="Based on originalnicodr spreadsheet",
                      color=0x3498DB)
    e.set_thumbnail(url="https://cdn.discordapp.com/avatars/128245457141891072/0ab765d7c5bd8fb373dbd3627796aeec.png?size=128")
    data = await over2000(data, gameNames, gamename)
    await interaction.response.send_message(content=data, embed=e, ephemeral=True) if len(data) < 2000 else await interaction.response.send_message("Search query is too vague, there are too many results to show", ephemeral=True)

@bot.tree.command(name='uuu', description='Checks if a game is compatible with UUU. ex: !uuu the ascent')
@app_commands.describe(gamename='The name of the game')
async def uuuAC(interaction: discord.Interaction, gamename: str):
    data, gameNames = await getUUU(gamename)
    if len(data) == 0: data = random.choice(notFound).format(gamename)
    e = FramedEmbed
    data = await over2000(data, gameNames, gamename)
    await interaction.response.send_message(content=data, embed=e, ephemeral=True) if len(data) < 2000 else await interaction.response.send_message("Search query is too vague, there are too many results to show", ephemeral=True)

@bot.tree.command(name='guide', description='Checks if a game have a guide on the site. ex: !guide cyberpunk')
@app_commands.describe(gamename='The name of the game')
async def guideAC(interaction: discord.Interaction, gamename: str):
    data, gameNames = await getGuides(gamename)
    if len(data) == 0: data = random.choice(notFound).format(gamename)
    e = FramedEmbed
    data = await over2000(data, gameNames, gamename)
    await interaction.response.send_message(content=data, embed=e, ephemeral=True) if len(data) < 2000 else await interaction.response.send_message("Search query is too vague, there are too many results to show", ephemeral=True)

@bot.tree.command(name='cheat', description='Checks if a game have cheat tables on the site. ex: !cheat alien')
@app_commands.describe(gamename='The name of the game')
async def cheatAC(interaction: discord.Interaction, gamename: str):
    data, gameNames = await getCheats(gamename)
    if len(data) == 0: data = random.choice(notFound).format(gamename)
    e = FramedEmbed
    data = await over2000(data, gameNames, gamename)
    await interaction.response.send_message(content=data, embed=e, ephemeral=True) if len(data) < 2000 else await interaction.response.send_message("Search query is too vague, there are too many results to show", ephemeral=True)

@bot.tree.command(name='tool', description='Checks if a game have a guide, cam or works with UUU. ex: !tool cyberpunk')
@app_commands.describe(gamename='The name of the game')
async def toolAC(interaction: discord.Interaction, gamename: str):
    cams, camGameNames = await getCams(gamename)
    uuus, uuuGameNames = await getUUU(gamename)
    guides, guideGameNames = await getGuides(gamename)
    cheats, cheatGameNames = await getCheats(gamename)
    data = ""
    if len(cams) > 0:
        data += cams + "----\n" if len(uuus) > 0 or len(guides) > 0 or len(cheats) > 0 else cams
    if len(uuus) > 0:
        data += uuus + "----\n" if len(guides) > 0 or len(cheats) > 0 else uuus
    if len(guides) > 0:
        data += guides + "----\n" if len(cheats) > 0 else guides
    if len(cheats) > 0:
        data += cheats
    if len(data) == 0: data = random.choice(notFound).format(gamename)
    if random.randint(0, 9) <= 1:
        data += "\n**╘** : <https://discord.com/channels/549986543650078722/549986543650078725/893340504719249429>"
    e = FramedEmbed
    data = await over2000(data, camGameNames + uuuGameNames + guideGameNames + cheatGameNames, gamename)
    await interaction.response.send_message(content=data, embed=e, ephemeral=True) if len(data) < 2000 else await interaction.response.send_message("Search query is too vague, there are too many results to show", ephemeral=True) # + str(len(data))

@bot.tree.command(name="bingo", description="Play to the framed bingo !")
@commands.cooldown(1, 30, commands.BucketType.guild)
async def bingoAC(interaction: discord.Interaction):
    bingoView = EphemeralBingo(interaction.channel.id)
    await interaction.response.send_message("", view=bingoView, file=discord.File('tempBingo.png'), ephemeral=True)

@app_commands.checks.has_role([549988038516670506, 549988228737007638, 874375168204611604])
@bot.tree.command(name="change_bingo", description="Change the bingo image (change takes effect at the next round)")
async def changeBingo(interaction: discord.Interaction, file: discord.Attachment):
    if file.url[-3:] == "png":
        newBingoRaw = requests.get(file.url, stream=True).raw
        newBingo = Image.open(newBingoRaw)
        newBingo.save('images/bingo.png')
        await interaction.response.send_message("The new bingo image has been set !\nThe new bingo will be used for the next round", ephemeral=True)
    else:
        await interaction.response.send_message("Oops, something went wrong...\nPlease send a valid **PNG** file attached to the command message", ephemeral=True)

@bot.tree.command(name="connect", description="Play connect 4")
@app_commands.describe(opponent="Choose your opponent !", emoji1="Use an emoji as your token", emoji2="Use an emoji as the opponent's token")
@app_commands.rename(emoji1="your_emoji", emoji2="opponents_emoji")
async def connect(interaction: discord.Interaction, opponent: discord.Member = None, emoji1: str = None, emoji2: str = None):
    opponentId = opponent.id if opponent is not None else None
    view = Confirm([interaction.user.id, opponentId], emoji1, emoji2)
    if opponentId is not None:
        await interaction.response.send_message(content=f"{interaction.user.mention} wants to play connect4 with you {opponent.mention}, will you accept ?", view=view)
    else:
        await interaction.response.send_message(content=f"{interaction.user.mention} wants to play connect4 with someone, will you accept ?", view=view)
    # Wait for the View to stop listening for input...
    await view.wait()

# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

@bot.tree.context_menu(name="Show join date")
async def show_join_date(interaction: discord.Interaction, member: discord.Member):
    await interaction.response.send_message(f'{member} joined at {discord.utils.format_dt(member.joined_at)}', ephemeral=True)

@bot.tree.command()
@app_commands.describe(member='The member you want to get the joined date from; defaults to the user who uses the command')
async def joined(interaction: discord.Interaction, member: Optional[discord.Member] = None):
    """Says when a member joined."""
    # If no member is explicitly provided then we use the command user here
    member = member or interaction.user

    # The format_dt function formats the date time into a human readable representation in the official client
    await interaction.response.send_message(f'{member} joined {discord.utils.format_dt(member.joined_at)}')

@bot.tree.context_menu(name='Report to admins')
async def report_message(interaction: discord.Interaction, message: discord.Message):
    # We're sending this response message with ephemeral=True, so only the command executor can see it
    await interaction.response.send_message(
        f'Thanks for reporting this message by {message.author.mention} to our moderators.', ephemeral=True
    )

    # Handle report by sending it into a log channel
    log_channel = interaction.guild.get_channel(ReportChannel)  # replace with your channel id

    embed = discord.Embed(title='Reported Message')
    if message.content:
        embed.description = message.content

    embed.set_author(name=message.author.display_name, icon_url=message.author.display_avatar.url)
    embed.timestamp = message.created_at

    url_view = discord.ui.View()
    url_view.add_item(discord.ui.Button(label='Go to Message', style=discord.ButtonStyle.url, url=message.jump_url))

    await log_channel.send(embed=embed, view=url_view)

@commands.has_any_role(549988038516670506, 549988228737007638, 874375168204611604)
@bot.command(name='sync', help='Sync slash commands')
async def sync(ctx):
    guild = discord.Object(id=GUILD_ID)  # you can use a full discord.Guild as the method accepts a Snowflake
    bot.tree.copy_global_to(guild=guild)
    await bot.tree.sync(guild=guild)

@bot.tree.context_menu(name='Add to your second look list')
async def addSLList(interaction: discord.Interaction, message: discord.Message):
    if message.channel.id != SYSChannel:
        await interaction.response.send_message(f"Sorry but this message doesn't come from <#{SYSChannel}> channel", ephemeral=True)
        return
    print(secondLookList)
    if interaction.user.id in secondLookList:
        if len(secondLookList[interaction.user.id]) < 20:
            secondLookList[interaction.user.id].append(message.jump_url)
        else:
            await interaction.response.send_message(f"You can't have more than 20 shots, please post the ones you currently have", ephemeral=True)
            return
    else:
        secondLookList[interaction.user.id] = [message.jump_url]
    await saveSLList()
    url_view = discord.ui.View()
    url_view.add_item(discord.ui.Button(label='Go back to the shot', style=discord.ButtonStyle.url, url=message.jump_url))
    await interaction.response.send_message(f"The shot has been added to your second look list", view=url_view, ephemeral=True)

@bot.tree.command(name="post_second_look_list", description="Post all the shot you added from the context menu")
async def postSLList(interaction: discord.Interaction):
    if interaction.user.id in secondLookList and len(secondLookList[interaction.user.id]) > 0:
        if interaction.channel_id == SLChannel:
            SLMessage = f"{interaction.user.mention}'s second look list :\n"
            for link in secondLookList[interaction.user.id]:
                SLMessage += f"{link}\n"
            await interaction.response.send_message(SLMessage)
            secondLookList[interaction.user.id] = []
            await saveSLList()
        else:
            await interaction.response.send_message(f"Please use the command in the <#{SLChannel}>", ephemeral=True)
    else:
        await interaction.response.send_message(f"You didn't add any shot to your list, please add some by right-clicking on a message in <#{SYSChannel}>, then click on 'Apps >' and 'Add to your second ...'", ephemeral=True)

# example
# secondloolist = {
#     '0000000000000000': ["linksetc"]
# }

async def saveSLList():
    with open('secondLookList.pkl', 'wb') as f:
        pickle.dump(secondLookList, f)

if os.path.isfile('./secondLookList.pkl'):
    with open('secondLookList.pkl', 'rb') as f:
        try:
            secondLookList = pickle.load(f)
        except EOFError:
            secondLookList = {}
else:
    secondLookList = {}
    with open('secondLookList.pkl', 'wb'): pass