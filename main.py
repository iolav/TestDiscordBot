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

emojis : Final[dict] = {
    "coin" : "<a:goldcoin:1328517822497685535>",
    "wallet" : "<:wallet:1328163268522410095>",
    "bank" : "<:bank2:1328163595434987551>"
}

@client.event
async def on_ready():
    global datastore
    datastore = Datastore("savedata.json")

@client.command(
        help="Displays your or another user's wallet and bank balance.",
        breif="Displays balance."
)
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
async def add(ctx, amount = 0, user : Optional[discord.Member] = None):
    user = user or ctx.author

    if any(role.permissions.administrator for role in ctx.author.roles):
        await ctx.reply(f"Lacking required permissions, operation failed")

        return

    datastore.change(str(user.id), "coins_wallet", amount, "+")

    await ctx.reply(f"Successfully addded {emojis["coin"]} **{amount}** to **{user}**'s wallet")

@client.command()
async def dice(ctx, bet : Optional[int] = None, guess : Optional[int] = None):
    if not bet or not guess:
        await ctx.reply("Incorrect usage! Use $help for assistance.")
        return

    if not bet or bet <= 0:
        await ctx.reply(f"You have to bet at least {emojis["coin"]} **1**!")
        return
    if not guess or guess < 1 or guess > 6:
        await ctx.reply("Your guess must be between 1 and 6!")
        return
    
    wallet : int = datastore.fetch(str(ctx.author.id), "coins_wallet") or 0
    if wallet < bet:
        await ctx.reply("Your bet is bigger than your wallet balance!")
        return

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

client.run(TOKEN)