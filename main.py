import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from typing import Final, Optional
from datastore import Datastore
import asyncio
import random

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
        description = f"{emojis["wallet"]} Wallet: {emojis["coin"]} **{wallet}**\n\n{emojis["bank"]} Bank: {emojis["coin"]} **{bank}**",
        colour=0xf5d400
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

@client.command()
async def dice(ctx, amount : int = 0):
    if amount == 0:
        await ctx.reply(f"You have to bet at least {emojis["coin"]} 1!")

        return
    
    startEmbed = discord.Embed(
        title=f"{ctx.author}'s Dice roll",
        description="🎲ㅤ**Rolling...**ㅤ🎲",
        colour=0x00b0f4
    )
    endEmbed = discord.Embed(  
        title=f"{ctx.author}'s Dice roll",
        description=f"🎲ㅤ**{random.randint(1, 6)}**ㅤ🎲", #Add win/loose and change color of embed and do coins stuff
        colour=0x00b0f4
    )
    
    message = await ctx.reply(embed=startEmbed)

    await asyncio.sleep(3)

    await message.edit(embed=endEmbed)

client.run(TOKEN)