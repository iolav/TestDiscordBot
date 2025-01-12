import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from typing import Final
import json

load_dotenv()

TOKEN : Final = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True

client = commands.Bot(command_prefix="$", intents=intents)

@client.event
async def on_ready():
    pass

@client.command()
async def test(ctx, user):
    embed = discord.Embed(title=f"{user}'s Balance",
                      description="<a:goldcoin:1328125082861572228> 500")
    await ctx.reply(embed=embed)

client.run(TOKEN)