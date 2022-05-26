import os
import discord
import firebase_admin
from firebase_admin import db
from dotenv import load_dotenv
from discord.ext import commands
from firebase_admin import credentials

PROD = True
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
    'framedle': {
        'name': '!framedle',
        'description': 'Play the framed wordle! The rules differ a little bit from the wordle'
    },
    'gvp': {
        'name': '!gvp',
        'description': 'Guess the VP! Answer in created threads'
    },
    'resetGVP': {
        'name': '!resetGVP',
        'description': 'Reset the Guess the VP game, when the command doesn\'t work or nobody finds the vp'
    },
    'special': {
        'name': 'Special reaction',
        'description': 'The bot has special reaction for some query : "good|bad|horny bot"'
    },
    'getScore': {
        'name': '!getScore [ids]',
        'description': 'Get the count of reaction from unique users of a shot'
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

framedleButtons = [
    ["A", "B", "C", "D", "E"],
    ["F", "G", "H", "I", "J"],
    ["K", "L", "M", "N", "O"],
    ["P", "Q", "R", "S", "T"],
    ["U", "V", "W", "X", "Y"],
]

golfFrames = [
    """
<:air:927935249982300251>
<:air:927935249982300251><:air:927935249982300251>🧑‍🦽🧍
    """,
    """
🤸
<:air:927935249982300251><:air:927935249982300251>🦽🏌️
    """,
    """
<:air:927935249982300251>
⛳<:air:927935249982300251>🦽🕺
    """,
]

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

framedleWords = [
    "photo", "skall", "berdu", "cheat", "putsos", "framed", "bot", "bingo", "bokeh", "ratio", "late",
    "reshade", "mods", "shot", "divorce", "crash", "retire", "late", "ratio", "drunk", "rick", "wordle",
    "ign", "uuu", "lore", "moykeh"
]

emojiLetters = "🇦🇧🇨🇩🇪🇫🇬🇭🇮🇯🇰🇱🇲🇳🇴🇵🇶🇷🇸🇹🇺🇻🇼🇽🇾🇿"
letters = "abcdefghijklmnopqrstuvwxyz"

colorNames = {
    "aliceblue": 0xf0f8ff,
	"antiquewhite": 0xfaebd7,
	"aqua": 0x00ffff,
	"aquamarine": 0x7fffd4,
	"azure": 0xf0ffff,
	"beige": 0xf5f5dc,
	"bisque": 0xffe4c4,
	"black": 0x000000,
	"blanchedalmond": 0xffebcd,
	"blue": 0x0000ff,
	"blueviolet": 0x8a2be2,
	"brown": 0xa52a2a,
	"burlywood": 0xdeb887,
	"cadetblue": 0x5f9ea0,
	"chartreuse": 0x7fff00,
	"chocolate": 0xd2691e,
	"coral": 0xff7f50,
	"cornflowerblue": 0x6495ed,
	"cornsilk": 0xfff8dc,
	"crimson": 0xdc143c,
	"cyan": 0x00ffff,
	"darkblue": 0x00008b,
	"darkcyan": 0x008b8b,
	"darkgoldenrod": 0xb8860b,
	"darkgray": 0xa9a9a9,
	"darkgreen": 0x006400,
	"darkgrey": 0xa9a9a9,
	"darkkhaki": 0xbdb76b,
	"darkmagenta": 0x8b008b,
	"darkolivegreen": 0x556b2f,
	"darkorange": 0xff8c00,
	"darkorchid": 0x9932cc,
	"darkred": 0x8b0000,
	"darksalmon": 0xe9967a,
	"darkseagreen": 0x8fbc8f,
	"darkslateblue": 0x483d8b,
	"darkslategray": 0x2f4f4f,
	"darkslategrey": 0x2f4f4f,
	"darkturquoise": 0x00ced1,
	"darkviolet": 0x9400d3,
	"deeppink": 0xff1493,
	"deepskyblue": 0x00bfff,
	"dimgray": 0x696969,
	"dimgrey": 0x696969,
	"dodgerblue": 0x1e90ff,
	"firebrick": 0xb22222,
	"floralwhite": 0xfffaf0,
	"forestgreen": 0x228b22,
	"fuchsia": 0xff00ff,
	"gainsboro": 0xdcdcdc,
	"ghostwhite": 0xf8f8ff,
	"gold": 0xffd700,
	"goldenrod": 0xdaa520,
	"gray": 0x808080,
	"green": 0x008000,
	"greenyellow": 0xadff2f,
	"grey": 0x808080,
	"honeydew": 0xf0fff0,
	"hotpink": 0xff69b4,
	"indianred": 0xcd5c5c,
	"indigo": 0x4b0082,
	"ivory": 0xfffff0,
	"khaki": 0xf0e68c,
	"lavender": 0xe6e6fa,
	"lavenderblush": 0xfff0f5,
	"lawngreen": 0x7cfc00,
	"lemonchiffon": 0xfffacd,
	"lightblue": 0xadd8e6,
	"lightcoral": 0xf08080,
	"lightcyan": 0xe0ffff,
	"lightgoldenrodyellow": 0xfafad2,
	"lightgray": 0xd3d3d3,
	"lightgreen": 0x90ee90,
	"lightgrey": 0xd3d3d3,
	"lightpink": 0xffb6c1,
	"lightsalmon": 0xffa07a,
	"lightseagreen": 0x20b2aa,
	"lightskyblue": 0x87cefa,
	"lightslategray": 0x778899,
	"lightslategrey": 0x778899,
	"lightsteelblue": 0xb0c4de,
	"lightyellow": 0xffffe0,
	"lime": 0x00ff00,
	"limegreen": 0x32cd32,
	"linen": 0xfaf0e6,
	"magenta": 0xff00ff,
	"maroon": 0x800000,
	"mediumaquamarine": 0x66cdaa,
	"mediumblue": 0x0000cd,
	"mediumorchid": 0xba55d3,
	"mediumpurple": 0x9370db,
	"mediumseagreen": 0x3cb371,
	"mediumslateblue": 0x7b68ee,
	"mediumspringgreen": 0x00fa9a,
	"mediumturquoise": 0x48d1cc,
	"mediumvioletred": 0xc71585,
	"midnightblue": 0x191970,
	"mintcream": 0xf5fffa,
	"mistyrose": 0xffe4e1,
	"moccasin": 0xffe4b5,
	"navajowhite": 0xffdead,
	"navy": 0x000080,
	"oldlace": 0xfdf5e6,
	"olive": 0x808000,
	"olivedrab": 0x6b8e23,
	"orange": 0xffa500,
	"orangered": 0xff4500,
	"orchid": 0xda70d6,
	"palegoldenrod": 0xeee8aa,
	"palegreen": 0x98fb98,
	"paleturquoise": 0xafeeee,
	"palevioletred": 0xdb7093,
	"papayawhip": 0xffefd5,
	"peachpuff": 0xffdab9,
	"peru": 0xcd853f,
	"pink": 0xffc0cb,
	"plum": 0xdda0dd,
	"powderblue": 0xb0e0e6,
	"purple": 0x800080,
	"rebeccapurple": 0x663399,
	"red": 0xff0000,
	"rosybrown": 0xbc8f8f,
	"royalblue": 0x4169e1,
	"saddlebrown": 0x8b4513,
	"salmon": 0xfa8072,
	"sandybrown": 0xf4a460,
	"seagreen": 0x2e8b57,
	"seashell": 0xfff5ee,
	"sienna": 0xa0522d,
	"silver": 0xc0c0c0,
	"skyblue": 0x87ceeb,
	"slateblue": 0x6a5acd,
	"slategray": 0x708090,
	"slategrey": 0x708090,
	"snow": 0xfffafa,
	"springgreen": 0x00ff7f,
	"steelblue": 0x4682b4,
	"tan": 0xd2b48c,
	"teal": 0x008080,
	"thistle": 0xd8bfd8,
	"tomato": 0xff6347,
	"turquoise": 0x40e0d0,
	"violet": 0xee82ee,
	"wheat": 0xf5deb3,
	"white": 0xffffff,
	"whitesmoke": 0xf5f5f5,
	"yellow": 0xffff00,
	"yellowgreen": 0x9acd32
}