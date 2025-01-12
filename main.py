import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from typing import Final
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
async def bal(ctx, user):
    embed = discord.Embed(title=f"{user}'s Balance",
                      description="<a:goldcoin:1328125082861572228> 500")
    await ctx.reply(embed=embed)

@client.command()
async def addtest(ctx):
    datastore.change(ctx.guild.id, ctx.author.id, "coins", 100, "+")

client.run(TOKEN)