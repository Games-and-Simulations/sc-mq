import csv
import glob
import json
import logging
from typing import Dict, Optional

import elo
import numpy as np
import pandas as pd
from pandas import DataFrame, Series
from tqdm import tqdm

logger = logging.getLogger(__name__)

elo.WIN = 1.
elo.DRAW = 0.5
elo.LOSS = 0.
elo.K_FACTOR = 20
elo.INITIAL = 2000
elo.BETA = 200


def process_results(result_dir: str) -> DataFrame:
    rows = {"game_name": [],
            "map": [],
            "winner": [],
            "winner_race": [],
            "loser": [],
            "loser_race": [],
            "game_time": []}

    race = dict(
        T="Terran",
        Z="Zerg",
        P="Protoss",
        R="Random"
    )

    for file in tqdm(glob.glob(f"{result_dir}/*/result.json"), unit="game"):
        with open(file, "r") as f:
            info = json.load(f)

        rows["game_name"].append(info["game_name"])
        rows["map"].append(info["map"].replace("sscai/", ""))
        rows["winner"].append(info['winner'])
        rows["winner_race"].append(race[info['winner_race']])
        rows["loser"].append(info['loser'])
        rows["loser_race"].append(race[info['loser_race']])
        rows["game_time"].append(info["game_time"])

    return DataFrame(rows).set_index("game_name")


def calc_stats(df: DataFrame, ser_round_robin_elos: Optional[Series]):
    # helper col
    df['one'] = 1

    bots = set(df['winner']).union(set(df['loser']))

    #  Win times
    df_wintimes = pd.pivot_table(df, index='winner', columns='loser', values='one', aggfunc=np.sum) \
        .fillna(0).sort_index()
    for missing_bot in bots - set(df_wintimes.columns):
        df_wintimes[missing_bot] = 0
    for missing_bot in bots - set(df_wintimes.index):
        df_wintimes = df_wintimes.append(Series({bot: 0 for bot in bots}, name=missing_bot))
    df_wintimes = df_wintimes.sort_index(axis=0).sort_index(axis=1)

    # Win rate
    df_rr_winrate = (df_wintimes / (df_wintimes + df_wintimes.transpose()))
    ser_overall_winrate = (
        df_wintimes.sum(axis=1) /
        (df_wintimes + df_wintimes.transpose()).sum(axis=1)
    ).sort_values(ascending=False)

    # Game times
    df_winner = df[['winner', 'winner_race', 'game_time']]
    df_winner.columns = ['bot', 'race', 'game_time']
    df_loser = df[['loser', 'loser_race', 'game_time']]
    df_loser.columns = ['bot', 'race', 'game_time']
    df_gametimes: DataFrame = pd.concat((df_winner, df_loser))

    # Map winning rates
    map_index = pd.MultiIndex.from_product([list(set(df['map'])), list(bots)])
    df_map_winners = df.groupby(by=["map", "winner"])['one'].sum().reindex(map_index)
    df_map_losers = df.groupby(by=["map", "loser"])['one'].sum().reindex(map_index)
    ser_maps = df_map_winners / (df_map_winners + df_map_losers)
    ser_maps.name = 'win_rate'

    # Race win times
    ser_bot_races = df_gametimes.set_index("bot").groupby("bot")['race'].head(1)
    df_race_wintimes = pd.pivot_table(df, index='winner_race', columns='loser_race',
                                      values='one', aggfunc=np.sum)
    # ... this is probably not needed
    races = set(ser_bot_races.unique())
    for missing_race in races - set(df_race_wintimes.columns):
        df_race_wintimes[missing_race] = 0
    for missing_race in races - set(df_race_wintimes.index):
        df_race_wintimes = df_race_wintimes.append(
            Series({race: 0 for race in races}, name=missing_race))

    # Each bot winrates against each race
    df_botrace_wintimes = pd.pivot_table(
        df, index='winner', columns='loser_race', values='one', aggfunc=np.sum) \
        .fillna(0).sort_index()
    df_botrace_losetimes = pd.pivot_table(
        df, index='loser', columns='winner_race', values='one', aggfunc=np.sum) \
        .fillna(0).sort_index()
    df_botrace_winrate = df_botrace_wintimes / (df_botrace_wintimes + df_botrace_losetimes)

    # Calculate elos
    if ser_round_robin_elos is None:
        ser_elos = calc_round_robin_elo(df)
    else:
        ser_elos = calc_player_elo(ser_round_robin_elos, df)

    return df_rr_winrate, \
           ser_overall_winrate, \
           df_gametimes, \
           df_race_wintimes, \
           df_botrace_winrate, \
           ser_maps, \
           ser_bot_races, \
           ser_elos


def save_stats(**df):
    for name, df in df.items():
        df.to_csv(f"{name}.csv", sep=",", quoting=csv.QUOTE_ALL)


def calc_round_robin_elo(df_results: DataFrame) -> Series:
    bots = set(df_results['winner']).union((set(df_results['loser'])))
    initial_ratings = {bot: elo.Rating() for bot in bots}
    return calc_elo(initial_ratings, df_results)


def calc_player_elo(ser_round_robin_elo: Series, df_bot_results: DataFrame) -> Series:
    ratings = {bot: elo.Rating(value=score) for bot, score in ser_round_robin_elo.items()}
    return calc_elo(ratings, df_bot_results)


def calc_elo(ratings: Dict[str, elo.Rating], df_game_results: DataFrame):
    elo_calc = elo.Elo(rating_class=elo.Rating)
    for i in np.arange(len(df_game_results)):
        winner = df_game_results.iloc[i]['winner']
        loser = df_game_results.iloc[i]['loser']

        winner_elo, loser_elo = elo_calc.rate_1vs1(ratings[winner],
                                                   ratings[loser], drawn=False)

        ratings[winner] = winner_elo
        ratings[loser] = loser_elo

    return Series({bot: rating.value for bot, rating in ratings.items()}, name="elo")
