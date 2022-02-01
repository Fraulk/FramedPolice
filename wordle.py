import discord
from discord.ui import button, View, Button, view
from discord.interactions import Interaction

from vars import *

class PlayFramedle(View):

    def __init__(self, timeout = None):
        super().__init__(timeout=timeout)
        # self.chanId = ctx.channel.id
        
    @discord.ui.button(label='Play', style=discord.ButtonStyle.blurple)
    async def playBtn(self, button: discord.ui.Button, interaction: discord.Interaction):
        # try:
        #     padawan = interaction.user.guild.get_role(PadawanRole)
        # except AttributeError:
        #     await interaction.response.send_message("Sorry but you can only play framedle in the Framed server", ephemeral=True)
        #     return
        # if padawan is None:
        #     await interaction.response.send_message("Sorry but you can only play framedle in the Framed server", ephemeral=True)
        # else:
        #     if padawan in interaction.user.roles:
        #         await interaction.response.send_message("Sorry! Members with padawan role aren't currently eligible to play framedle right now.", ephemeral=True)
        #     else:
                await interaction.response.send_message("Choose a box", view=Framedle(), ephemeral=True)

class Framedle(View):

    def __init__(self, timeout = None):
        super().__init__(timeout=timeout)
        self.board = [
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
        ]
        self.word = getTodayWord()
        self.wordLength = len(self.word)
        self.typedWord = ""
        self.lettersPos = []
        self.wordHistory = ""
        for x in range(5):
            for y in range(5):
                self.add_item(FramedleButton(x, y, framedleButtons[y][x], self.board))

    def setScore(self, x, y):
        print(f"{self.user.name} checked the {x+1}-{y+1} case")
        emptyBingo[x][y] = 1
        for bp in bingoPoints:
            if bp.id == self.user.id:
                # bp.pointMap[x][y] = 1
                return True
        # bingoPoints.append(BingoPoints(self.user.id, self.user.name))

    def checkWord(self, givenWord):
        for letter in givenWord:
            if letter.lower() in self.word:
                print("letter in word")
            else: 
                print("letter not in word")
                print(letter)

    def checkWinner(self):
        return None
    # https://github.com/Rapptz/discord.py/blob/45d498c1b76deaf3b394d17ccf56112fa691d160/examples/views/tic_tac_toe.py

class FramedleButton(Button):
    def __init__(self, x, y, label, board):
        if board[x][y] == 0:
            super().__init__(label=label, style=discord.ButtonStyle.secondary, row=y)
        if board[x][y] == 1:
            super().__init__(label=label, style=discord.ButtonStyle.grey, disabled=True, row=y)
        if board[x][y] == 2:
            super().__init__(label=label, style=discord.ButtonStyle.red, disabled=True, row=y)
        if board[x][y] == 3:
            super().__init__(label=label, style=discord.ButtonStyle.success, disabled=True, row=y)
        self.x = x
        self.y = y
        self.label = label
    
    async def callback(self, interaction: discord.Interaction):
        assert self.view is not None
        view = self.view
        # view.setScore(self.x, self.y)

        if len(view.typedWord) < view.wordLength:
            view.typedWord += self.label
            view.lettersPos.append([self.x, self.y])
            await interaction.response.edit_message(content=view.typedWord, view=view)
        else:
            # hasWin = view.checkWord(view.typedWord)
            view.wordHistory += view.typedWord
            for child in view.children:
                if child.label.lower() in view.word:
                    posTyped = view.typedWord.find(child.label.lower())
                    posWord = view.word.find(child.label.lower())
                    print((posTyped > -1 or posWord > -1) and posTyped == posWord)
                    if (posTyped > -1 or posWord > -1) and posTyped == posWord:
                        child.style = discord.ButtonStyle.success
                    elif (posTyped > -1 or posWord > -1): child.style = discord.ButtonStyle.red
            view.typedWord = ""
            await interaction.response.edit_message(content=view.wordHistory, view=view)
        # lineEntered = checkWord()
        # self.style = discord.ButtonStyle.success
        # self.disabled = True

        # winner = view.checkWinner()
        # if winner is not None:
        #     bot.dispatch("bingo_winner", view.user, view.channel)

def getTodayWord():
    return "photo"