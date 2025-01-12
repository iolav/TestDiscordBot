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

@client.event
async def on_ready():
    global datastore
    datastore = Datastore("savedata.json")

@client.command()
async def bal(ctx, user : Optional[discord.Member] = None):
    user = user or ctx.author
    balance : int = datastore.fetch(user.id, "coins") or 0

    embed = discord.Embed(title=f"{user}'s Balance",
                      description=f"<a:goldcoin:1328125082861572228> **{balance}** coins")
    await ctx.reply(embed=embed)

@client.command()
async def add(ctx, amount : int = 0, user : Optional[discord.Member] = None):
    user = user or ctx.author

    if any(role.permissions.administrator for role in ctx.author.roles):
        await ctx.reply(f"Lacking required permissions, operation failed")

        return

    datastore.change(user.id, "coins", amount, "+")

    await ctx.reply(f"Successfully addded <a:goldcoin:1328125082861572228> **{amount}** coins to user {user}")

client.run(TOKEN)