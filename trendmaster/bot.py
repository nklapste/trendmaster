#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Discord bot api"""

import operator
from logging import getLogger
from typing import Dict, Optional

from discord import Server, Channel, Embed
from discord.ext import commands
from discord.ext.commands import Bot, BucketType
from discord.ext.commands.context import Context


from trendmaster.trends import GoogleTrendsGame, get_google_trends_url, \
    Position, InvalidGameStateError

DESCRIPTION = """A Discord bot for playing a "Family Feud" like game using the
Google Trends analytics engine!"""

BOT = commands.Bot(command_prefix=["trendmaster ", "%T "], description=DESCRIPTION)


__log__ = getLogger(__name__)


@BOT.event
async def on_ready():
    """Startup logged callout/setup"""
    __log__.info("logged in as: {}".format(BOT.user.id))


class TrendMaster:
    """Discord bot GoogleTrendsGame interaction class"""
    bot: Bot
    active_games: Dict[Server, Dict[Channel, GoogleTrendsGame]]

    def __init__(self, bot: Bot):
        self.bot = bot
        self.active_games = {}

    @staticmethod
    def _create_scores_embed(scores) -> Embed:
        current_scores_embed = Embed(
            title="Scores",
            description="The current GoogleTrendsGame's player scores:"
        )
        for player, score in scores:
            current_scores_embed.add_field(name=player, value=score)
        return current_scores_embed

    async def _get_channel_game(self, ctx: Context) -> Optional[GoogleTrendsGame]:
        """Get the current channel's GoogleTrendsGame"""
        try:
            return self.active_games[ctx.message.server][ctx.message.channel]
        except KeyError:
            await self.bot.say(
                "**ERROR:** A GoogleTrendsGame is not active in this channel!\n"
                "Please start a GoogleTrendsGame by using the `game start` "
                "command before using the previous command!"
            )

    @commands.group()
    async def game(self):
        """Subcommands relating to GoogleTrendsGames. Type
        `trendmaster help game` for more available subcommands."""
        pass

    @game.command("start", pass_context=True)
    async def start_game(self, ctx: Context):
        """Start a new game of a GoogleTrendsGame in the current channel"""
        self.active_games[ctx.message.server] = self.active_games.get(
            ctx.message.server, {})
        if self.active_games[ctx.message.server].get(ctx.message.channel):
            await self.bot.say(
                "**ERROR:** A GoogleTrendsGame is already active in this channel!\n"
                "Please end it using `game end` before starting a new game!"
            )
        else:
            self.active_games[ctx.message.server][ctx.message.channel] = GoogleTrendsGame()
            game_start_embed = Embed(
                title="Game Start",
                description="A new GoogleTrendsGame is starting!"
            )
            await self.bot.say(
                embed=game_start_embed
            )

    @game.command(pass_context=True)
    async def scores(self, ctx: Context):
        """Report the channel's GoogleTrendsGame's scores"""
        active_game = await self._get_channel_game(ctx)
        await self.bot.say(
            embed=self._create_scores_embed(active_game.scores.items())
        )

    @game.command(pass_context=True)
    async def list(self, ctx: Context):
        """List the GoogleTrendsGames active on the server's channels"""
        self.active_games[ctx.message.server] = self.active_games.get(
            ctx.message.server, {})
        active_games_embed = Embed(
            title="Active GoogleTrendsGames",
            description="The following channels have active GoogleTrendsGames:"
        )
        for channel in self.active_games[ctx.message.server].keys():
            active_games_embed.add_field(name=channel.name, value=None)
        await self.bot.say(embed=active_games_embed)

    @game.command("end", pass_context=True)
    async def end_game(self, ctx: Context):
        """End the channel's GoogleTrendsGame"""
        active_game = await self._get_channel_game(ctx)
        scores = active_game.scores
        winner = max(scores.items(), key=operator.itemgetter(1))[0]

        # post the game winner
        winner_embed = Embed(
            title="Game End",
            description="The GoogleTrendsGame has ended!"
        )
        winner_embed.add_field(name="Winner", value="**{}** wins with **{}** points!\n".format(winner, scores[winner]))
        await self.bot.say(embed=winner_embed)

        # post the current scores
        await self.bot.say(
            embed=self._create_scores_embed(active_game.scores.items())
        )

        # remove the current game from the active games
        self.active_games[ctx.message.server].pop(ctx.message.channel)

    @commands.group()
    async def round(self):
        """Subcommands relating to a GoogleTrendsGame's round. Type
        `trendmaster help round` for more available subcommands."""
        pass

    @round.command("start", pass_context=True)
    async def start_round(self, ctx: Context):
        """Start a new round of a GoogleTrendsGame in the current channel"""
        # TODO: ensure not overwriting another active round
        active_game = await self._get_channel_game(ctx)
        try:
            active_game.start_round()
        except InvalidGameStateError:
            await self.bot.say(
                "**ERROR:** A round is already in progress!\n"
                "Please end it using `round end` before starting a new round!"
            )
        else:
            round_start_embed = Embed(
                title="Round Start",
                description="A new GoogleTrendsGame round is starting!"
            )
            round_start_embed.add_field(name="Round Trend Term", value=active_game.question)
            await self.bot.say(
                embed=round_start_embed
            )
        # TODO: add timer that automatically ends the round

    @round.command("end", pass_context=True)
    @commands.cooldown(rate=1, per=5, type=BucketType.user)
    async def end_round(self, ctx: Context):
        """End the channel's GoogleTrendsGame's round"""
        # post the google trends frontend results link
        active_game = await self._get_channel_game(ctx)
        # post a link to the direct google trends data

        question = active_game.question
        await self.bot.say(
            get_google_trends_url(list(active_game.words.values()))
        )

        round_results_embed = Embed(
            title="Round End",
            description="Results for this round's term: **{}**".format(question)
        )
        round_results = active_game.end_round()
        for word, score in round_results.items():
            round_results_embed.add_field(name=word, value=score)
        await self.bot.say(embed=round_results_embed)

        # post the current scores
        await self.bot.say(
            embed=self._create_scores_embed(active_game.scores.items())
        )

    @round.command(pass_context=True)
    async def word(self, ctx: Context, word: str, position: Position = Position.front):
        """Add a word to the channel's GoogleTrendsGame's round

        :param word: word to appended either to the front or back of the rounds
            question term.
        :param position: (OPTIONAL) specify "front" or "back" to note where to
            place your word relative the question term. (Default: "front")
        """
        active_game = await self._get_channel_game(ctx)
        await self.bot.whisper(
            "Your round's response was: **{}**".format(
                active_game.add_word(word.strip(), ctx.message.author, position)
            )
        )


BOT.add_cog(TrendMaster(BOT))
