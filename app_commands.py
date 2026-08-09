from typing import Optional
from discord import app_commands, ui
from discord.interactions import Interaction
from discord.ext import commands

from vars import *
from functions import *
from betting import activePredictions, build_prediction_embed, PredictionView, close_prediction, auto_close_prediction, Prediction, parse_duration
from db_connector import betting_db, DB_PATH

# OLD COMMANDS APP COMMAND EQUIVALENT >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

@bot.tree.command(name='reset', description="Resets the count for a person, with his his @name as a parameter")
@app_commands.describe(member='The member you want to reset')
@app_commands.checks.has_role("Founders Edition")
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

# @bot.tree.command(name='tool', description='Checks if a game have a guide, cam or works with UUU. ex: !tool cyberpunk')
# @app_commands.describe(gamename='The name of the game')
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

@app_commands.checks.has_role("Founders Edition")
@bot.tree.command(name="change_bingo", description="Change the bingo image (change takes effect at the next round)")
async def changeBingo(interaction: discord.Interaction, file: discord.Attachment):
    if file.url.split(".")[-1][0:3] == "png":
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

@app_commands.checks.has_any_role(549988038516670506, 549988228737007638, 874375168204611604)
@bot.tree.command(name="echo", description="Have fun mods")
@app_commands.describe(text='The message to send', channel="The channel to send to")
async def echo(interaction: discord.Interaction, text: str, channel: discord.TextChannel = None):
    if channel is not None:
        await channel.send(content=text)
    else:
        await interaction.channel.send(content=text)
    await interaction.response.send_message(content="Message sent", ephemeral=True)

@app_commands.checks.has_any_role(549988038516670506, 549988228737007638, 874375168204611604)
@bot.tree.command(name="echo_dm", description="Have fun mods")
@app_commands.describe(text='The message to send', member="The member to send to")
async def echoDM(interaction: discord.Interaction, text: str, member: discord.Member):
    DMChannel = await member.create_dm()
    await DMChannel.send(content=text)
    await interaction.response.send_message(content="Message sent", ephemeral=True)

@bot.tree.command(name="emoji_text", description="Send a text to the bot and get it rendered with emojis")
@app_commands.describe(text="8 max w/o nitro and no custom emojis", emoji1="The emoji to write the text", emoji2="The emoji for the background")
@app_commands.rename(emoji1="text_emoji", emoji2="background_emoji")
async def connect(interaction: discord.Interaction, text: str, emoji1: str, emoji2: str = "<:air:927935249982300251>"):
    result = []
    splittedText = list(text.lower())
    emojis = [emoji2, emoji1]
    for _ in range(5):
        row = ''
        for j, lett in enumerate(splittedText):
            letter = lett if lett != ' ' else 'space'
            letterWidth = len(letters_dict[letter][0])
            spacePos = letterWidth - 1
            for k in range(letterWidth):
                row += emojis[letters_dict[letter][_][k]]
            if k == spacePos and j < len(splittedText) - 1:
                row += emojis[0]
        result.append(row)
    emojified_message = '\n'.join(result)
    if len(emojified_message) > 2000:
        await interaction.response.send_message(content=f"The emoji length is a bit too long. Please try using a shorter one.\nYou can use a default emoji like ⬛ for the background to type more letters.\nWith one custom emoji, you can use 4-5 letters; without any custom emojis, about 8 letters.\nYour message is currently {len(emojified_message)} characters, but the max allowed is 2000. Thank you!", ephemeral=True)
    else:
        await interaction.response.send_message(content=emojified_message, ephemeral=True)

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
    
    class ReportModal(discord.ui.Modal, title="Report Message"):
        reason = discord.ui.TextInput(
            label="Why are you reporting this message?",
            style=discord.TextStyle.paragraph,
            required=True,
            max_length=500,
            placeholder="Describe the issue for the mods"
        )

        def __init__(self):
            super().__init__()

        async def on_submit(self, modal_interaction: discord.Interaction):
            await modal_interaction.response.send_message(
                "Do you want to send this report anonymously?",
                ephemeral=True,
                view=AnonymousChoiceView(reason=self.reason.value)
            )

    class AnonymousChoiceView(discord.ui.View):
        def __init__(self, reason):
            super().__init__(timeout=60)
            self.reason = reason

        @discord.ui.select(
            placeholder="Send anonymously?",
            min_values=1,
            max_values=1,
            options=[
                discord.SelectOption(label="Yes", value="yes", description="Send this report anonymously"),
                discord.SelectOption(label="No", value="no", description="Include your username in the report")
            ]
        )
        async def select_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
            send_anon = select.values[0] == "yes"
            log_channel = interaction.guild.get_channel(ReportChannel)
            embed = discord.Embed(title='Reported Message')

            if message.content:
                embed.description = message.content
            embed.set_author(name=message.author.display_name, icon_url=message.author.display_avatar.url)
            embed.timestamp = message.created_at

            reporter_field = "Anonymous" if send_anon else interaction.user.mention
            embed.add_field(name="Reporter", value=reporter_field, inline=False)
            embed.add_field(name="Reason for report", value=self.reason, inline=False)

            url_view = discord.ui.View()
            url_view.add_item(discord.ui.Button(label='Go to Message', style=discord.ButtonStyle.url, url=message.jump_url))

            await log_channel.send(embed=embed, view=url_view)
            await interaction.response.edit_message(content="Report sent to moderators. Thank you!", view=None)

    await interaction.response.send_modal(ReportModal())

