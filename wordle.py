import random
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
                await interaction.response.edit_message(content="Choose a letter", view=Framedle()) #, ephemeral=True

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
        self.turn = 1
        self.rightGuesses = []
        for x in range(5):
            for y in range(5):
                self.add_item(FramedleButton(x, y, framedleButtons[y][x], self.board))

    def checkWord(self, givenWord):
        if givenWord == self.word.lower(): return True
        else: return False

    def hint(self, typedWord):
        hint = ""
        hint += ' '.join([emojiLetters[letters.find(typedLetter.lower())] for typedLetter in typedWord])
        for pos in range(len(typedWord), len(self.word)):
            hint += " " + emojiLetters[letters.find(self.word[pos])] if self.word[pos] in self.rightGuesses else " 🔳"
        return hint

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
        view.typedWord += self.label
        view.lettersPos.append([self.x, self.y])
        if len(view.typedWord) < view.wordLength:
            await interaction.response.edit_message(content=f"{view.wordHistory}\n{view.hint(view.typedWord)}" if view.turn == 1 else f"{view.wordHistory}{view.hint(view.typedWord)}")
            return

        hasWon = view.checkWord(view.typedWord.lower())
        view.wordHistory += "> " + view.typedWord + "\n"
        for child in view.children:
            if child.label.lower() in view.word:
                posTyped = view.typedWord.lower().find(child.label.lower())
                posWord = view.word.lower().find(child.label.lower())
                if posTyped > -1 and posTyped == posWord:
                    child.style = discord.ButtonStyle.success
                    view.rightGuesses.append(view.word[posWord])
                elif posTyped > -1 and posTyped != posWord:
                    if child.style != discord.ButtonStyle.success:
                        child.style = discord.ButtonStyle.red
        view.typedWord = ""
        view.turn += 1
        hasLost = True if view.turn > 6 else False
        if hasWon or hasLost:
            for child in view.children:
                child.disabled = True
            view.wordHistory = f"Bravo! The word was `{view.word}`" if hasWon else f"Sorry but you have lost, the word was `{view.word}`"
        await interaction.response.edit_message(content=view.wordHistory + view.hint(''), view=view)
        # lineEntered = checkWord()
        # self.style = discord.ButtonStyle.success
        # self.disabled = True

        # winner = view.checkWinner()
        # if winner is not None:
        #     bot.dispatch("bingo_winner", view.user, view.channel)

def getTodayWord():
    return random.choice(framedleWords)