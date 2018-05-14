#!/usr/bin/python
# -*- coding: utf-8 -*-

"""interactions with Google Trends"""

import copy
import random
from enum import Enum
from logging import getLogger
from typing import Dict, List, Optional

from discord import Member
from pytrends.request import TrendReq
from pytrends.exceptions import ResponseError

from urllib.parse import quote
__log__ = getLogger(__name__)


def get_google_trends_url(words: List[str]) -> str:
    """Create a url to a google trends page with the inputted words queried"""
    return "https://trends.google.com/trends/explore" + "?q={}".format(",".join(map(quote, words)))


class InvalidGameStateError(RuntimeError):
    pass


# {theme: [questions]}
QUESTSIONS = [
    # naughty
    "lewd",
    "porn",
    "hentai",
    "prison",
    "assault",
    "nudes",
    "noods",
    "rule34",
    "rule63",
    "fapfic",

    # normal
    "cat",
    "dog",
    "food",
    "wedding",

    # movies
    "disney",
    "pixar",
    "anime",
    "fanfic",

    # video games
    "game",
    "vrchat",
    "steam",
    "update",
    "patch",
    "twitch",
    "stream",
    "minecraft",
    "roblox",
    "VR",
    "skyrim",
    "zelda",
    "mario",

    # computers,
    "discord",
    "facebook",
    "youtube",
    "google",
    "instagram",
    "snapchat",
    "myspace",
    "spotify",
    "windows",
    "mac",
    "apple",
    "linux",

    # political
    "obama",
    "trump",
    "the queen",
    "russia",
    "china",
    "US",
    "wall",
    "republican",
    "democrat",
    "election",
    "immigration",

    # inside jokes
    "respect",
    "ramen",
    "thot",
    "a fly in the wind",
    "cummies",
]


class Position(Enum):
    front = "front"
    back = "back"


class GoogleTrendsGame:
    """Google trends game class"""
    trender: TrendReq
    scores: Dict[Member, int]
    # words for a current round implemented as a dictionary mapped
    # to the user and the word the user submitted
    # resets every round
    words: Dict[Member, str]
    # resets every round
    question: str

    def __init__(self):
        self.trender = TrendReq()
        self.scores = {}
        self.words = {}
        self.question = None
        self.available_questions = copy.copy(QUESTSIONS)

    def start_round(self):
        """Start a round of GoogleTrendsGame"""
        # ensure we are not in the middle of a round
        if self.words or self.question:
            raise InvalidGameStateError("A round is already in progress")
        self.question = random.choice(self.available_questions)
        self.available_questions.remove(self.question)

    def add_word(self, word: str, player: Member, position: Position = Position.front) -> str:
        """Add a players word to the rounds words"""
        if position == Position.front:
            self.words[player] = "{} {}".format(word, self.question)
        elif position == position.back:
            self.words[player] = "{} {}".format(self.question, word)
        else:
            raise ValueError("Invalid Position: {}".format(position))

        # add the player to the scores if they are not already
        if player not in self.scores:
            self.scores[player] = 0
        return self.words[player]

    def end_round(self) -> Optional[Dict[str, int]]:
        """End a round of GoogleTrendsGame"""
        # ensure we are in a round
        if not self.words or not self.question:
            raise InvalidGameStateError("No round in progress to end")

        __log__.debug("requesting google trends interest over time for the "
                      "following terms: {}".format(self.words.values()))

        self.trender.build_payload(self.words.values())

        # todo: make special response for empty response
        try:
            df = self.trender.interest_over_time()
        except ResponseError:
            return

        try:
            df = df.drop(columns=["isPartial"])
        except ValueError:
            pass

        # todo: make special response for empty response
        if df.empty:
            return

        __log__.debug("obtained the following data frame: {}".format(df))
        # get the most recent trend numbers
        wintuples = dict(zip(df.columns.tolist(), df.values[-1].tolist()))

        for player in self.words:
            self.scores[player] += wintuples[self.words[player]]
        # cleanup the current round
        self.words.clear()
        self.question = None

        return wintuples