@commands.has_any_role(*ModRoles)
@bot.command(name='sync', help='Sync slash commands')
async def sync(ctx):
    guild = discord.Object(id=GUILD_ID)  # you can use a full discord.Guild as the method accepts a Snowflake
    # print(bot.tree.get_commands(type=discord.AppCommandType.message))
    # bot.tree.remove_command('Report to admins', type=discord.AppCommandType.message)
    # bot.tree.remove_command('Add to your second look list', type=discord.AppCommandType.message)
    bot.tree.clear_commands(type=discord.AppCommandType.message, guild=guild)
    # bot.tree.clear_commands(type=discord.AppCommandType.message, guild=None)
    # bot.tree.copy_global_to(guild=guild)
    # print(await bot.tree.fetch_commands(guild=guild))
    cmd = app_commands.Command(
        name="tool",
        description="Checks if a game has a guide, cam or works with UUU.",
        callback=toolAC,
    )
    cmd.type = 4
    cmd.handler = 2
    bot.tree.add_command(cmd)
    await bot.tree.sync(guild=guild)
    await bot.tree.sync()

@commands.has_any_role(*ModRoles)
@bot.command(name='syncbets', help='Sync betting slash commands')
async def syncbets(ctx):
    guild = discord.Object(id=GUILD_ID)
    bot.tree.clear_commands(type=discord.AppCommandType.message, guild=guild)
    await bot.tree.sync(guild=guild)
    await bot.tree.sync()
    await ctx.send("Betting slash commands synced!")

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

class birthDayModal(ui.Modal, title = "Enter your birthday"):
    birthDay = ui.TextInput(label = "Enter your birthday in this format MM/DD/YYYY", style = discord.TextStyle.short, placeholder = "MM/DD/YYYY", required = True, max_length = 10)
    currentName = ui.TextInput(label = "Enter your name", style = discord.TextStyle.short, required = True)
    template = ui.TextInput(label = "Template to use", style = discord.TextStyle.short, placeholder = "(alive for {XXXX} days)", required = False)

    async def on_submit(self, interaction: discord.Interaction):
        # this line should work, but doesn't, and that's the reason i now hate that f langage
        # date = datetime.datetime.strptime("%m/%d/%Y", self.birthDay.value)
        date = self.birthDay.value.split("/")
        date = datetime.datetime(int(date[2]), int(date[0]), int(date[1]), 12)
        aliveFor = datetime.datetime.now().timestamp() - date.timestamp()
        daysAlive = aliveFor / 60 / 60 / 24
        user = interaction.user
        defaultTemplate = "(alive for {XXXX} days)"
        template = self.template.value if self.template.value != "" else defaultTemplate
        aliveForText = template.replace("{XXXX}", str(round(daysAlive)))
        newName = f"{self.currentName} {aliveForText}"
        if (len(newName) > 32):
            return await interaction.response.send_message(content=f"The name cannot surpass 32 characters, please make the template shorter\nName: {self.currentName} = {len(self.currentName.value)} characters\nTemplate: {aliveForText} = {len(aliveForText)} characters\nTotal: {len(self.currentName.value) + len(aliveForText)} + 1 space", ephemeral=True)
        await user.edit(nick=newName) # needs "Manage nicknames" permission
        birthDays[user.id] = {
            "birthday": date,
            "template": template,
            "name": self.currentName.value
        }
        await saveBirthdays()
        print(f"Name: {self.currentName.value} = {len(self.currentName.value)} characters\nTemplate: {aliveForText} = {len(aliveForText)} characters\nTotal: {len(self.currentName.value) + len(aliveForText)} + 1 space")
        return await interaction.response.send_message(content="Name successfully modified", ephemeral=True)

