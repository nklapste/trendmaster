#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Discord bot api"""

import operator
from logging import getLogger
from typing import Dict, Optional

from discord import Server, Channel
from discord.ext import commands
from discord.ext.commands import Bot
from discord.ext.commands.context import Context


from trendmaster.trends import GoogleTrendsGame, get_google_trends_url, Position


DESCRIPTION = """A Discord bot for playing a "Family Feud" like game using 
Google Trends!"""

BOT = commands.Bot(command_prefix=["trendmaster ", "!t"], description=DESCRIPTION)


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

    def _get_channel_game(self, ctx: Context) -> Optional[GoogleTrendsGame]:
        """Get the current channel's GoogleTrendsGame"""
        try:
            return self.active_games[ctx.message.server][ctx.message.channel]
        except KeyError:
            self.bot.send_message(
                ctx.message.channel,
                "A GoogleTrendsGame is not active in this channel!\n"
                "Please start one using `start_game` before using the previous command!"
            )
            raise

    @commands.command(pass_context=True)
    async def games(self, ctx: Context):
        """List the GoogleTrendsGames active on the server's channels"""
        self.active_games[ctx.message.server] = self.active_games.get(ctx.message.server, {})
        await self.bot.send_message(
            ctx.message.channel,
            "The following channels have active GoogleTrendsGames:\n{}".format(
                "\n".join([channel.name for channel in self.active_games[ctx.message.server].keys()])
            )
        )

    @commands.command(pass_context=True)
    async def start_game(self, ctx: Context):
        """Start a new game of a GoogleTrendsGame in the current channel"""
        self.active_games[ctx.message.server] = self.active_games.get(ctx.message.server, {})
        if self.active_games[ctx.message.server].get(ctx.message.channel):
            await self.bot.send_message(
                ctx.message.channel,
                "A GoogleTrendsGame is already active in this channel!\n"
                "Please end it using `end_game` before starting a new game!"
            )
        else:
            self.active_games[ctx.message.server][ctx.message.channel] = GoogleTrendsGame()
            await self.bot.send_message(
                ctx.message.channel,
                "Starting a new GoogleTrendsGame in the current channel!"
            )

    @commands.command(pass_context=True)
    async def start_round(self, ctx: Context):
        """Start a new round of a GoogleTrendsGame in the current channel"""
        # TODO: ensure not overwriting another active round
        active_game = self._get_channel_game(ctx)
        active_game.start_round()
        await self.bot.send_message(
            ctx.message.channel,
            "Round started!\n"
            "The current rounds question is: {}".format(
                active_game.question
            )
        )
        # TODO: add timer that automatically ends the round

    @commands.command(pass_context=True)
    async def word(self, ctx: Context, word: str, position: str = "front"):
        """Add a word to the channel's GoogleTrendsGame's round

        :param word: word to appened either to the front or back of the rounds
            question term.
        :param position: (OPTIONAL) specify "front" or "back" to note where to
            place your word relative the question term. (Default: "front")
        """
        active_game = self._get_channel_game(ctx)
        await self.bot.whisper(
            "Your round's response was: {}".format(
                active_game.add_word(word.strip(), ctx.message.author, Position(position.lower().strip()))
            )
        )

    @commands.command(pass_context=True)
    async def end_round(self, ctx: Context):
        """End the channel's GoogleTrendsGame's round"""
        # post the google trends frontend results link
        active_game = self._get_channel_game(ctx)
        await self.bot.send_message(
            ctx.message.channel,
            get_google_trends_url(list(active_game.words.values()))
        )

        # post the round results backend data
        round_results = active_game.end_round()
        await self.bot.send_message(
            ctx.message.channel,
            "Round ended!\n"
            "Round results: {}".format(round_results)
        )

        # post the games current scores
        await self.scores(ctx)

    @commands.command(pass_context=True)
    async def end_game(self, ctx: Context):
        """End the channel's GoogleTrendsGame"""
        active_game = self._get_channel_game(ctx)
        scores = active_game.scores
        winner = max(scores.items(), key=operator.itemgetter(1))[0]
        await self.bot.send_message(
            ctx.message.channel,
            "Game ended!\n"
            "{} wins with {} points!\n"
            "The ending scores are:\n{}".format(winner, scores[winner], "\n".join(["{}: {}".format(k, v) for k, v in scores.items()]))
        )
        # remove the current game from the active games
        self.active_games[ctx.message.server].pop(ctx.message.channel)

    @commands.command(pass_context=True)
    async def scores(self, ctx: Context):
        """Report the channel's GoogleTrendsGame's scores"""
        active_game = self._get_channel_game(ctx)
        scores = active_game.scores
        await self.bot.send_message(
            ctx.message.channel,
            "The current scores are:\n{}".format(
                "\n".join(["{}: {}".format(k, v) for k, v in scores.items()])
            )
        )


BOT.add_cog(TrendMaster(BOT))
