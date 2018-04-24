#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Main script entry point for the trendmaster Discord bot"""

import argparse
import sys

import logging
import logging.handlers

from trendmaster.bot import BOT


def main():
    """Startup script for the trendmaster Discord bot"""
    parser = argparse.ArgumentParser()

    group = parser.add_argument_group(title="Token config")
    group = group.add_mutually_exclusive_group(required=True)
    group.add_argument("-t", "--token",
                       help="String of the Discord token.txt for the bot")
    group.add_argument("-tf", "--token-file", dest="token_file",
                       help="Path to file containing the Discord token.txt "
                            "for the bot")

    group = parser.add_argument_group(title="Logging config")
    group.add_argument("-v", "--verbose", action="store_true",
                       help="Enable verbose logging")
    group.add_argument("-f", "--log-dir", dest="logdir",
                       help="Enable time rotating file logging at "
                            "the path specified")
    group.add_argument("-d", "--debug", action="store_true",
                       help="Enable DEBUG logging level")

    args = parser.parse_args()

    # initialize logging
    handlers = list()
    if args.logdir is not None:
        handlers.append(
            logging.handlers.TimedRotatingFileHandler(
                args.logdir,
                when="D",
                interval=1,
                backupCount=45
            )
        )

    if args.verbose:
        handlers.append(logging.StreamHandler())
    if args.debug:
        level = logging.DEBUG
    else:
        level = logging.INFO

    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=handlers,
    )

    # read the token.txt file and extract the token.txt
    if args.token_file is not None:
        with open(args.token_file, "r") as token_file:
            token = str(token_file.read()).strip()
    elif args.token is not None:
        token = args.token

    # run the bot
    BOT.run(token)

    return 0


if __name__ == "__main__":
    sys.exit(main())
