import discord
from discord.ext import commands

import asyncio
import random
import os

from dotenv import load_dotenv
from typing import Final, Optional

from datastore import Datastore

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

emojis : Final[dict] = {
    "coin" : "<a:goldcoin:1328517822497685535>",
    "wallet" : "<:wallet:1328163268522410095>",
    "bank" : "<:bank2:1328163595434987551>"
}

@client.event
async def on_ready():
    global datastore
    datastore = Datastore("savedata.json")

    await client.add_cog(Economy())
    await client.add_cog(Gambling())
    await client.add_cog(OwnerOnly())

## COMMANDS ##

class Economy(commands.Cog):
    @commands.command(
        help="Displays your or another user's wallet and bank balance."
    )
    async def bal(self, ctx, user : Optional[discord.Member] = None):
        """Checks the balance of a user

        Args:
            ctx (_type_): Context from Discord.Py
            user (Optional[discord.Member], optional): The user to check the balance of, optional to check your own if no user provided. Defaults to None.
        """

        user = user or ctx.author

        wallet : int = datastore.fetch(str(user.id), "coins_wallet") or 0
        bank : int = datastore.fetch(str(user.id), "coins_bank") or 0

        embed = discord.Embed(
            title = f"{user}'s Balance",
            description = f"{emojis["wallet"]} Wallet: {emojis["coin"]} **{wallet}**\n\n{emojis["bank"]} Bank: {emojis["coin"]} **{bank}**",
            colour=0xf5d400
        )

        await ctx.reply(embed=embed)

class Gambling(commands.Cog):
    @commands.command(
        help="Bet any amount on a dice roll, 1-6 odds, win 6x your bet."
    )
    async def dice(self, ctx, bet : int, guess : int):
        """Dice roll gamble that pays 6:1

        Args:
            ctx (_type_): Context from Discord.Py
            bet (int): The amount of coins to bet
            guess (int): The dice number to bet it on

        Raises:
            commands.CheckFailure: Error handling for not enough coins
        """
        
        wallet : int = datastore.fetch(str(ctx.author.id), "coins_wallet") or 0
        if wallet < bet:
            raise commands.CheckFailure

        roll : int = random.randint(1, 6)
        won : bool = roll == guess

        if won:
            datastore.change(str(ctx.author.id), "coins_wallet", bet * 6, "+")
        else:
            datastore.change(str(ctx.author.id), "coins_wallet", bet, "-")
        
        startEmbed = discord.Embed(
            title=f"{ctx.author}'s Dice roll",
            description=":game_die:ㅤ**Rolling...**ㅤ:game_die:",
            colour=0x00b0f4
        )
        endEmbed = discord.Embed(
            title=f"{ctx.author}'s Dice roll",
            description=f":game_die:ㅤ**{roll}**ㅤ:game_die:\n\n{'You win!' if won else 'You lose!'}",
            colour=0x38ff4f if won else 0xff3838
        )
        
        message = await ctx.reply(embed=startEmbed)

        await asyncio.sleep(3)

        await message.edit(embed=endEmbed)
    
    @commands.command(
        help="Bet any amount on multiple options with different payouts.",
        aliases=["rl"]
    )
    async def roulette(self, ctx, bet : int, option : str = commands.parameter(description=":\n\t\todds 1:2\n\t\tevens 1:2\n\t\tred 1:2\n\t\tblack 1:2")):
        """Classic roulette, bet coins on any normal roulette option

        Args:
            ctx (_type_): Context from Discord.Py
            bet (int): The amount of coins to bet
            option (_type_, optional): The option to bet on.

        Raises:
            commands.CheckFailure: _description_
        """

        if not option in ["odds", "evens", "red", "black"]:
            raise commands.BadArgument
        
        wallet : int = datastore.fetch(str(ctx.author.id), "coins_wallet") or 0
        if wallet < bet:
            raise commands.CheckFailure

        roll : int = random.randint(0, 36)
        
        payout : int = 0
        colorEmoji : str
        if (option == "evens" or option == "black") and roll % 2 == 0:
            payout = 2
            colorEmoji = "black_large_square"
        elif (option == "odds" or option == "red") and roll % 3 == 0:
            payout = 2
            colorEmoji = "red_square"
        if (roll == 0):
            payout = 0
            colorEmoji = "green_square"

        if payout > 0:
            datastore.change(str(ctx.author.id), "coins_wallet", bet * payout, "+")
        else:
            datastore.change(str(ctx.author.id), "coins_wallet", bet, "-")

        startEmbed = discord.Embed(
            title=f"{ctx.author}'s Roulette spin",
            description=":dart:ㅤ**Rolling...**ㅤ:dart:",
            colour=0x00b0f4
        )

        endEmbed = discord.Embed(
            title=f"{ctx.author}'s Roulette spin",
            description=f":{colorEmoji}:ㅤ**{roll}**ㅤ:{colorEmoji}:\n\n{'You win!' if payout > 0 else 'You lose!'}",
            colour=0x38ff4f if payout > 0 else 0xff3838
        )
        
        message = await ctx.reply(embed=startEmbed)

        await asyncio.sleep(3)

        await message.edit(embed=endEmbed)

@commands.is_owner()
class OwnerOnly(commands.Cog):
    @commands.command(
        help="Adds a coin amount to a user",
        hidden=True
    )
    async def add(self, ctx, user : Optional[discord.Member] = None, amount = 0):
        """Adds a coin amount to a given user or themself

        Args:
            ctx (_type_): Context from Discord.Py
            user (Optional[discord.Member], optional): The user to add coins to. Defaults to None.
            amount (int, optional): The amount of coins to add. Defaults to 0.
        """

        user = user or ctx.author

        datastore.change(str(user.id), "coins_wallet", amount, "+")

        await ctx.reply(f"Successfully addded {emojis["coin"]} **{amount}** to **{user}**'s wallet") 

## 

## ERRORS ##

@Gambling.dice.error
async def diceError(self, ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.reply("Incorrect usage, use $help for assistance.")
    elif isinstance(error, commands.CheckFailure):
        await ctx.reply("Your bet is bigger than your wallet balance!")
@Gambling.roulette.error
async def rouletteError(self, ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.reply("Incorrect usage, use $help for assistance. Using it on this specific command will give a list of avalible options.")
    elif isinstance(error, commands.CheckFailure):
        await ctx.reply("Your bet is bigger than your wallet balance!")
    elif isinstance(error, commands.BadArgument):
        await ctx.reply("No roulette valid option found.")

@OwnerOnly.add.error
async def addError(self, ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.reply("Incorrect usage, use $help for assistance.")
    elif isinstance(error, commands.CheckFailure):
        await ctx.reply("Lacking required permissions, only the owner can use this command.")

##

client.run(TOKEN)