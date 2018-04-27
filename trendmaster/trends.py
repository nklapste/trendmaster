#!/usr/bin/python
# -*- coding: utf-8 -*-

"""interactions with Google Trends"""

from typing import Dict, List

from discord import Member
from pytrends.request import TrendReq


def get_google_trends_url(words: List[str]) -> str:
    """Create a url to a google trends page with the inputted words queried"""
    return "https://trends.google.com/trends/explore" + "?q={}".format(",".join(words))


class InvalidGameStateError(RuntimeError):
    pass


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
        # TODO: make internal getter/setter
        self.scores = {}
        self.words = {}
        self.question = None

    def start_round(self):
        """Start a round of GoogleTrendsGame"""
        # ensure we are not in the middle of a round
        if self.words or self.question:
            raise InvalidGameStateError("A round is already in progress")

        # TODO: set round_question
        self.question = "{} update"

    def add_word(self, word: str, player: Member):
        """Add a players word to the rounds words"""
        self.words[player] = self.question.format(word)
        if player not in self.scores:
            self.scores[player] = 0
        return self.words[player]

    def end_round(self):
        """End a round of GoogleTrendsGame"""
        # ensure we are in a round
        if not self.words or not self.question:
            raise InvalidGameStateError("No round in progress to end")

        self.trender.build_payload(self.words.values())
        df = self.trender.interest_over_time()
        df = df.drop(columns=["isPartial"])
        wintuples = dict(zip(df.columns.tolist(), df.values[-1].tolist()))

        for player in self.words:
            self.scores[player] += wintuples[self.words[player]]

        # cleanup the current round
        self.words.clear()
        self.question = None

        return wintuples
