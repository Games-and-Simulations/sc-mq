import logging
import os
from argparse import Namespace
from copy import copy
from multiprocessing import Process
from os.path import exists

from pika import ConnectionParameters
from pika.credentials import PlainCredentials
from scbw.error import DockerException, GameException
from scbw.game import run_game, GameArgs

from .message import PlayMessage
from .producer import publish_msg
from ..rabbitmq_consumer import AckConsumer
from ..rabbitmq_consumer import consumer_error

logger = logging.getLogger(__name__)


class ConsumerConfig(Namespace):
    # rabbit connection
    host: str
    port: int
    user: str
    password: str

    # parallelization
    n_processes: int

    # results
    result_dir: str

    # game settings
    game_type: str
    game_speed: int
    timeout: int
    bot_dir: str
    game_dir: str
    map_dir: str
    bwapi_data_bwta_dir: str
    bwapi_data_bwta2_dir: str
    read_overwrite: bool
    random_names: bool
    docker_image: str
    opt: str


class PlayConsumer(AckConsumer):
    EXCHANGE = 'play'
    EXCHANGE_TYPE = 'direct'
    QUEUE = 'play'
    ROUTING_KEY = 'play'

    def __init__(self, config: ConsumerConfig):
        super(PlayConsumer, self).__init__(ConnectionParameters(
            host=config.host,
            port=config.port,
            credentials=PlainCredentials(config.user, config.password),

            connection_attempts=3,
            heartbeat_interval=60,
        ))

        self.result_dir = config.result_dir

        self.game_args = GameArgs()
        self.game_args.game_type = config.game_type
        self.game_args.game_speed = config.game_speed
        self.game_args.timeout = config.timeout
        self.game_args.bot_dir = config.bot_dir
        self.game_args.game_dir = config.game_dir
        self.game_args.map_dir = config.map_dir
        self.game_args.bwapi_data_bwta_dir = config.bwapi_data_bwta_dir
        self.game_args.bwapi_data_bwta2_dir = config.bwapi_data_bwta2_dir
        self.game_args.read_overwrite = config.read_overwrite
        self.game_args.docker_image = config.docker_image
        self.game_args.random_names = config.random_names

        self.game_args.opt = config.opt

        self.game_args.human = False
        self.game_args.headless = True
        self.game_args.vnc_host = "localhost"
        self.game_args.vnc_base_port = 5900
        self.game_args.allow_input = False
        self.game_args.auto_launch = False
        self.game_args.plot_realtime = False
        self.game_args.hide_names = False
        self.game_args.capture_movement = False
        self.game_args.show_all = False

    @consumer_error(GameException, DockerException)
    def handle_message(self, json_request: str):
        self._connection.process_data_events()
        play = PlayMessage.deserialize(json_request)

        result_file = f"{self.result_dir}/{play.game_name}.json"
        if exists(result_file):
            logger.warning(f"Game {play.game_name} has already been played!")
            return

        game_args = copy(self.game_args)
        game_args.bots = play.bots
        game_args.map = play.map
        game_args.game_name = play.game_name

        # When read_overwrite is enabled, bots save what they've learned in the game,
        # thus there cannot be the same bots playing at the same time.
        # If such a game request happens, it will be appended to the end of the RMQ queue
        if self.game_args.read_overwrite:
            if self.bots_playing(game_args.bots):
                logger.info(f"Cannot play {game_args.bots} now, requeuing {json_request}")
                self.requeue_game(json_request)
                return

            try:
                self.reserve_bots(game_args.bots)
                run_game(game_args, wait_callback=self.wait_callback)
            finally:
                self.free_bots(game_args.bots)

        else:
            run_game(game_args, wait_callback=self.wait_callback)

        self._connection.process_data_events()

    def wait_callback(self):
        # This calls process_data_events under the hood
        self._connection.sleep(3)

    def reserve_bots(self, bots) -> None:
        for bot in bots:
            fname = f"playing_{bot}"
            with open(fname, 'a'):
                os.utime(fname, times=None)

    def free_bots(self, bots) -> None:
        for bot in bots:
            fname = f"playing_{bot}"
            try:
                os.remove(fname)
            except OSError:
                pass

    def bots_playing(self, bots) -> bool:
        return any(os.path.exists(f"playing_{bot}") for bot in bots)

    def requeue_game(self, json_request: str) -> None:
        publish_msg(self._channel, json_request)


def launch_consumer(args: ConsumerConfig):
    def run() -> None:
        logger.info("Initializing a new worker")

        # setup services
        consumer = PlayConsumer(args)
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
