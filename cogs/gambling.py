import discord
from discord.ext import commands

import asyncio
import random

class Gambling(commands.Cog):
    def __init__(self, datastore, emojis : dict[str]):
        self.datastore = datastore
        self.emojis = emojis

    @commands.command(
        help="Bet any amount on a dice roll, 1-6 odds, win 6x your bet."
    )
    async def dice(self, ctx, bet : int = commands.parameter(description="The amount to bet."), guess : int = commands.parameter(description="The number to bet on.")):
        """Dice roll gamble that pays 6:1

        Args:
            ctx (_type_): Context from Discord.Py
            bet (int): The amount of coins to bet
            guess (int): The dice number to bet it on

        Raises:
            commands.CheckFailure: Error handling for not enough coins
        """

        if guess < 1 or guess > 6:
            raise commands.BadArgument
        
        wallet : int = self.datastore.fetch(str(ctx.author.id), "coins_wallet") or 0
        if wallet < bet:
            raise commands.CheckFailure

        roll : int = random.randint(1, 6)
        won : bool = roll == guess

        if won:
            self.datastore.change(str(ctx.author.id), "coins_wallet", bet * 6, "+")
        else:
            self.datastore.change(str(ctx.author.id), "coins_wallet", bet, "-")
        
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
    async def roulette(self, ctx, bet : int = commands.parameter(description="The amount to bet."), option : str = commands.parameter(description=":\n\t\todds 2:1\n\t\tevens 2:1\n\t\tred 2:1\n\t\tblack 2:1\n\t\tnumber : 35:1")):
        """Classic roulette, bet coins on any normal roulette option

        Args:
            ctx (_type_): Context from Discord.Py
            bet (int): The amount of coins to bet
            option (_type_, optional): The option to bet on.

        Raises:
            commands.CheckFailure: _description_
        """

        if option not in ["odds", "evens", "red", "black"]:
            if not option.isdigit() or not (0 <= int(option) <= 36):
                raise commands.BadArgument("Invalid roulette option.")
        
        wallet : int = self.datastore.fetch(str(ctx.author.id), "coins_wallet") or 0
        if wallet < bet:
            raise commands.CheckFailure

        roll : int = random.randint(0, 36)
        
        payout : int = 0
        colorEmoji : str

        if roll == 0:
            colorEmoji = "green_square"
        elif roll % 2 == 0:
            colorEmoji = "black_large_square"
        else:
            colorEmoji = "red_square"

        if ((option == "evens" or option == "black") and roll % 2 == 0) or ((option == "odds" or option == "red") and roll % 2 == 1):
            payout = 2
        elif int(option) == roll:
            payout = 35

        if payout != 35 and roll == 0:
            payout = 0
            colorEmoji = "green_square"

        if payout > 0:
            self.datastore.change(str(ctx.author.id), "coins_wallet", bet * payout, "+")
        else:
            self.datastore.change(str(ctx.author.id), "coins_wallet", bet, "-")

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