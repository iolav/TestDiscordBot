import discord
from discord.ext import commands

import asyncio
import random
import json
import math

class Blackjack(discord.ui.View):
    def __init__(self, embed, emojis, cardEmojis, bet, datastore, authorId):
        super().__init__(timeout = None)

        self.embed = embed
        self.emojis = emojis
        self.cardEmojis = cardEmojis
        self.bet = bet
        self.datastore = datastore
        self.authorId = authorId
        
        self.deck = list(self.cardEmojis.keys()) * 2

        self.plrHand = []
        self.dealerHand = []
        for _ in range(2):
            self.plrHand.append(self.getRandCard())

        self.dealerHand.append(self.getRandCard())

        if self.getScore(self.plrHand) == 21:
            for child in self.children:
                child.disabled = True # type: ignore
                
            self.datastore.change(str(self.authorId), "coins_wallet", math.floor(self.bet * 2.5), "+")

    def getRandCard(self):
        card = random.choice(self.deck)

        self.deck.remove(card)
        
        return card
    
    def getScore(self, hand):
        score = 0
        aceCount = 0

        for card in hand:
            value, _ = card.split("_")

            if value in ["king", "queen", "jack"]:
                score += 10
            elif value == "ace":
                score += 11
                aceCount += 1
            else:
                score += int(value)

        while score > 21 and aceCount > 0:
            score -= 10
            aceCount -= 1

        return score

    def getHand(self, hand):
        output : str = "ㅤ" if hand == self.dealerHand else ""

        for card in hand:
            output += self.cardEmojis[card]

        if hand == self.dealerHand and len(hand) == 1:
            output += self.emojis["card_back"]

        return output
    
    def playDealer(self):
        while self.getScore(self.dealerHand) < 17:
            self.dealerHand.append(self.getRandCard())

        self.embed.set_field_at(1,
                        name = "ㅤDealer's hand",
                        value = self.getHand(self.dealerHand),
                        inline = True)
        self.embed.set_field_at(2,
                        name = "",
                        value = f"Value: **{self.getScore(self.plrHand)}**ㅤㅤValue: **{self.getScore(self.dealerHand)}**",
                        inline = False)
        

    @discord.ui.button(label = "Hit", style = discord.ButtonStyle.blurple)
    async def hit(self, interaction : discord.Interaction, button):
        if interaction.user.id != self.authorId: return

        self.plrHand.append(self.getRandCard())

        score : int = self.getScore(self.plrHand)
        if score > 21:
            for child in self.children:
                child.disabled = True # type: ignore

            self.embed.add_field(name = "Bust! You lose.",
                        value = "",
                        inline = False)
            self.embed.colour = 0xff3838

        self.embed.set_field_at(0,
                        name = "Your hand",
                        value = self.getHand(self.plrHand),
                        inline = True)
        self.embed.set_field_at(2,
                        name = "",
                        value = f"Value: {score}ㅤㅤValue: {self.getScore(self.dealerHand)}",
                        inline = False)

        await interaction.response.edit_message(embed = self.embed, view = self)

    @discord.ui.button(label = "Stand", style = discord.ButtonStyle.green)
    async def stand(self, interaction : discord.Interaction, button):
        if interaction.user.id != self.authorId: return
        
        for child in self.children:
            child.disabled = True # type: ignore

        self.playDealer()

        plrScore : int = self.getScore(self.plrHand)
        dealerScore : int = self.getScore(self.dealerHand)
        if plrScore > dealerScore or dealerScore > 21:
            self.datastore.change(str(self.authorId), "coins_wallet", self.bet * 2, "+")

            self.embed.add_field(name = "Dealer busts, you win!" if dealerScore > 21 else f"{plrScore} beats {dealerScore}, you win!",
                            value = "",
                            inline = False)
            self.embed.colour = 0x38ff4f
        elif dealerScore > plrScore:
            self.embed.add_field(name = f"{dealerScore} beats {plrScore}, you lose.",
                            value = "",
                            inline = False)
            self.embed.colour = 0xff3838
        else:
            self.datastore.change(str(self.authorId), "coins_wallet", self.bet, "+")

            self.embed.add_field(name = "Score tied, push.",
                            value = "",
                            inline = False)
        
        await interaction.response.edit_message(embed = self.embed, view = self)

