import logging
import shutil
import sys
import time
from argparse import Namespace
from os.path import exists, basename, dirname
from typing import Optional

import pandas as pd
import pika
from pika import PlainCredentials
from scbw.player import check_bot_exists
from tqdm import tqdm

from .factory import retrieve_benchmark
from .plots import plot_overall_results, plot_bot_results
from .stats import process_results, calc_stats, save_stats
from .storage import BenchmarkException, RerunningBenchmarkException
from .storage import SscaitBenchmarkStorage
from ..producer import ProducerConfig
from ..producer import launch_producer

logger = logging.getLogger(__name__)


class BenchmarkConfig(Namespace):
    # rabbit connection
    host: str
    port: int
    user: str
    password: str

    benchmark: str
    base_dir: str
    test_bot_dir: Optional[str]


def get_queued_cnt(channel):
    declare_ok = channel.queue_declare(queue="play", passive=True)
    return declare_ok.method.message_count


def wait_until_benchmark_finished(args: BenchmarkConfig, total_messages: int):
    connection = pika.BlockingConnection(pika.ConnectionParameters(
        host=args.host,
        port=args.port,
        connection_attempts=5,
        retry_delay=3,
        credentials=PlainCredentials(args.user, args.password)
    ))

    try:
        channel = connection.channel()

        logger.info("Please wait until all games are finished.")
        logger.info("Don't forget to launch tournament consumers.")
        logger.info("This can take several hours, please be patient.")

        bar = tqdm(total=total_messages, unit="game")
        last_messages = total_messages

        while last_messages != 0:
            current_messages = get_queued_cnt(channel)
            bar.update(last_messages - current_messages)
            last_messages = current_messages
            time.sleep(5)

        bar.close()

    finally:
        connection.close()


def launch_benchmark(args: BenchmarkConfig):
    # you can add custom benchmark storages here
    benchmark_storages = (SscaitBenchmarkStorage(args.base_dir),)
    benchmark = retrieve_benchmark(args.benchmark, benchmark_storages)

    test_bot = None
    test_bot_dir = None
    if args.test_bot_dir is not None:
        test_bot, test_bot_dir = basename(args.test_bot_dir), dirname(args.test_bot_dir)

    if not benchmark.has_results():
        if test_bot is not None:
            # test bot checks
            check_bot_exists(test_bot, test_bot_dir)
            if exists(f"{benchmark.bot_dir}/{test_bot}"):
                raise BenchmarkException(
                    f"Bot '{test_bot}' is listed in benchmark bots in '{benchmark.bot_dir}'")

            shutil.copytree(args.test_bot_dir, f"{benchmark.bot_dir}/{test_bot}")

        producer_args = ProducerConfig(
            host=args.host,
            port=args.port,
            user=args.user,
            password=args.password,

            bot_file=benchmark.bot_file,
            map_file=benchmark.map_file,
            test_bot=test_bot,
            repeat_games=benchmark.repeat_games,

            bot_dir=benchmark.bot_dir,
            map_dir=benchmark.map_dir,
            result_dir=benchmark.result_dir
        )

        # create all producer messages
        total_messages = launch_producer(producer_args)
        wait_until_benchmark_finished(args, total_messages)

    else:
        logger.warning(f"Results directory {benchmark.result_dir} is not empty.")
        logger.warning(f"Please truncate it's contents to prevent overwriting results.")
        logger.warning(f"Will not launch benchmarking, but can process results.")
        logger.info("Would you like to continue to process results? [Y/n]")
        ans = input()
        if not (ans == "y" or ans == "Y" or ans == ""):
            logger.warning("Aborting.")
            sys.exit(1)

    logger.info("Processing results...")
    df_results = process_results(benchmark.result_dir)

    logger.info("Calculating stats")
    ser_elos = None
    if exists(benchmark.elo_file):
        ser_elos = pd.read_csv(benchmark.elo_file, names=["bot", "rating"],
                               index_col="bot", squeeze=True)

    df_rr_winrate, \
    ser_overall_winrate, \
    df_gametimes, \
    df_race_wintimes, \
    df_botrace_winrate, \
    ser_maps, \
    ser_bot_races, \
    ser_elos = calc_stats(df_results, ser_elos)

    logger.info("Creating plots and saving stats")
    if test_bot is None:
        plot_overall_results(ser_overall_winrate, df_race_wintimes, df_gametimes,
                             ser_bot_races, ser_maps, ser_elos)
    else:
        plot_bot_results(test_bot, df_rr_winrate, ser_overall_winrate, df_botrace_winrate,
                         ser_maps, ser_elos)