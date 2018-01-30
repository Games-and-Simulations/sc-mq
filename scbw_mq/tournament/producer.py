import logging
import os
from argparse import Namespace
from random import choice
from typing import Iterable

import pika
from pika import PlainCredentials
from pika.adapters.blocking_connection import BlockingChannel
from scbw.bot_factory import retrieve_bots
from scbw.bot_storage import LocalBotStorage, SscaitBotStorage
from scbw.map import download_sscait_maps, check_map_exists

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
    test_bot: str
    repeat_games: int

    bot_dir: str
    map_dir: str
    result_dir: str


def publish_all_vs_all(channel: BlockingChannel, repeat_games: int,
                       bots: Iterable[str], maps: Iterable[str]) -> int:
    n = 0
    for _ in range(repeat_games):
        for i, bot_a in enumerate(bots):
            for bot_b in bots[(i + 1):]:
                for map_name in maps:
                    game_name = "".join(choice("0123456789ABCDEF")
                                        for _ in range(8)) + "_%06d" % n
                    msg = PlayMessage([bot_a, bot_b], map_name, game_name).serialize()
                    channel.basic_publish(exchange='', routing_key='play', body=msg)

                    n += 1
    logger.info(f"published {n} messages")


def publish_one_vs_all(channel: BlockingChannel, one_bot: str,
                       repeat_games: int, bots: Iterable[str], maps: Iterable[str]) -> int:
    n = 0
    for _ in range(repeat_games):
        for other_bot in bots:
            for map_name in maps:
                game_name = "".join(choice("0123456789ABCDEF")
                                    for _ in range(8)) + "_%06d" % n
                msg = PlayMessage([one_bot, other_bot], map_name, game_name).serialize()
                channel.basic_publish(exchange='', routing_key='play', body=msg)

                n += 1
    return n


def launch_producer(args: ProducerConfig) -> int:
    bots = read_lines(args.bot_file)
    maps = read_lines(args.map_file)

    if args.test_bot:
        bots.append(args.test_bot)

    # make sure to download bots and maps before producing messages
    bot_storages = (LocalBotStorage(args.bot_dir), SscaitBotStorage(args.bot_dir))
    download_sscait_maps(args.map_dir)
    retrieve_bots(bots, bot_storages)
    for map in maps:
        check_map_exists(args.map_dir + "/" + map)
    os.makedirs(args.result_dir, exist_ok=True)

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
