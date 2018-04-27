#!/usr/bin/python
# -*- coding: utf-8 -*-

"""pytests for trends.py"""

import pytest

from trendmaster.trends import GoogleTrendsGame, InvalidGameStateError,\
    get_google_trends_url, Position

from pytrends.request import TrendReq


class TestGoogleTrendsGame:
    """Class for testing GoogleTrendsGame"""

    def setup_method(self):
        """Create a new instance of GoogleTrendsGame to test"""
        self.game = GoogleTrendsGame()

        assert self.game
        assert isinstance(self.game, GoogleTrendsGame)

        assert self.game.question is None

        assert self.game.words == {}
        assert self.game.scores == {}

        assert self.game.trender
        assert isinstance(self.game.trender, TrendReq)

    def test_start_round(self):
        """Test GoogleTrendsGame.start_round()"""
        self.game.start_round()

        assert self.game.question
        assert isinstance(self.game.question, str)

    def test_start_round_fail(self):
        """Test executing GoogleTrendsGame.start_round() twice

        should raise an InvalidGameStateError
        """
        self.game.start_round()

        with pytest.raises(InvalidGameStateError):
            self.game.start_round()

    def test_add_word_def(self):
        """Test GoogleTrendsGame.add_word()"""
        self.game.start_round()
        # TODO: make mock player?
        self.game.add_word("example", "player")

        assert self.game.words
        assert isinstance(self.game.words, dict)

        assert self.game.words["player"]
        assert isinstance(self.game.words["player"], str)
        assert "{} {}".format("example", self.game.question) == self.game.words["player"]

    def test_add_word_front(self):
        """Test GoogleTrendsGame.add_word()"""
        self.game.start_round()
        # TODO: make mock player?
        self.game.add_word("example", "player", Position.front)

        assert self.game.words
        assert isinstance(self.game.words, dict)

        assert self.game.words["player"]
        assert isinstance(self.game.words["player"], str)
        assert "{} {}".format("example", self.game.question) == self.game.words["player"]

    def test_add_word_back(self):
        """Test GoogleTrendsGame.add_word()"""
        self.game.start_round()
        # TODO: make mock player?
        self.game.add_word("example", "player", Position.back)

        assert self.game.words
        assert isinstance(self.game.words, dict)

        assert self.game.words["player"]
        assert isinstance(self.game.words["player"], str)
        assert "{} {}".format(self.game.question, "example") == self.game.words["player"]

    def test_end_round(self):
        """Test GoogleTrendsGame.end_round()"""
        self.game.start_round()
        self.game.add_word("example", "player_1")

        results = self.game.end_round()
        assert results
        assert isinstance(results, dict)

    def test_end_round_fail(self):
        """Test GoogleTrendsGame.end_round() with no round actually started

        should raise an InvalidGameStateError
        """
        with pytest.raises(InvalidGameStateError):
            self.game.end_round()


def test_get_google_trends_url():
    """Test get_google_trends_url"""
    url = get_google_trends_url(["example", "words"])
    assert url == "https://trends.google.com/trends/explore?q=example,words"