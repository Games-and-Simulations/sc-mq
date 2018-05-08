import logging
import os
from argparse import Namespace
from random import choice, shuffle
from typing import Iterable, Optional

import pika
from pika import PlainCredentials
from pika.adapters.blocking_connection import BlockingChannel
from scbw.bot_factory import retrieve_bots
from scbw.bot_storage import LocalBotStorage, SscaitBotStorage
from scbw.map import check_map_exists

from .message import PlayMessage
from ..utils import read_lines

logger = logging.getLogger(__name__)


class ProducerConfig(Namespace):
    # rabbit connection
    host: str
    port: int
    user: str
    password: str

    bot_file: str
    map_file: str
    test_bot: Optional[str]
    repeat_games: int

    bot_dir: str
    map_dir: str
    game_dir: str


def publish_all_vs_all(channel: BlockingChannel, repeat_games: int,
                       bots: Iterable[str], maps: Iterable[str]) -> int:

    # randomize order of bots playing against each other
    bot_combinations = []
    j = 0
    for i, bot_a in enumerate(bots):
        for bot_b in bots[(i + 1):]:
            bot_combinations.append((bot_a, bot_b, j))
            j += 1
    shuffle(bot_combinations)

    n = 0
    for _ in range(repeat_games):
        for map_name in maps:
            for bot_a, bot_b, j in bot_combinations:
                game_name = "%06d" % (n+j)
                msg = PlayMessage([bot_a, bot_b], map_name, game_name).serialize()
                publish_msg(channel, msg)

            n += len(bot_combinations)
    return n


def publish_one_vs_all(channel: BlockingChannel, one_bot: str,
                       repeat_games: int, bots: Iterable[str], maps: Iterable[str]) -> int:
    n = 0
    for _ in range(repeat_games):
        for other_bot in bots:
            for map_name in maps:
                game_name = "".join(choice("0123456789ABCDEF")
                                    for _ in range(8)) + "_%06d" % n
                msg = PlayMessage([one_bot, other_bot], map_name, game_name).serialize()
                publish_msg(channel, msg)

                n += 1
    return n


def publish_msg(channel, msg):
    channel.basic_publish(
        exchange='',
        routing_key='play',
        body=msg,
        properties=pika.BasicProperties(
            delivery_mode=2,  # make message persistent
        ))


def launch_producer(args: ProducerConfig) -> int:
    bots = read_lines(args.bot_file)
    maps = read_lines(args.map_file)

    if args.test_bot:
        bots.append(args.test_bot)

    # make sure to bots and maps are available before producing messages
    bot_storages = (LocalBotStorage(args.bot_dir), SscaitBotStorage(args.bot_dir))
    retrieve_bots(bots, bot_storages)
    for map in maps:
        check_map_exists(args.map_dir + "/" + map)
    os.makedirs(args.game_dir, exist_ok=True)

    if len(os.listdir(args.game_dir)) != 0:
        raise Exception(f"Result dir '{args.game_dir}' is not empty!"
                        "Please empty the dir or use different result dir as destination.")

    connection = pika.BlockingConnection(pika.ConnectionParameters(
        host=args.host,
        port=args.port,
        connection_attempts=5,
        retry_delay=3,
        credentials=PlainCredentials(args.user, args.password)
    ))

    try:
        channel = connection.channel()

        if args.test_bot is not None:
            n = publish_one_vs_all(channel, args.test_bot, args.repeat_games, bots, maps)
        else:
            n = publish_all_vs_all(channel, args.repeat_games, bots, maps)

        return n

    finally:
        connection.close()
