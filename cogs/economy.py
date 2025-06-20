import discord
from discord.ext import commands

from typing import Optional

class Economy(commands.Cog):
    def __init__(self, datastore, emojis):
        self.datastore = datastore
        self.emojis = emojis

    @commands.command(
        help="Displays your or another user's wallet and bank balance."
    )
    async def bal(self, ctx, user : Optional[discord.Member] = commands.parameter(default=None, description="Optional - the user to check the balance of.")):
        """Checks the balance of a user

        Args:
            ctx (_type_): Context from Discord.Py
            user (Optional[discord.Member], optional): The user to check the balance of, optional to check your own if no user provided. Defaults to None.
        """

        user = user or ctx.author

        wallet : int = self.datastore.fetch(str(user.id), "coins_wallet") or 0
        bank : int = self.datastore.fetch(str(user.id), "coins_bank") or 0

        embed = discord.Embed(
            title = f"{user}'s Balance",
            description = f"{self.emojis["wallet"]} Wallet: {self.emojis["coin"]} **{wallet}**\n\n{self.emojis["bank"]} Bank: {self.emojis["coin"]} **{bank}**",
            colour=0xf5d400
        )

        await ctx.reply(embed=embed)