@bot.tree.command(name="birthday_modal", description="Give the bot you birthday")
async def birthdayModal(interaction: discord.Interaction):
    await interaction.response.send_modal(birthDayModal())

@bot.tree.command(name="birthday_remove", description="Remove yourself from the birthday list")
async def birthdayModal(interaction: discord.Interaction):
    if interaction.user.id in birthDays:
        del birthDays[interaction.user.id]
        await saveBirthdays()
        return await interaction.response.send_message(content="Removed from the birthday list", ephemeral=True)
    await interaction.response.send_message(content="Not in the list", ephemeral=True)

# betting / prediction market commands start here

def _require_db():
    # commands can still work off activePredictions even if sqlite is down, just no persistence/scores
    return betting_db if betting_db.is_connected() else None


@app_commands.checks.has_role("Founders Edition")
@bot.tree.command(name="bet_create", description="[MOD] Create a new prediction market bet")
@app_commands.describe(
    question="The prediction question, e.g. 'Will Bloodborne PC be announced?'",
    description="Optional extra context or rules",
    option_a="Label for the YES/first option (default: YES)",
    option_b="Label for the NO/second option (default: NO)",
    duration="How long voting stays open, e.g. 30m, 2h, 2 hours, 1d, 2 days (default: 24h)",
)
async def bet_create(
    interaction: discord.Interaction,
    question: str,
    option_a: str = "YES",
    option_b: str = "NO",
    duration: str = "24h",
    description: str = "",
):
    await interaction.response.defer(ephemeral=False)

    try:
        duration_minutes = parse_duration(duration)
    except ValueError:
        await interaction.followup.send(
            f"Couldn't make sense of `{duration}` as a duration. Try something like `30m`, `2h`, `2 hours`, `1d` or `2 days`.",
            ephemeral=True,
        )
        return

    closes_at = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=duration_minutes)

    pred = Prediction(
        question=question,
        description=description,
        option_a=option_a,
        option_b=option_b,
        duration_minutes=duration_minutes,
        creator_id=interaction.user.id,
        creator_name=interaction.user.display_name,
        closes_at=closes_at,
        guild_id=interaction.guild_id,
        channel_id=interaction.channel_id,
    )

    embed = build_prediction_embed(pred)
    view = PredictionView(pred.prediction_id)
    view.vote_a.label = pred.option_a
    view.vote_b.label = pred.option_b
    msg = await interaction.followup.send(embed=embed, view=view)
    pred.message_id = msg.id

    activePredictions[pred.prediction_id] = pred

    db = _require_db()
    if db:
        await db.create_prediction(pred)
        await db.update_message_id(pred.prediction_id, msg.id)

    asyncio.create_task(auto_close_prediction(interaction.client, pred, db))

    print(f"[BETTING] Prediction {pred.prediction_id} created by {interaction.user}")


