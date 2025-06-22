import discord
from discord.ext import commands

from typing import Optional

@commands.is_owner()
class OwnerOnly(commands.Cog):
    def __init__(self, datastore, emojis):
        self.datastore = datastore
        self.emojis = emojis

    @commands.command(
        help = "Adds a coin amount to a user",
        hidden = True
    )
    async def add(self, ctx, user : Optional[discord.Member] = None, amount = 0):
        user = user or ctx.author

        self.datastore.change(str(user.id), "coins_wallet", amount, "+")

        await ctx.reply(f"Successfully addded {self.emojis["coin"]} **{amount}** to **{user}**'s wallet") 