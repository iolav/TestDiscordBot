import discord
from discord.ext import commands

from typing import Optional

from datetime import datetime, timedelta

class Economy(commands.Cog):
    def __init__(self, datastore, emojis):
        self.datastore = datastore
        self.emojis = emojis

    @commands.command(
        help="Displays your or another user's wallet and bank balance."
    )
    async def bal(self, ctx, user : Optional[discord.Member] = commands.parameter(default=None, description="Optional - the user to check the balance of.")):
        user = user or ctx.author

        wallet : int = self.datastore.fetch(str(user.id), "coins_wallet") or 0
        bank : int = self.datastore.fetch(str(user.id), "coins_bank") or 0

        embed = discord.Embed(
            title = f"{user}'s Balance",
            description = f"{self.emojis["wallet"]} Wallet: {self.emojis["coin"]} **{wallet}**\n\n{self.emojis["bank"]} Bank: {self.emojis["coin"]} **{bank}**",
            colour=0xf5d400
        )

        await ctx.reply(embed=embed)

    @commands.command(
        help="Shows the global leaderboard.",
        aliases = ["lb"]
    )
    async def leaderboard(self, ctx):
        data : dict = self.datastore.fetchAll()

        sortedData = sorted(
            data.items(),
            key=lambda item: int(item[1]["coins_wallet"]) + int(item[1]["coins_bank"]),
            reverse=True
        )

        curPlace : int = 1
        output : str = ""
        for userId, userData in sortedData:
            rankEmoji : str = ""
            match curPlace:
                case 1:
                    rankEmoji = ":medal: "
                case 2:
                    rankEmoji = ":second_place: "
                case 3:
                    rankEmoji = ":third_place: "
                
            total : int = int(userData["coins_wallet"]) + int(userData["coins_bank"])
            output += f"{rankEmoji}<@{userId}> :  {self.emojis["coin"]} **{total}**\n"

            curPlace += 1
        
        embed = discord.Embed(
            title = "Global Leaderboard",
            description = output,
            colour=0xf5d400
        )

        await ctx.reply(embed=embed)

    @commands.command(
        help="Withdraws coins from your bank balance.",
        aliases = ["with"]
    )
    async def withdraw(self, ctx, amount : int = commands.parameter(description="The amount to withdraw.")):
        if amount < 1:
            raise commands.BadArgument("The withdraw amount must be greater than 0, use $help for assistance.")

        bank : int = self.datastore.fetch(str(ctx.author.id), "coins_bank") or 0
        if amount > bank:
            raise commands.CheckFailure("Your requested withdraw amount is greater than your bank balance!")
        
        self.datastore.change(str(ctx.author.id), "coins_bank", amount, "-")
        self.datastore.change(str(ctx.author.id), "coins_wallet", amount, "+")

        await ctx.reply(f"Successfully withdrew {self.emojis["coin"]} **{amount}**") 

    @commands.command(
        help="Deposits coins into your bank balance.",
        aliases = ["dep"]
    )
    async def deposit(self, ctx, amount : int = commands.parameter(description="The amount to deposit.")):
        if amount < 1:
            raise commands.BadArgument("The deposit amount must be greater than 0, use $help for assistance.")

        wallet : int = self.datastore.fetch(str(ctx.author.id), "coins_wallet") or 0
        if amount > wallet:
            raise commands.CheckFailure("Your requested deposit amount is greater than your wallet balance!")
        
        self.datastore.change(str(ctx.author.id), "coins_wallet", amount, "-")
        self.datastore.change(str(ctx.author.id), "coins_bank", amount, "+")

        await ctx.reply(f"Successfully deposited {self.emojis["coin"]} **{amount}**") 

    @commands.command(
        help="Claims your daily coin bonus. Avalible every 12 hours."
    )
    async def daily(self, ctx):
        lastTimeStr : str = self.datastore.fetch(str(ctx.author.id), "last_daily")
        timeNow : datetime = datetime.now()

        if lastTimeStr:
            lastTime = datetime.fromisoformat(lastTimeStr)

            if timeNow - lastTime < timedelta(hours = 12):
                raise commands.CheckFailure("You've already claimed your bonus in the last 12 hours!")
            
        self.datastore.change(str(ctx.author.id), "last_daily", timeNow.isoformat(), "=")
        self.datastore.change(str(ctx.author.id), "coins_wallet", 100, "+")

        await ctx.reply(f"Successfully claimed {self.emojis["coin"]} **100** daily bonus.")