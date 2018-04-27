#!/usr/bin/python
# -*- coding: utf-8 -*-

"""pytests for trends.py"""

import pytest

from trendmaster.trends import GoogleTrendsGame, InvalidGameStateError, get_google_trends_url

from pytrends.request import TrendReq


class TestGoogleTrendsGame:

    def setup_method(self):
        self.game = GoogleTrendsGame()

        assert self.game
        assert isinstance(self.game, GoogleTrendsGame)
        assert self.game.question is None
        assert self.game.words == {}
        assert self.game.scores == {}
        assert self.game.trender
        assert isinstance(self.game.trender, TrendReq)

    def test_start_round(self):
        self.game.start_round()
        assert self.game.question
        assert isinstance(self.game.question, str)

    def test_start_round_fail(self):
        self.game.start_round()
        with pytest.raises(InvalidGameStateError):
            self.game.start_round()

    def test_add_word(self):
        self.game.start_round()
        # TODO: make mock player?
        self.game.add_word("doot", "player")
        assert self.game.words
        assert isinstance(self.game.words, dict)
        assert self.game.words["player"]
        assert isinstance(self.game.words["player"], str)

    def test_end_round(self):
        self.game.start_round()
        self.game.add_word("example", "player_1")
        results = self.game.end_round()
        assert results

    def test_end_round_fail(self):
        with pytest.raises(InvalidGameStateError):
            self.game.end_round()


def test_get_google_trends_url():
    url = get_google_trends_url(["example", "words"])
    assert url == "https://trends.google.com/trends/explore?q=example,words"