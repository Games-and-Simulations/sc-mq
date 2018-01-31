import csv
import glob
import json
import logging
import time
from pprint import pprint

import elo
import numpy as np
import pandas as pd
import pika
from pika import PlainCredentials
from tqdm import tqdm

from .producer import ProducerConfig, launch_producer

logger = logging.getLogger(__name__)


def get_queued_cnt(channel):
    declare_ok = channel.queue_declare(queue="play", passive=True)
    return declare_ok.method.message_count


def process_results(result_dir: str):
    rows = {"game_name": [],
            "map": [],
            "winner": [],
            "loser": [],
            "read_overwrite": [],
            "game_time": []}

    logger.info("Processing results...")
    for file in tqdm(glob.glob(f"{result_dir}/*.json")):
        if "failed" in file:
            continue

        with open(file, "r") as f:
            info = json.load(f)

        if info['winner_player'] == 0:
            winner = info["bots"][0]
            loser = info["bots"][1]
        else:
            winner = info["bots"][1]
            loser = info["bots"][0]

        rows["game_name"].append(info["game_name"])
        rows["map"].append(info["map"])
        rows["winner"].append(winner)
        rows["loser"].append(loser)
        rows["read_overwrite"].append(info["read_overwrite"])
        rows["game_time"].append(info["game_time"])

    return pd.DataFrame(rows).set_index("game_name")


def calc_stats(df):
    logger.info("Calculating stats")
    df['one'] = 1

    df_winrate = pd.pivot_table(df, index='winner', columns='loser',
                                values='one', aggfunc=np.sum) \
        .fillna(0).sort_index()

    df_gametimes = pd.pivot_table(df, index='winner', columns='loser',
                              values='game_time', aggfunc=np.mean) \
        .fillna(0).sort_index()



    return df_winrate, df_gametimes


def save_stats(df_winrate, df_times):
    logger.info("Saving stats")
    df_winrate.to_csv("results_winrate.csv", quoting=csv.QUOTE_MINIMAL, sep="\t")
    df_times.to_csv("results_times.csv", quoting=csv.QUOTE_MINIMAL, sep="\t")


def calc_elo(df):
    elo.WIN = 1.  #: The actual score for win.
    elo.DRAW = 0.5  #: The actual score for draw.
    elo.LOSS = 0.  #: The actual score for loss.
    K_FACTOR = 10  # 20  #: Default K-factor.
    INITIAL = 1200  # 2000  #: Default initial rating.
    BETA = 200  # 200  #: Default Beta value.

    bots = set(df['winner']).union((set(df['loser'])))
    ratings = {bot: elo.CountedRating(INITIAL) for bot in bots}

    elo_calc = elo.Elo(
        k_factor=K_FACTOR,
        initial=INITIAL,
        beta=BETA,
        rating_class=elo.CountedRating)

    rng = np.arange(df.shape[0])
    perm = np.random.permutation(rng)
    for j in perm:
        winner = df.iloc[j]['winner']
        loser = df.iloc[j]['loser']

        winner_elo, loser_elo = elo_calc.rate_1vs1(
            ratings[winner], ratings[loser], drawn=False)

        ratings[winner] = winner_elo
        ratings[loser] = loser_elo

    rating_tuples = [(bot, rating) for bot, rating in ratings.items()]
    return rating_tuples


def launch_bot_benchmark(args: ProducerConfig):
    # clear dirs
    # todo

    # download benchmarked bots
    # todo

    # create all producer messages
    total_messages = launch_producer(args)

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
        bar = tqdm(total=total_messages, unit="game")
        last_messages = total_messages

        while last_messages != 0:
            current_messages = get_queued_cnt(channel)
            bar.update(last_messages - current_messages)
            last_messages = current_messages
            time.sleep(1)

        bar.close()

    finally:
        connection.close()

    df_results = process_results(args.result_dir)
    save_stats(*calc_stats(df_results))
    logger.info("Player elos")
    pprint(calc_elo(df_results))
