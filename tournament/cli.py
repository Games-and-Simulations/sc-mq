import argparse
import logging
from os.path import abspath, dirname

import coloredlogs
from scbw.cli import SC_BOT_DIR, SC_LOG_DIR, SC_MAP_DIR, SC_BWAPI_DATA_BWTA_DIR, \
    SC_BWAPI_DATA_BWTA2_DIR, SC_IMAGE, SCBW_BASE_DIR
from scbw.game_type import GameType

from .consumer import launch_consumer
from .producer import launch_producer

logger = logging.getLogger(__name__)

SC_RESULT_DIR = f"{SCBW_BASE_DIR}/results"

consumer_parser = argparse.ArgumentParser(
    description='Launch tournament client that uses RabbitMQ specification to launch a game',
    formatter_class=argparse.RawTextHelpFormatter)

# Rabbit connection
consumer_parser.add_argument('--host', type=str, help="RabbitMQ host", default="localhost")
consumer_parser.add_argument('--port', type=int, help="RabbitMQ port", default=5672)
consumer_parser.add_argument('--user', type=str, help="RabbitMQ user", default="starcraft")
consumer_parser.add_argument('--password', type=str, help="RabbitMQ password", default="starcraft")

# Parallelization
consumer_parser.add_argument('--n_processes', type=int, default=4)

# Results
consumer_parser.add_argument('--result_dir', type=str, default=SC_RESULT_DIR,
                             help=f"Directory where results are stored, default:\n{SC_RESULT_DIR}")

# Game settings
consumer_parser.add_argument("--game_type", type=str, metavar="GAME_TYPE",
                             default=GameType.FREE_FOR_ALL.value,
                             choices=[game_type.value for game_type in GameType],
                             help="Set game type. It can be one of:\n- " +
                                  "\n- ".join([game_type.value for game_type in GameType]))
consumer_parser.add_argument("--game_speed", type=int, default=0,
                             help="Set game speed (pause of ms between frames),\n"
                                  "use -1 for game default.")
consumer_parser.add_argument("--timeout", type=int, default=600,
                             help="Kill docker container after timeout seconds.\n"
                                  "If not set, run without timeout.")

# Volumes
consumer_parser.add_argument('--bot_dir', type=str, default=SC_BOT_DIR,
                             help=f"Directory where bots are stored, default:\n{SC_BOT_DIR}")
consumer_parser.add_argument('--log_dir', type=str, default=SC_LOG_DIR,
                             help=f"Directory where logs are stored, default:\n{SC_LOG_DIR}")
consumer_parser.add_argument('--map_dir', type=str, default=SC_MAP_DIR,
                             help=f"Directory where maps are stored, default:\n{SC_MAP_DIR}")

#  BWAPI data volumes
consumer_parser.add_argument('--bwapi_data_bwta_dir', type=str, default=SC_BWAPI_DATA_BWTA_DIR,
                             help=f"Directory where BWTA map caches are stored, "
                                  f"default:\n{SC_BWAPI_DATA_BWTA_DIR}")
consumer_parser.add_argument('--bwapi_data_bwta2_dir', type=str, default=SC_BWAPI_DATA_BWTA2_DIR,
                             help=f"Directory where BWTA2 map caches are stored, "
                                  f"default:\n{SC_BWAPI_DATA_BWTA2_DIR}")

# Settings
consumer_parser.add_argument('--read_overwrite', action="store_true",
                             help="At the end of each game, copy the contents\n"
                                  "of 'write' directory to the read directory\n"
                                  "of the bot.\n"
                                  "Needs to be explicitly turned on.")
consumer_parser.add_argument('--docker_image', type=str, default=SC_IMAGE,
                             help="The name of the image that should \n"
                                  "be used to launch the game.\n"
                                  "This helps with local development.")
consumer_parser.add_argument('--opt', type=str, default="",
                             help="Specify custom docker run options")

consumer_parser.add_argument('--log_level', type=str, default="INFO",
                             choices=['DEBUG', 'INFO', 'WARN', 'ERROR'],
                             help="Logging level.")


def consumer():
    args = consumer_parser.parse_args()
    coloredlogs.install(level=args.log_level, fmt="%(levelname)s %(name)s[%(process)d] %(message)s")
    launch_consumer(args)


producer_parser = argparse.ArgumentParser(
    description='Launch tournament client that uses RabbitMQ specification to launch a game',
    formatter_class=argparse.RawTextHelpFormatter)

# Rabbit connection
producer_parser.add_argument('--host', type=str, required=True, help="RabbitMQ host")
producer_parser.add_argument('--port', type=int, required=True, help="RabbitMQ port")
producer_parser.add_argument('--user', type=str, required=True, help="RabbitMQ user")
producer_parser.add_argument('--password', type=str, required=True, help="RabbitMQ password")

# Input data
here = dirname(abspath(__file__))
producer_parser.add_argument('--bot_file', type=str, default=f"{here}/BOTS_SSCAIT_2017",
                             help="File with newline separated list of bots")
producer_parser.add_argument('--map_file', type=str, default=f"{here}/SSCAIT_MAPS",
                             help="File with newline separated list of maps")
producer_parser.add_argument('--bot_dir', type=str, default=SC_BOT_DIR,
                             help=f"Directory where bots are stored, default:\n{SC_BOT_DIR}")
producer_parser.add_argument('--map_dir', type=str, default=SC_MAP_DIR,
                             help=f"Directory where maps are stored, default:\n{SC_MAP_DIR}")
# Results
producer_parser.add_argument('--result_dir', type=str, default=SC_RESULT_DIR,
                             help=f"Directory where results are stored, default:\n{SC_RESULT_DIR}")

producer_parser.add_argument('--log_level', type=str, default="INFO",
                             choices=['DEBUG', 'INFO', 'WARN', 'ERROR'],
                             help="Logging level.")


def producer():
    args = producer_parser.parse_args()
    coloredlogs.install(level=args.log_level, fmt="%(levelname)s %(name)s[%(process)d] %(message)s")
    launch_producer(args)
