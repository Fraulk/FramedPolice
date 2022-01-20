import os
import discord
import firebase_admin
from firebase_admin import db
from dotenv import load_dotenv
from discord.ext import commands
from firebase_admin import credentials

PROD = True
# 86400 : 24h
# 43200 : 12h
# Test channel : 873627093840314401
# Framed channel : 549986930071175169
DELAY = 43200
LIMIT = 5
WelcomeRole = 873297069715099721 if PROD else 898969812254990367
PadawanRole = 872825204869582869 if PROD else 899266723906220042
JoinedChannel = 873242046675169310 if PROD else 874368324023255131
LeftChannel = 873242046675169310 if PROD else 874368324023255131
SYSChannel = 549986930071175169 if PROD else 873627093840314401
SLChannel = 859492383845646346 if PROD else 889793521106714634
IntroChannel = 872825951011082291 if PROD else 898977778039390268

load_dotenv()
API_KEY = os.getenv("API_KEY")
DB_URL = os.getenv("DB_URL")
cred = credentials.Certificate("./secret.json")
SLapp = firebase_admin.initialize_app(cred, {'databaseURL': DB_URL})
ref = db.reference("/")
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

badBot = {
    'batmanSlap': {
        'size': (75, 75),
        'botPosition': (265, 30),
        'badPosition': (132, 100)
    },
    'pepeSlap': {
        'size': (100, 100),
        'botPosition': (80, 290),
        'badPosition': (-100, -100)
    },
    'kermitSlap': {
        'size': (128, 128),
        'botPosition': (690, 320),
        'badPosition': (-200, -200)
    },
    'humanSlap': {
        'size': (128, 128),
        'botPosition': (690, 90),
        'badPosition': (160, 90)
    },
    'drawSlap': {
        'size': (128, 128),
        'botPosition': (250, 30),
        'badPosition': (50, 240)
    },
    'terminatorSlap': {
        'size': (35, 35),
        'botPosition': (175, 20),
        'badPosition': (20, 90)
    },
    'seifieldSlap': {
        'size': (100, 100),
        'botPosition': (220, 70),
        'badPosition': (-100, -100)
    },
    'catSlap': {
        'size': (60, 60),
        'botPosition': (245, 70),
        'badPosition': (115, 150)
    },
    'woomanSlap': {
        'size': (100, 100),
        'botPosition': (450, 430),
        'badPosition': (370, 90)
    },
    'pepeSad': {
        'size': (128, 128),
        'botPosition': (-128, -128),
        'badPosition': (-128, -128)
    },
}

badGifs = [
    "https://discord.com/channels/549986543650078722/549986543650078725/893340504719249429",
    "https://tenor.com/view/the-rock-dwayne-johnson-dwayne-the-rock-tea-joe-moment-gif-22606108",
    "https://tenor.com/view/rock-one-eyebrow-raised-rock-staring-the-rock-gif-22113367",
    "https://tenor.com/view/i-was-acting-gif-23414661",
    "https://tenor.com/view/bonk-gif-19410756",
]

badReaction = [
    "<:angery:774364490057515058>",
    "<:FrogMan:550964011081007104>",
    "<:shrek:907243907513991188>",
    "<a:angrysmash:731197915581776156>",
    "<:catwtf:882606420686684161>",
    "<a:blink:750012630030221332>",
    "<:blobNO:613463993058852865>",
    "<a:blobangryAnim:551112353236779029>",
    "<:wellwellwell:908910894761771048>",
]

hornyBot = {
    'bonk': {
            'size': (128, 128),
            'botPosition': (400, 100),
            'badPosition': (1050, 500)
        },
}

hornyGifs = [
    "https://tenor.com/view/horny-jail-bonk-dog-hit-head-stop-being-horny-gif-17298755",
    "https://tenor.com/view/bonk-gif-19410756",
    "https://tenor.com/view/zhongli-genshin-impact-bonk-horny-jail-meteor-gif-20675806",
    "https://imgur.com/2QyYLP7",
    "https://tenor.com/view/listen-here-you-little-shit-bird-meme-bird-listen-here-you-little-shit-gif-19221308",
    "https://tenor.com/view/yes-yes-yes-gif-22948122",
    "https://tenor.com/view/nani-hmm-intensifies-jojos-bizarre-encyclopedia-triggered-anime-gif-9845045"
]

