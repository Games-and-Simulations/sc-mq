import argparse
from os.path import dirname, abspath

import coloredlogs
from scbw.cli import SC_BOT_DIR, SCBW_BASE_DIR, SC_LOG_DIR, SC_MAP_DIR, SC_BWAPI_DATA_BWTA_DIR, SC_BWAPI_DATA_BWTA2_DIR

from .consumer import launch_consumer
from .producer import launch_producer

SC_RESULT_DIR = f"{SCBW_BASE_DIR}/results"
SC_STORAGE_DIR = f"{SCBW_BASE_DIR}/storage"
SC_PARSER_DIR = f"{SCBW_BASE_DIR}/parser"

producer_parser = argparse.ArgumentParser(
    description='Launch parser client that uses RabbitMQ specification to parse a replay',
    formatter_class=argparse.RawTextHelpFormatter)

# Rabbit connection
producer_parser.add_argument('--host', type=str, required=True, help="RabbitMQ host")
producer_parser.add_argument('--port', type=int, required=True, help="RabbitMQ port")
producer_parser.add_argument('--user', type=str, required=True, help="RabbitMQ user")
producer_parser.add_argument('--password', type=str, required=True, help="RabbitMQ password")

# Input data
here = dirname(abspath(__file__))
producer_parser.add_argument('--replay_file', type=str, default=f"{here}/REPLAYS",
                             help="File with newline separated list of bots")
producer_parser.add_argument('--replay_dir', type=str, default=SC_BOT_DIR,
                             help=f"Directory where bots are stored, default:\n{SC_BOT_DIR}")
producer_parser.add_argument('--log_level', type=str, default="INFO",
                             choices=['DEBUG', 'INFO', 'WARN', 'ERROR'],
                             help="Logging level.")


def producer():
    args = producer_parser.parse_args()
    coloredlogs.install(level=args.log_level, fmt="%(levelname)s %(name)s[%(process)d] %(message)s")
    launch_producer(args)


consumer_parser = argparse.ArgumentParser(
    description='Launch parser client that uses RabbitMQ specification to parse a replay',
    formatter_class=argparse.RawTextHelpFormatter)

# Rabbit connection
consumer_parser.add_argument('--host', type=str, help="RabbitMQ host", default="localhost")
consumer_parser.add_argument('--port', type=int, help="RabbitMQ port", default=5672)
consumer_parser.add_argument('--user', type=str, help="RabbitMQ user", default="starcraft")
consumer_parser.add_argument('--password', type=str, help="RabbitMQ password", default="starcraft")

# Parallelization
consumer_parser.add_argument('--n_processes', type=int, default=4)

# Results
consumer_parser.add_argument('--storage_dir', type=str, default=SC_STORAGE_DIR,
                             help=f"Directory where features results are stored, default:\n{SC_STORAGE_DIR}")
consumer_parser.add_argument('--parser_dir', type=str, default=SC_PARSER_DIR,
                             help=f"Directory where parser binaries are stored, default:\n{SC_PARSER_DIR}")

# Game settings
consumer_parser.add_argument("--timeout", type=int, default=600,
                             help="Kill docker container after timeout seconds.\n"
                                  "If not set, run without timeout.")

# Volumes
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
consumer_parser.add_argument('--opt', type=str, default="",
                             help="Specify custom docker run options")

consumer_parser.add_argument('--log_level', type=str, default="INFO",
                             choices=['DEBUG', 'INFO', 'WARN', 'ERROR'],
                             help="Logging level.")


def consumer():
    args = consumer_parser.parse_args()
    coloredlogs.install(level=args.log_level, fmt="%(levelname)s %(name)s[%(process)d] %(message)s")
    launch_consumer(args)
