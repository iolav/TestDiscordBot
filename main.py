import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from typing import Final, Optional
from datastore import Datastore

load_dotenv()

TOKEN : Final = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True

client = commands.Bot(command_prefix="$", intents=intents)

emojis = {
    "coin" : "<a:goldcoin:1328125082861572228>",
    "wallet" : "<:wallet:1328163268522410095>",
    "bank" : "<:bank2:1328163595434987551>"
}

@client.event
async def on_ready():
    global datastore
    datastore = Datastore("savedata.json")

@client.command()
async def bal(ctx, user : Optional[discord.Member] = None):
    user = user or ctx.author

    wallet : int = datastore.fetch(str(user.id), "coins_wallet") or 0
    bank : int = datastore.fetch(str(user.id), "coins_bank") or 0

    embed = discord.Embed(
        title = f"{user}'s Balance",
        description = f"{emojis["wallet"]} Wallet: {emojis["coin"]} **{wallet}**\n\n{emojis["bank"]} Bank: {emojis["coin"]} **{bank}**"
    )

    await ctx.reply(embed=embed)

@client.command()
async def add(ctx, amount : int = 0, user : Optional[discord.Member] = None):
    user = user or ctx.author

    if any(role.permissions.administrator for role in ctx.author.roles):
        await ctx.reply(f"Lacking required permissions, operation failed")

        return

    datastore.change(str(user.id), "coins_wallet", amount, "+")

    await ctx.reply(f"Successfully addded {emojis["coin"]} **{amount}** to **{user}**'s wallet")

client.run(TOKEN)