class Gambling(commands.Cog):
    def __init__(self, datastore, emojis : dict[str, str]):
        self.datastore = datastore
        self.emojis = emojis

        with open("cards.json", "r") as file:
            self.cardEmojis = json.load(file)

    @commands.command(
        help = "Bet any amount on a dice roll, 1-6 odds, pays 5:1"
    )
    async def dice(self, ctx, bet : int = commands.parameter(description="The amount to bet."), guess : int = commands.parameter(description="The number to bet on.")):
        if bet < 1:
            raise commands.BadArgument("The bet amount must be greater than 0, use $help for assistance.")
        
        if guess < 1 or guess > 6:
            raise commands.BadArgument("The dice number must be between 1 and 6, use $help for assistance.")
        
        wallet : int = self.datastore.fetch(str(ctx.author.id), "coins_wallet") or 0
        if wallet < bet:
            raise commands.CheckFailure("Your bet is bigger than your wallet balance!")

        roll : int = random.randint(1, 6)
        won : bool = roll == guess

        if won:
            self.datastore.change(str(ctx.author.id), "coins_wallet", bet * 5, "+")
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
    async def roulette(self, ctx, bet : int = commands.parameter(description="The amount to bet."), option : str = commands.parameter(description=":\n\t\todds 1:1\n\t\tevens 1:1\n\t\tred 1:1\n\t\tblack 1:1\n\t\t<number> 35:1")):
        if bet < 1:
            raise commands.BadArgument("The bet amount must be greater than 0, use $help for assistance.")

        if option in ["odds", "evens", "red", "black"]:
            pass
        elif option.isdigit() and 0 <= int(option) <= 36:
            pass
        else:
            raise commands.BadArgument("No valid roulette option found, use $help for assistance.")
        
        wallet : int = self.datastore.fetch(str(ctx.author.id), "coins_wallet") or 0
        if wallet < bet:
            raise commands.CheckFailure("Your bet is bigger than your wallet balance!")

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
            payout = 1
        elif option.isdigit() and int(option) == roll:
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
        help = "Play a blackjack game against a computer dealer.\n\n2 decks\nDealer must stand on a 17 and draw to 16\nBlackjack pays 3:2, win pays 1:1",
        aliases = ["bj"]
    )
    async def blackjack(self, ctx, bet : int = commands.parameter(description="The amount to bet.")):
        if bet < 1:
            raise commands.BadArgument("The bet amount must be greater than 0, use $help for assistance.")
        
        wallet : int = self.datastore.fetch(str(ctx.author.id), "coins_wallet") or 0
        if wallet < bet:
            raise commands.CheckFailure("Your bet is bigger than your wallet balance!")
        
        self.datastore.change(str(ctx.author.id), "coins_wallet", bet, "-")
        
        embed = discord.Embed()
        embed.set_author(name = f"{ctx.author}'s Blackjack game")

        game = Blackjack(embed, self.emojis, self.cardEmojis, bet, self.datastore, ctx.author.id)

        embed.add_field(name = "Your hand",
                        value = game.getHand(game.plrHand),
                        inline = True)
        embed.add_field(name = "ㅤDealer's hand",
                        value = game.getHand(game.dealerHand),
                        inline = True)
        embed.add_field(name = "",
                        value = f"Value: {game.getScore(game.plrHand)}ㅤㅤValue: {game.getScore(game.dealerHand)}",
                        inline = False)
        embed.colour = 0x00b0f4

        if game.getScore(game.plrHand) == 21:
            embed.add_field(name = "Blackjack, you win!",
                                value = "",
                                inline = False)
            embed.colour = 0x38ff4f

        await ctx.reply(embed = embed, view = game)