import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from typing import Final, Optional
from datastore import Datastore
import asyncio
import random

load_dotenv()

TOKEN : Final = os.getenv("TOKEN") #Bot token from env file

intents = discord.Intents.default() #My intentions
intents.message_content = True

client = commands.Bot(command_prefix="$", intents=intents) #Setting up the bot/client

emojis : Final[dict] = { #Easy way to get the custom emojies so I dont have to write them out every time, might move to json ltr
    "coin" : "<a:goldcoin:1328517822497685535>",
    "wallet" : "<:wallet:1328163268522410095>",
    "bank" : "<:bank2:1328163595434987551>"
}

@client.event
async def on_ready(): #Initalizing the "database" when the bot/client is ready
    global datastore
    datastore = Datastore("savedata.json")

## CHECKS ##
# REMEMBER: DO CHECKS

## COMMANDS ##

@client.command(
    help="Displays your or another user's wallet and bank balance."
)
async def bal(ctx, user : Optional[discord.Member] = None):
    user = user or ctx.author

    wallet : int = datastore.fetch(str(user.id), "coins_wallet") or 0 # Fetching the values from the "database"
    bank : int = datastore.fetch(str(user.id), "coins_bank") or 0

    embed = discord.Embed( # Making embeds is so simple its great
        title = f"{user}'s Balance",
        description = f"{emojis["wallet"]} Wallet: {emojis["coin"]} **{wallet}**\n\n{emojis["bank"]} Bank: {emojis["coin"]} **{bank}**",
        colour=0xf5d400
    )

    await ctx.reply(embed=embed)

@client.command(
    help="Admin only - adds a coin amount to a user"
)
async def add(ctx, user : Optional[discord.Member] = None, amount = 0):
    user = user or ctx.author

    if any(role.permissions.administrator for role in ctx.author.roles): #Checks roles for admin permission
        await ctx.reply(f"Lacking required permissions, operation failed") #Fail response
        return

    datastore.change(str(user.id), "coins_wallet", amount, "+") # Adds amount to user's wallet balance

    await ctx.reply(f"Successfully addded {emojis["coin"]} **{amount}** to **{user}**'s wallet") #Sucess response

@client.command(
    help="Bet any amount on a dice number, if it rolls on that number, you win 6x your bet."
)
async def dice(ctx, bet : int, guess : int):
    wallet : int = datastore.fetch(str(ctx.author.id), "coins_wallet") or 0 #Getting and checking the users wallet balance
    if wallet < bet:
        raise commands.CheckFailure

    roll : int = random.randint(1, 6) # Psuedorandom :(
    won : bool = roll == guess

    if won:
        datastore.change(str(ctx.author.id), "coins_wallet", bet * 6, "+") #Win condition check and reward payout
    else:
        datastore.change(str(ctx.author.id), "coins_wallet", bet, "-")
    
    startEmbed = discord.Embed( #Wait embed
        title=f"{ctx.author}'s Dice roll",
        description=":game_die:ㅤ**Rolling...**ㅤ:game_die:",
        colour=0x00b0f4
    )
    endEmbed = discord.Embed( #Win/lose embed  
        title=f"{ctx.author}'s Dice roll",
        description=f":game_die:ㅤ**{roll}**ㅤ:game_die:\n\n{'You win!' if won else 'You lose!'}",
        colour=0x38ff4f if won else 0xff3838
    )
    
    message = await ctx.reply(embed=startEmbed)

    await asyncio.sleep(3) #Wait for dramatic effect

    await message.edit(embed=endEmbed)

## ERRORS ## REMEBER: https://discordpy.readthedocs.io/en/stable/ext/commands/commands.html#error-handling

@dice.error
async def diceError(ctx, error): # Error handling for dice command
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.reply("Incorrect usage, use $help for assistance.")
    elif isinstance(error, commands.CheckFailure):
        await ctx.reply("Your bet is bigger than your wallet balance!")

client.run(TOKEN) #Finally, running the bot/client