hornyReaction = [
    "<:judyTease:799286516965703700>",
    "<a:angrysmash:731197915581776156>",
    "<a:bonk:898191413622210581>",
    "<:catwtf:882606420686684161>",
    "<:nou:869265435676254228>",
    "<a:teasing:852712400914612264>",
]

goodBot = {
    'duck_puppy': {
            'size': (50, 50),
            'botPosition': (80, 120),
            'badPosition': (180, 110)
        },
    'goose_retriever': {
            'size': (100, 100),
            'botPosition': (420, 210),
            'badPosition': (500, 30)
        },
    'old_lady': {
            'size': (80, 80),
            'botPosition': (290, 180),
            'badPosition': (10, 0)
        },
    'retriever': {
            'size': (80, 80),
            'botPosition': (280, 180),
            'badPosition': (80, 210)
        },
}

goodGifs = [
    "https://tenor.com/view/kya_cute_k_timi-cutie-kando_kha_muji-khatey-muji-gif-21747239",
    "https://tenor.com/view/kith-cat-wholesome-chungus-valorant-gif-20521962",
    "https://tenor.com/view/kitten-love-luv-u-please-notice-me-gif-11462572",
]

goodReaction = [
    "<:catblobheart:822464758530965546>",
    "<a:gandalf:551112351986876447>",
    "<:PraiseTheSun:553217550813757451>",
    "<a:faceheart:852713931327275028>",
    "<a:HyperPartyBlobAnim:555409742579630090>", 
    "<a:catcoffee:862103121572003841>", 
    "<:heartinf:885091024232407071>",
    "<a:trulyamazingAnim:602947248048832565>",
]

notFound = [
    "I couldn't find anything for `{}`.",
    "There doesn't seem to be anything for `{}`.",
    "It looks like there's nothing for `{}`."
]

tooVague = [
    "I found too many results for `{}` ! Did you mean : ",
    "`{}` is too vague, were you looking for : "
]

found = [
    "Found these for ya!",
    "Were you looking for these?",
    "Hope these help!",
    "I managed to get these for you!"
]

helpMsg = {
    'check': {
        'name': '!check',
        'description': 'Shows data about you'
    },
    'cam': {
        'name': '!cam [name]',
        'description': 'Search for a freecams or a tool by string. ex: !cam cyberpunk 2077'
    },
    'guide': {
        'name': '!guide [name]',
        'description': 'Checks if a game have a guide on the site. ex: !guide cyberpunk'
    },
    'uuu': {
        'name': '!uuu [name]',
        'description': 'Checks if a game is compatible with UUU. ex: !uuu the ascent'
    },
    'cheat': {
        'name': '!cheat [name]',
        'description': 'Checks if a game have cheat tables on the site. ex: !cheat alien'
    },
    'tool': {
        'name': '!tool(s) [name]',
        'description': 'Checks if a game have a guide, cam or works with UUU. ex: !tool cyberpunk'
    },
    'changeDelay': {
        'name': '!changeDelay [seconds]',
        'description': 'Change the delay after reaching the limit for posting shots, with number of seconds'
    },
    'changeLimit': {
        'name': '!changeLimit [number]',
        'description': 'Change the limit for posting shots'
    },
    'currentValue': {
        'name': '!currentValue',
        'description': 'Shows the current values for DELAY and LIMIT'
    },
    'dump': {
        'name': '!dump',
        'description': 'Shows data about everybody'
    },
    'dumpR': {
        'name': '!dumpR',
        'description': 'Shows data about those who reached the limit and have been dm\'d by the bot'
    },
    'reset': {
        'name': '!reset [userID]',
        'description': 'Resets the count for a person, with his ID as parameter'
    },
    'resetAll': {
        'name': '!resetAll',
        'description': 'Resets the count for everyone'
    },
    'bingo': {
        'name': '!bingo',
        'description': 'Play to the framed bingo !'
    },
    'resetBingo': {
        'name': '!resetBingo',
        'description': 'Manually reset the bingo. (doesn\'t return any message)'
    },
    'changeBingo': {
        'name': '!changeBingo',
        'description': 'Change the bingo image with the attached png file in your command\n(change takes effect at the next round)'
    },
    'connect': {
        'name': '!connect @someone :emoji:',
        'description': 'Starts a connect4 game against @someone, with an optionnal emoji replacing your token'
    },
    'special': {
        'name': 'Special reaction',
        'description': 'The bot has special reaction for some query : "good|bad|horny bot"'
    },
}

