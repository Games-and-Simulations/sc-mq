import json
import logging
from argparse import Namespace
from copy import copy
from multiprocessing import Process

from scbw import DockerException, GameException, run_game, GameArgs

from .message import PlayMessage
from .rabbitmq_consumer import AckConsumer
from .rabbitmq_consumer import consumer_error

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
    log_dir: str
    map_dir: str
    bwapi_data_bwta_dir: str
    bwapi_data_bwta2_dir: str
    read_overwrite: bool
    docker_image: str
    opt: str


class PlayConsumer(AckConsumer):
    EXCHANGE = 'play'
    EXCHANGE_TYPE = 'direct'
    QUEUE = 'play'
    ROUTING_KEY = 'play'

    def __init__(self, config: ConsumerConfig):
        url = f'amqp://{config.user}:{config.password}@{config.host}:{config.port}/%2F'
        super(PlayConsumer, self).__init__(url)

        self.result_dir = config.result_dir

        self.game_args = GameArgs()
        self.game_args.game_type = config.game_type
        self.game_args.game_speed = config.game_speed
        self.game_args.timeout = config.timeout
        self.game_args.bot_dir = config.bot_dir
        self.game_args.log_dir = config.log_dir
        self.game_args.map_dir = config.map_dir
        self.game_args.bwapi_data_bwta_dir = config.bwapi_data_bwta_dir
        self.game_args.bwapi_data_bwta2_dir = config.bwapi_data_bwta2_dir
        self.game_args.read_overwrite = config.read_overwrite
        self.game_args.docker_image = config.docker_image

        self.game_args.opt = config.opt + (" " if config.opt else "") + "--rm"

        self.game_args.human = False
        self.game_args.headless = True
        self.game_args.vnc_base_port = 5900
        self.game_args.show_all = False
        self.game_args.disable_checks = True

    @consumer_error(GameException, DockerException)
    def handle_message(self, json_request: str):
        play = PlayMessage.deserialize(json_request)

        game_args = copy(self.game_args)
        game_args.bots = play.bots
        game_args.map = play.map
        game_args.game_name = play.game_name

        game_result = run_game(game_args)

        info = dict(
            bots=game_args.bots,
            map=game_args.map,
            game_name=game_args.game_name,
            game_type=game_args.game_type,
            game_speed=game_args.game_speed,
            timeout=game_args.timeout,
            read_overwrite=game_args.read_overwrite,
            game_time=game_result.game_time,
            winner_player=game_result.winner_player,
            replay_files=game_result.replay_files,
            log_files=game_result.log_files,
        )
        logger.debug(info)
        with open(f"{self.result_dir}/{play.game_name}.json", "w") as f:
            json.dump(info, f)

        logger.info(f"game {game_args.game_name} finished")


def launch_consumer(args: ConsumerConfig):
    def run() -> None:
        logger.info("Initializing a new worker")

        # setup services
        consumer = PlayConsumer(args)
        try:
            consumer.run()
        except KeyboardInterrupt:
            logger.info("Shutting down worker")
            consumer.stop()

    for i in range(args.n_processes):
        p = Process(target=run)
        p.start()
