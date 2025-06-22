import discord
from discord.ext import commands

import os

from dotenv import load_dotenv
from typing import Final

from datastore import Datastore

from cogs.economy import Economy
from cogs.gambling import Gambling
from cogs.admin import Admin

load_dotenv()

TOKEN : Final = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True

client = commands.Bot(
    command_prefix = "$",
    intents = intents,
    help_command = commands.DefaultHelpCommand(
        no_category = "Default"
    )
)

@client.event
async def on_ready():
    datastore = Datastore("savedata.json")

    emojis : Final[dict] = {
        "coin" : "<a:goldcoin:1328517822497685535>",
        "wallet" : "<:wallet:1328163268522410095>",
        "bank" : "<:bank2:1328163595434987551>",
        "wheel" : "<a:roulettewheel:1386230490872152136>",
        "card_back" : "<:card_back:1386468981002735656>"
    }

    await client.add_cog(Economy(datastore, emojis))
    await client.add_cog(Gambling(datastore, emojis))
    await client.add_cog(Admin(datastore, emojis))

@client.event
async def on_command_error(ctx, error):
    await ctx.reply(error)

client.run(TOKEN)