bingoText = [
    ["tweets gets people mad", "syphon lore fail", "game crashes", "V💜S", "HighQualityMeme™"],
    ["skall starts smthng", "someone's drunk", "play w/ the bot", "nuvo disagrees", "sono interrupts convo"],
    ["should play tgthr", "social media sucks", "FREE SPOT", "BBPC/Elden Ring", "Smithy has a bad opinion"],
    ["someone brings up nft", "someone didn't readme", "ghost says hi", "from scrap to hof", "cat gif"],
    ["moy nerds out", "suspiria talks abt old days", "hof anxiety", "mentions retiring", "awake at 6am"]
]

bingoPoints = []

emptyBingo = [
    [0, 0, 0, 0, 0], 
    [0, 0, 0, 0, 0], 
    [0, 0, 0, 0, 0], 
    [0, 0, 0, 0, 0], 
    [0, 0, 0, 0, 0]
]

titleAlts = []

golfEmoji = """
        🤸 
        <:air:927935249982300251> 🦽 🏌️
    """

marioEmoji = """
<:air:927935249982300251><:air:927935249982300251><:air:927935249982300251>🟥🟥🟥🟥🟥<:air:927935249982300251><:air:927935249982300251><:air:927935249982300251><:air:927935249982300251>
<:air:927935249982300251><:air:927935249982300251>🟥🟥🟥🟥🟥🟥🟥🟥🟥<:air:927935249982300251>
<:air:927935249982300251><:air:927935249982300251>🟫🟫🟫🟨🟨⬛🟨<:air:927935249982300251><:air:927935249982300251><:air:927935249982300251>
<:air:927935249982300251>🟫🟨🟫🟨🟨🟨⬛🟨🟨🟨<:air:927935249982300251>
<:air:927935249982300251>🟫🟨🟫🟫🟨🟨🟨🟫🟨🟨🟨
<:air:927935249982300251>🟫🟫🟨🟨🟨🟨🟫🟫🟫🟫<:air:927935249982300251>
<:air:927935249982300251><:air:927935249982300251><:air:927935249982300251>🟨🟨🟨🟨🟨🟨<:air:927935249982300251><:air:927935249982300251><:air:927935249982300251>
<:air:927935249982300251><:air:927935249982300251>🟥🟥🟦🟥🟥🟦🟥🟥<:air:927935249982300251><:air:927935249982300251>
<:air:927935249982300251>🟥🟥🟥🟦🟥🟥🟦🟥🟥🟥<:air:927935249982300251>
🟥🟥🟥🟥🟦🟦🟦🟦🟥🟥🟥🟥
🟨🟨🟥🟦🟧🟦🟦🟧🟦🟥🟨🟨
🟨🟨🟨🟦🟦🟦🟦🟦🟦🟨🟨🟨
🟨🟨🟦🟦🟦🟦🟦🟦🟦🟦🟨🟨
<:air:927935249982300251><:air:927935249982300251>🟦🟦🟦<:air:927935249982300251><:air:927935249982300251>🟦🟦🟦<:air:927935249982300251><:air:927935249982300251>
<:air:927935249982300251><:air:927935249982300251>🟫🟫<:air:927935249982300251><:air:927935249982300251><:air:927935249982300251><:air:927935249982300251>🟫🟫<:air:927935249982300251><:air:927935249982300251>
<:air:927935249982300251>🟫🟫🟫<:air:927935249982300251><:air:927935249982300251><:air:927935249982300251><:air:927935249982300251>🟫🟫🟫<:air:927935249982300251>
    """


shockedFrames = {
    'shocked0' : "<:air:927935249982300251>🤏😎",
    'shocked1' : "🤏🕶️😳",
}