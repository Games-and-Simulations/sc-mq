import logging
import time
from argparse import Namespace
from multiprocessing import Process
from subprocess import Popen
from typing import Callable

from pika import ConnectionParameters
from pika.credentials import PlainCredentials
from scbw.docker import APP_DIR, LOG_DIR, MAP_DIR, BWAPI_DATA_BWTA_DIR, BWAPI_DATA_BWTA2_DIR, xoscmounts

from .message import ParseMessage
from ..rabbitmq_consumer import AckConsumer
from ..rabbitmq_consumer import consumer_error

logger = logging.getLogger(__name__)


class ParseException(Exception):
    pass


class ConsumerConfig(Namespace):
    # rabbit connection
    host: str
    port: int
    user: str
    password: str

    # parallelization
    n_processes: int

    # results
    storage_dir: str
    parser_dir: str

    # other settings
    timeout: int
    log_dir: str
    map_dir: str
    bwapi_data_bwta_dir: str
    bwapi_data_bwta2_dir: str
    docker_image: str
    opt: str


PARSER_DIR = f"{APP_DIR}/bin"
STORAGE_DIR = f"{APP_DIR}/storage"


def parse_replay(replay_file: str, config: ConsumerConfig, wait_callback: Callable) -> int:
    cmd = ["docker", "run",
           "--privileged",
           "--name", f"PARSE_{replay_file}",
           "--volume", f"{xoscmounts(config.parser_dir)}:{PARSER_DIR}:ro",
           "--volume", f"{xoscmounts(config.storage_dir)}:{STORAGE_DIR}:rw",
           "--volume", f"{xoscmounts(config.log_dir)}:{LOG_DIR}:rw",
           "--volume", f"{xoscmounts(config.map_dir)}:{MAP_DIR}:rw",
           "--volume", f"{xoscmounts(config.bwapi_data_bwta_dir)}:{BWAPI_DATA_BWTA_DIR}:rw",
           "--volume", f"{xoscmounts(config.bwapi_data_bwta2_dir)}:{BWAPI_DATA_BWTA2_DIR}:rw",

           "starcraft:replay-parser", "/app/replay_entrypoint.sh",
           replay_file,
           str(config.timeout)]

    p = Popen(cmd)
    while True:
        ret_code = p.poll()
        wait_callback()
        if ret_code is not None:
            if ret_code != 0:
                raise ParseException(f"exit code is not 0 but {ret_code}")
            break
        time.sleep(3)


class ParseConsumer(AckConsumer):
    EXCHANGE = 'parse'
    EXCHANGE_TYPE = 'direct'
    QUEUE = 'parse'
    ROUTING_KEY = 'parse'

    def __init__(self, config: ConsumerConfig):
        super(ParseConsumer, self).__init__(ConnectionParameters(
            host=config.host,
            port=config.port,
            credentials=PlainCredentials(config.user, config.password),

            connection_attempts=3,
            heartbeat_interval=20,
        ))
        self.config = config

    @consumer_error(ParseException)
    def handle_message(self, request: str):
        play = ParseMessage.deserialize(request)
        parse_replay(play.map, self.config, wait_callback=self.wait_callback)

    def wait_callback(self):
        self._connection.process_data_events()


def launch_consumer(args: ConsumerConfig):
    def run() -> None:
        logger.info("Initializing a new worker")

        # setup services
        consumer = ParseConsumer(args)
        try:
            consumer.connect()
            consumer.start_consuming()
        except KeyboardInterrupt:
            logger.warning("Shutting down worker")
            consumer.stop_consuming()
        finally:
            consumer.close()

    for i in range(args.n_processes):
        p = Process(target=run)
        p.start()
