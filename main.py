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
    command_prefix="$",
    intents=intents,
    help_command=commands.DefaultHelpCommand(
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
    }

    await client.add_cog(Economy(datastore, emojis))
    await client.add_cog(Gambling(datastore, emojis))
    await client.add_cog(Admin(datastore, emojis))

@Gambling.dice.error
async def diceError(self, ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.reply("Incorrect usage, use $help for assistance.")
    elif isinstance(error, commands.CheckFailure):
        await ctx.reply("Your bet is bigger than your wallet balance!")
    elif isinstance(error, commands.BadArgument):
        await ctx.reply("The dice number must be between 1 and 6, use $help for assistance.")
@Gambling.roulette.error
async def rouletteError(self, ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.reply("Incorrect usage, use $help for assistance. Using it on this specific command will give a list of avalible options.")
    elif isinstance(error, commands.CheckFailure):
        await ctx.reply("Your bet is bigger than your wallet balance!")
    elif isinstance(error, commands.BadArgument):
        await ctx.reply("No roulette valid option found.")

@Economy.withdraw.error
async def rouletteError(self, ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.reply("Your requested withdraw amount is greater than your bank balance!")
    elif isinstance(error, commands.BadArgument):
        await ctx.reply("The withdraw amount must be greater than 0, use $help for assistance.")
@Economy.deposit.error
async def rouletteError(self, ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.reply("Your requested deposit amount is greater than your wallet balance!")
    elif isinstance(error, commands.BadArgument):
        await ctx.reply("The deposit amount must be greater than 0, use $help for assistance.")
@Economy.daily.error
async def rouletteError(self, ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.reply("You've already claimed your bonus in the last 12 hours!")

@Admin.add.error
async def addError(self, ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.reply("Incorrect usage, use $help for assistance.")
    elif isinstance(error, commands.CheckFailure):
        await ctx.reply("Lacking required permissions to use this command.")

client.run(TOKEN)