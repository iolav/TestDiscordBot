import discord
from discord.ext import commands

import asyncio
import random
import json

class Blackjack(discord.ui.View):
    def __init__(self, embed, emojis):
        super().__init__(timeout = None)

        self.embed = embed
        self.emojis = emojis
        
        self.deck = list(self.emojis.keys()) * 2

        self.plrHand = []
        self.dealerHand = []
        for _ in range(2):
            self.plrHand.append(self.getRandCard())
            self.dealerHand.append(self.getRandCard())

    def getRandCard(self):
        card = random.choice(self.deck)

        self.deck.remove(card)
        
        return card
    
    def getScore(self, hand):
        score : int = 0

        for card in hand:
            value, suit = card.split("_")

            if value == "king" or value == "queen" or value == "jack":
                score += 10
            elif value == "ace":
                score += 11
            else:
                score += int(value)

        return score

    def getHand(self, hand):
        output : str = "ㅤ" if hand == self.dealerHand else ""

        for card in hand:
            output += self.emojis[card]

        return output

    @discord.ui.button(label = "Hit", style = discord.ButtonStyle.blurple)
    async def hit(self, interaction : discord.Interaction, button):
        self.plrHand.append(self.getRandCard())

        score : int = self.getScore(self.plrHand)

        if score > 21:
            button.disabled = True

            self.embed.add_field(name = "Bust! You lose.",
                        value = "",
                        inline = False)

        self.embed.set_field_at(0,
                        name = "Your hand",
                        value = self.getHand(self.plrHand),
                        inline = True)
        self.embed.set_field_at(2,
                        name = "",
                        value = f"Your score: {score}ㅤㅤDealer's score: {self.getScore(self.dealerHand)}",
                        inline = False)

        await interaction.response.edit_message(embed = self.embed, view = self)

    @discord.ui.button(label = "Stand", style = discord.ButtonStyle.green)
    async def stand(self, interaction : discord.Interaction, button):
        pass

class Gambling(commands.Cog):
    def __init__(self, datastore, emojis : dict[str]):
        self.datastore = datastore
        self.emojis = emojis

        with open("cards.json", "r") as file:
            self.cardEmojis = json.load(file)

    @commands.command(
        help = "Bet any amount on a dice roll, 1-6 odds, win 6x your bet."
    )
    async def dice(self, ctx, bet : int = commands.parameter(description="The amount to bet."), guess : int = commands.parameter(description="The number to bet on.")):
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
        help = "Bet any amount on multiple options with different payouts.",
        aliases = ["rl"]
    )
    async def roulette(self, ctx, bet : int = commands.parameter(description="The amount to bet."), option : str = commands.parameter(description=":\n\t\todds 2:1\n\t\tevens 2:1\n\t\tred 2:1\n\t\tblack 2:1\n\t\t<number> 35:1")):
        if option not in ["odds", "evens", "red", "black"]:
            if not option.isdigit() or not (0 <= int(option) <= 36):
                raise commands.BadArgument("Invalid roulette option.")
        
        wallet : int = self.datastore.fetch(str(ctx.author.id), "coins_wallet") or 0
        if wallet < bet:
            raise commands.CheckFailure

        roll : int = random.randint(0, 36)
        
        payout : int = 0
        colorEmoji : str = ""

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
            description=f"{self.emojis["wheel"]}ㅤ**Rolling...**ㅤ{self.emojis["wheel"]}",
            colour=0x00b0f4
        )

        endEmbed = discord.Embed(
            title=f"{ctx.author}'s Roulette spin",
            description=f":{colorEmoji}:ㅤ**{roll}**ㅤ:{colorEmoji}:\n\n{'You win!' if payout > 0 else 'You lose!'}",
            colour=0x38ff4f if payout > 0 else 0xff3838
        )
        
        message = await ctx.reply(embed = startEmbed)

        await asyncio.sleep(3)

        await message.edit(embed = endEmbed)

    @commands.command(
        help = "Play a blackjack game against a computer dealer. 2 decks, dealer must stand on a 17 and draw to 16, and blackjack pays 3:2.",
        aliases = ["bj"]
    )
    async def blackjack(self, ctx):
        embed = discord.Embed()
        embed.set_author(name = f"{ctx.author}'s Blackjack game")

        game = Blackjack(embed, self.cardEmojis)

        embed.add_field(name = "Your hand",
                        value = game.getHand(game.plrHand),
                        inline = True)
        embed.add_field(name = "ㅤDealer's hand",
                        value = game.getHand(game.dealerHand),
                        inline = True)
        embed.add_field(name = "",
                        value = f"Your score: {game.getScore(game.plrHand)}ㅤㅤDealer's score: {game.getScore(game.dealerHand)}",
                        inline = False)
        embed.colour = 0x00b0f4

        await ctx.reply(embed = embed, view = game)