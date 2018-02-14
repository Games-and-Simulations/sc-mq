import logging
from argparse import Namespace
from typing import List

import pika
from pika import PlainCredentials
from scbw.map import check_map_exists
from ..utils import read_lines

logger = logging.getLogger(__name__)


class ProducerConfig(Namespace):
    # rabbit connection
    host: str
    port: int
    user: str
    password: str

    replay_file: str
    replay_dir: str
    log_level: str


def launch_producer(args: ProducerConfig):
    replays = read_lines(args.replay_file)
    for replay_file in replays:
        check_map_exists(args.replay_dir + "/" + replay_file)

    connection = pika.BlockingConnection(pika.ConnectionParameters(
        host=args.host,
        port=args.port,
        connection_attempts=5,
        retry_delay=3,
        credentials=PlainCredentials(args.user, args.password)
    ))

    try:
        channel = connection.channel()

        logger.info(f"publishing {len(replays)} messages")
        for replay in replays:
            channel.basic_publish(
                exchange='',
                routing_key='parse',
                body=replay,
                properties=pika.BasicProperties(
                    delivery_mode=2,  # make message persistent
                ))

    finally:
        connection.close()