@app_commands.checks.has_role("Founders Edition")
@bot.tree.command(name="bet_close", description="[MOD] Resolve a prediction and award scores")
@app_commands.describe(
    bet_number="The bet number (shown as 'Bet #1', 'Bet #2', etc. in the embed footer)",
    winner="Which option won",
)
async def bet_close(
    interaction: discord.Interaction,
    bet_number: int,
    winner: str,
):
    await interaction.response.defer(ephemeral=True)

    pred = None
    for active_pred in activePredictions.values():
        if active_pred.display_id == bet_number:
            pred = active_pred
            break

    if pred is None:
        await interaction.followup.send(
            f"No active prediction with number `{bet_number}`. Use `/bet_list` to see active predictions.",
            ephemeral=True,
        )
        return

    # winner is the value "A" or "B" coming from autocomplete
    if winner not in ("A", "B"):
        await interaction.followup.send("Invalid option. Please select from the autocomplete suggestions.", ephemeral=True)
        return

    db = _require_db()
    summary = await close_prediction(interaction.client, pred, winner, db)

    try:
        channel = interaction.guild.get_channel(pred.channel_id)
        if channel:
            await channel.send(summary)
            await interaction.followup.send("Done!", ephemeral=True)
        else:
            await interaction.followup.send(summary, ephemeral=False)
    except Exception:
        await interaction.followup.send(summary, ephemeral=False)

    print(f"[BETTING] Bet #{pred.display_id} resolved by {interaction.user} — winner: {winner}")


@bet_close.autocomplete("winner")
async def bet_close_winner_autocomplete(
    interaction: discord.Interaction,
    current: str,
) -> list[app_commands.Choice[str]]:
    # bet_number is usually already typed by the time they get to this field
    bet_number = None
    try:
        raw = interaction.namespace.bet_number
        if raw is not None:
            bet_number = int(raw)
    except (TypeError, ValueError, AttributeError):
        pass

    if bet_number is not None:
        pred = next(
            (p for p in activePredictions.values() if p.display_id == bet_number),
            None,
        )
        if pred:
            return [
                app_commands.Choice(name=f"✅ {pred.option_a}", value="A"),
                app_commands.Choice(name=f"✅ {pred.option_b}", value="B"),
            ]

    # nothing typed yet (or it didn't parse) - just dump every open bet's options
    choices = []
    for pred in list(activePredictions.values()):
        if pred.status in ("open", "closed"):
            choices.append(app_commands.Choice(name=f"#{pred.display_id} → {pred.option_a}", value="A"))
            choices.append(app_commands.Choice(name=f"#{pred.display_id} → {pred.option_b}", value="B"))
    if choices:
        return choices[:25]

    return [
        app_commands.Choice(name="Option A", value="A"),
        app_commands.Choice(name="Option B", value="B"),
    ]


@bot.tree.command(name="bet_list", description="Show all currently open predictions")
async def bet_list(interaction: discord.Interaction):
    open_preds = [p for p in activePredictions.values() if p.status in ("open", "closed")]

    if not open_preds:
        await interaction.response.send_message("No active predictions right now.", ephemeral=True)
        return

    embed = discord.Embed(title="Active Predictions", color=0x5865F2)
    for pred in open_preds[:10]:  # max 10 in one embed
        embed.add_field(
            name=f"Bet #{pred.display_id} · {pred.question}",
            value=(
                f"{pred.option_a}: **{pred.percent_a()}%** ({pred.votes_a} votes)  "
                f"{pred.option_b}: **{pred.percent_b()}%** ({pred.votes_b} votes)\n"
                f"Closes: <t:{int(pred.closes_at.timestamp())}:R>"
            ),
            inline=False,
        )
    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name="leaderboard", description="Show the prediction market leaderboard")
