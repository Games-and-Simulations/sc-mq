import argparse
import logging

import coloredlogs
from pika import ConnectionParameters
from pika.credentials import PlainCredentials

from .cli import (
    RABBITMQ_HOST,
    RABBITMQ_PORT,
    RABBITMQ_USER,
    RABBITMQ_PASSWORD,
    RABBITMQ_QUEUE
)
from ..rabbitmq_consumer import AckConsumer

logger = logging.getLogger(__name__)


class DumpConfig(argparse.Namespace):
    host: str
    port: int
    user: str
    password: str
    queue: str


class Dumper(AckConsumer):
    EXCHANGE = 'play'
    EXCHANGE_TYPE = 'direct'
    QUEUE = 'play'
    ROUTING_KEY = 'play'

    def __init__(self, config: DumpConfig):
        self.EXCHANGE = config.queue
        self.QUEUE = config.queue
        self.ROUTING_KEY = config.queue

        super(Dumper, self).__init__(ConnectionParameters(
            host=config.host,
            port=config.port,
            credentials=PlainCredentials(config.user, config.password),

            connection_attempts=3,
            heartbeat_interval=60,
        ))

    def handle_message(self, msg: str):
        print(msg)


def launch_dumper(args: DumpConfig):
    # setup services
    consumer = Dumper(args)
    try:
        consumer.connect()
        consumer.start_consuming()
    except KeyboardInterrupt:
        logger.warning("Shutting down worker")
        consumer.stop_consuming()
    finally:
        consumer.close()


dumper_parser = argparse.ArgumentParser(
    description='Print messages to stdout from given queue. This consumes the messages.',
    formatter_class=argparse.RawTextHelpFormatter)

dumper_parser.add_argument('--host', type=str, help="RabbitMQ host", default=RABBITMQ_HOST)
dumper_parser.add_argument('--port', type=int, help="RabbitMQ port", default=RABBITMQ_PORT)
dumper_parser.add_argument('--user', type=str, help="RabbitMQ user", default=RABBITMQ_USER)
dumper_parser.add_argument('--password', type=str, help="RabbitMQ password",
                           default=RABBITMQ_PASSWORD)
dumper_parser.add_argument('--queue', type=str, help="RabbitMQ queue",
                           default=RABBITMQ_QUEUE)


def dumper():
    args = dumper_parser.parse_args()
    coloredlogs.install(level='DEBUG', fmt="%(levelname)s %(name)s[%(process)d] %(message)s")
    launch_dumper(args)


if __name__ == '__main__':
    dumper()
