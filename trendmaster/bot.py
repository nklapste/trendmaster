#!/usr/bin/python
# -*- coding: utf-8 -*-

""""""

from logging import getLogger

from discord.ext import commands
from discord.ext.commands import Bot
from discord.ext.commands.context import Context

DESCRIPTION = """"""

BOT = commands.Bot(command_prefix="trendmaster", description=DESCRIPTION)

__log__ = getLogger(__name__)


@BOT.event
async def on_ready():
    """Startup logged callout/setup"""
    __log__.info("logged in as: {}".format(BOT.user.id))


class Config:
    """"""
    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def primify(self, ctx: Context):
        """"""


BOT.add_cog(Config(BOT))