@app_commands.describe(scope="Global all-time scores, or scores for a specific prediction ID")
async def leaderboard(interaction: discord.Interaction, scope: str = "global"):
    await interaction.response.defer(ephemeral=True)

    db = _require_db()
    if db is None:
        await interaction.followup.send("Database not connected.", ephemeral=True)
        return

    scope = scope.strip().lower()

    if scope == "global":
        rows = await db.get_global_leaderboard(10)
        if not rows:
            await interaction.followup.send("No scores recorded yet.", ephemeral=True)
            return

        embed = discord.Embed(title="🏆 Global Leaderboard", color=0xF1C40F)
        medals = ["🥇", "🥈", "🥉"]
        for i, row in enumerate(rows):
            medal = medals[i] if i < 3 else f"{i+1}."
            score = row["global_score"]
            accuracy = row["accuracy"]
            total = row["total_bets"]
            correct = row["correct_bets"]
            embed.add_field(
                name=f"{medal} {row['username']}",
                value=f"**{score:+.1f} pts** — {correct}/{total} correct ({accuracy}%)",
                inline=False,
            )
        await interaction.followup.send(embed=embed, ephemeral=True)

    else:
        # otherwise scope is a prediction id
        pred = activePredictions.get(scope)
        if pred is None:
            pred_data = await db.get_prediction(scope)
            if pred_data is None:
                await interaction.followup.send(
                    f"No prediction found with ID `{scope}`.", ephemeral=True
                )
                return
            question = pred_data["question"]
        else:
            question = pred.question

        rows = await db.get_event_leaderboard(scope, 10)
        if not rows:
            await interaction.followup.send("No scores for this prediction yet.", ephemeral=True)
            return

        embed = discord.Embed(
            title=f"🏆 Prediction Leaderboard",
            description=f"**{question}**",
            color=0xF1C40F,
        )
        medals = ["🥇", "🥈", "🥉"]
        for i, row in enumerate(rows):
            medal = medals[i] if i < 3 else f"{i+1}."
            correct_str = "Correct" if row["is_correct"] else "Wrong"
            embed.add_field(
                name=f"{medal} {row['username']}",
                value=f"**{row['score_awarded']:+.1f} pts** — {correct_str}",
                inline=False,
            )
        await interaction.followup.send(embed=embed, ephemeral=True)


@bot.tree.command(name="my_bets", description="See your prediction history and scores")
@app_commands.describe(member="Leave empty to check yourself, or mention another member")
async def my_bets(interaction: discord.Interaction, member: discord.Member = None):
    await interaction.response.defer(ephemeral=True)

    db = _require_db()
    if db is None:
        await interaction.followup.send("Database not connected.", ephemeral=True)
        return

    target = member or interaction.user
    stats = await db.get_user_stats(target.id)
    bets = await db.get_user_bets(target.id, 10)

    embed = discord.Embed(
        title=f"{target.display_name}'s Predictions",
        color=0x5865F2,
    )

    if stats:
        accuracy = stats["accuracy"]
        embed.add_field(
            name="Overall Stats",
            value=(
                f"Score: {stats['global_score']:+.1f} pts\n"
                f"Total bets: {stats['total_bets']}\n"
                f"Correct: {stats['correct_bets']} ({accuracy}%)"
            ),
            inline=False,
        )
    else:
        embed.add_field(name="Overall Stats", value="No resolved bets yet.", inline=False)

    if bets:
        history = ""
        for bet in bets[:8]:
            chosen = bet["option_a"] if bet["chosen_option"] == "A" else bet["option_b"]
            if bet["is_correct"] is None:
                result = "Pending"
            elif bet["is_correct"]:
                result = f"+{bet['score_awarded']:.1f}pts"
            else:
                result = f"{bet['score_awarded']:.1f}pts"
            history += f"• **{bet['question'][:45]}...**\n  → {chosen} — {result}\n"
        embed.add_field(name="Recent Bets", value=history, inline=False)
    else:
        embed.add_field(name="Recent Bets", value="No bets placed yet.", inline=False)

    await interaction.followup.send(embed=embed, ephemeral=True)


@app_commands.checks.has_role("Founders Edition")
@bot.tree.command(name="bet_export", description="[MOD] Download the betting database as a file")
async def bet_export(interaction: discord.Interaction):
    if interaction.channel_id != BetModChannel:
        await interaction.response.send_message(
            f"This command can only be used in <#{BetModChannel}>.", ephemeral=True
        )
        return
    if not os.path.isfile(DB_PATH):
        await interaction.response.send_message(f"No database file found at `{DB_PATH}`.", ephemeral=True)
        return
    size_kb = os.path.getsize(DB_PATH) // 1024
    await interaction.response.send_message(
        f"Here's the current betting database (`{size_kb} KB`):",
        file=discord.File(DB_PATH, filename="betting.db"),
        ephemeral=True,
    )


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

async def saveBirthdays():
    with open('birthDays.pkl', 'wb') as f:
        pickle.dump(birthDays, f)

if os.path.isfile('./birthDays.pkl'):
    with open('birthDays.pkl', 'rb') as f:
        try:
            birthDays = pickle.load(f)
        except EOFError:
            birthDays = {}
else:
    birthDays = {}
    with open('birthDays.pkl', 'wb'): pass