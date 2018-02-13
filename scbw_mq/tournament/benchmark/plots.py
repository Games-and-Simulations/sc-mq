import logging

import matplotlib.pyplot as plt
import pandas as pd
from pandas import DataFrame, Series

from .stats import save_stats

logger = logging.getLogger(__name__)

base_dir = "."


def plot_rr_overall_winrates(ser_overall_winrate: Series):
    plt.figure()
    bot_winrates = ser_overall_winrate.sort_values(ascending=False)
    ax = bot_winrates.plot(
        kind="bar",
        figsize=(ser_overall_winrate.shape[0] / 4, 6),
        title=f"Win rates of tournament bots",
        ylim=(0, 1.1),
        color="#8B96D0"
    )
    ax.set_xlabel("Bot name")
    ax.set_ylabel("Win rate")
    fig = ax.get_figure()
    fig.tight_layout()

    for p in ax.patches:
        ax.annotate("%.2f" % p.get_height(),
                    (p.get_x() + p.get_width() / 2., 0.01),
                    ha='center', va='bottom', xytext=(0, 10), textcoords='offset points',
                    rotation=90)
    fig.savefig(f"{base_dir}/rr_overall_winrates.pdf")
    save_stats(rr_overall_winrates=DataFrame(bot_winrates))


def plot_rr_elos(ser_elos: Series):
    plt.figure()
    ser_elos = ser_elos.sort_values(ascending=False)
    ax = ser_elos.plot(
        kind="bar",
        figsize=(len(ser_elos) / 4, 5),
        title=f"Elo ratings of tournament bots",
        ylim=(0, ser_elos.max()),
        color="#8B96D0"
    )
    ax.set_xlabel("Bot name")
    ax.set_ylabel("Elo rating")
    for p, patch_bot in zip(ax.patches, ser_elos.index.tolist()):
        ax.annotate("%.2f" % p.get_height(),
                    (p.get_x() + p.get_width() / 2., 0.01),
                    ha='center', va='bottom', xytext=(0, 10), textcoords='offset points',
                    rotation=90)

    fig = ax.get_figure()
    fig.tight_layout()
    fig.savefig(f"{base_dir}/rr_elos.pdf")
    save_stats(rr_elos=DataFrame(ser_elos))


def plot_rr_race_winrates(df_race_wintimes):
    race_winrates = df_race_wintimes.sum(axis=1) / \
                    (df_race_wintimes + df_race_wintimes.transpose()).sum(axis=1)

    plt.figure()
    ax = race_winrates.sort_values(ascending=False).plot(
        kind="bar",
        figsize=(5, 3),
        title=f"Win rates of tournament races",
        ylim=(0, 1.1),
        color="#8B96D0"
    )
    ax.set_ylabel("Win rate")
    ax.set_xlabel("")
    for p in ax.patches:
        ax.annotate("%.2f" % p.get_height(),
                    (p.get_x() + p.get_width() / 2., 0.01),
                    ha='center', va='bottom', xytext=(0, 10), textcoords='offset points',
                    rotation=90)
    fig = ax.get_figure()
    fig.tight_layout()
    fig.savefig(f"{base_dir}/rr_race_winrates.pdf")
    save_stats(rr_race_winrates=DataFrame(race_winrates))


def plot_rr_race_counts(ser_races: Series):
    race_counts = ser_races.groupby(ser_races).count().sort_values(ascending=False)
    plt.figure()
    ax = race_counts.plot(
        kind="bar",
        figsize=(5, 3),
        title=f"Number of tournament bots that use given race",
        ylim=(0, race_counts.max()),
        color="#8B96D0"
    )
    ax.set_xlabel("")
    ax.set_ylabel("")

    for p in ax.patches:
        ax.annotate("%d" % p.get_height(),
                    (p.get_x() + p.get_width() / 2., 0.01),
                    ha='center', va='bottom', xytext=(0, 10), textcoords='offset points',
                    rotation=90)
    fig = ax.get_figure()
    fig.tight_layout()
    fig.savefig(f"{base_dir}/rr_race_counts.pdf")
    save_stats(rr_race_counts=DataFrame(race_counts))


def plot_rr_game_times(df_gametimes: DataFrame):
    plt.figure()
    df2 = pd.DataFrame({col: vals['game_time'] for col, vals in df_gametimes.groupby(["bot"])})
    meds = df2.median()
    meds.sort_values(ascending=False, inplace=True)
    df2 = df2[meds.index]
    ax = df2.plot(
        kind="box",
        figsize=(df2.shape[1] / 4, 7),
        rot=90,
        grid=True
    )
    ax.set_title("Real-life time durations of play sorted by median times")
    ax.set_xlabel("Bot name")
    ax.set_ylabel("Time [sec]")
    fig = ax.get_figure()
    fig.tight_layout()
    fig.savefig(f"{base_dir}/rr_times.pdf")
    save_stats(rr_times=df2)


def plot_rr_maps_winrates(ser_maps: Series):
    maps = ser_maps.index.get_level_values(level=0)
    best_bot_on_map = DataFrame(ser_maps).groupby(maps).apply(
        lambda x: pd.Series([x['win_rate'].argmax()[1], x['win_rate'].max()],
                            index=["bot", "score"]))
    ax = best_bot_on_map.plot(
        kind="bar",
        figsize=(12, 6),
        rot=90,
        legend=None,
        ylim=(0, 1.1),
        color="#8B96D0"
    )
    ax.set_title("Best-scoring bots on each tournament map scenario")
    ax.set_xlabel("Map name")
    ax.set_ylabel("Win rate")
    for p, bot in zip(ax.patches, best_bot_on_map['bot'].tolist()):
        ax.annotate("%.2f %s" % (p.get_height(), bot),
                    (p.get_x() + p.get_width() / 2., 0.01),
                    ha='center', va='bottom', xytext=(0, 10), textcoords='offset points',
                    rotation=90)
    fig = ax.get_figure()
    fig.tight_layout()
    fig.savefig(f"{base_dir}/rr_maps.pdf")
    save_stats(rr_maps=best_bot_on_map)


def plot_bot_overall_winrates(bot: str, ser_overall_winrate: Series):
    plt.figure()
    bot_winrates = ser_overall_winrate.sort_values(ascending=False)
    ax = bot_winrates.plot(
        kind="bar",
        figsize=(ser_overall_winrate.shape[0] / 4, 6),
        title=f"Updated win rates after playing '{bot}' with tournament bots",
        ylim=(0, 1.1),
        color="#8B96D0"
    )
    ax.set_xlabel("Bot name")
    ax.set_ylabel("Win rate")
    fig = ax.get_figure()
    fig.tight_layout()

    for p in ax.patches:
        ax.annotate("%.2f" % p.get_height(),
                    (p.get_x() + p.get_width() / 2., 0.01),
                    ha='center', va='bottom', xytext=(0, 10), textcoords='offset points',
                    rotation=90)

    pos = bot_winrates.index.get_loc(bot)
    ax.patches[pos].set_facecolor('#ff0000')

    fig.savefig(f"{base_dir}/bot_overall_winrates.pdf")
    save_stats(bot_overall_winrates=DataFrame(bot_winrates))


def plot_bot_rr_winrates(bot: str, df_rr_winrate: DataFrame):
    plt.figure()
    bots = set(df_rr_winrate.columns)
    other_winrates = df_rr_winrate.loc[bot, bots - {bot}].sort_values(ascending=False)
    ax = other_winrates.plot(
        kind="bar",
        figsize=(df_rr_winrate.shape[0] / 4, 5),
        title=f"Win rate of bot '{bot}' against each opponent",
        ylim=(0, 1.1),
        color="#8B96D0"
    )
    ax.set_xlabel("Bot name")
    ax.set_ylabel("Win rate")
    for p in ax.patches:
        ax.annotate("%.2f" % p.get_height(),
                    (p.get_x() + p.get_width() / 2., 0.01),
                    ha='center', va='bottom', xytext=(0, 10), textcoords='offset points',
                    rotation=90)

    fig = ax.get_figure()
    fig.tight_layout()
    fig.savefig(f"{base_dir}/bot_rr_winrates.pdf")
    save_stats(bot_rr_winrates=DataFrame(other_winrates))


def plot_bot_elos(bot: str, ser_elos: Series):
    plt.figure()
    ser_elos = ser_elos.sort_values(ascending=False)
    ax = ser_elos.plot(
        kind="bar",
        figsize=(len(ser_elos) / 4, 5),
        title=f"Updated elo ratings after playing '{bot}' with tournament bots",
        ylim=(0, ser_elos.max()),
        color="#8B96D0"
    )
    ax.set_xlabel("Bot name")
    ax.set_ylabel("Elo rating")
    for p, patch_bot in zip(ax.patches, ser_elos.index.tolist()):
        ax.annotate("%.2f" % p.get_height(),
                    (p.get_x() + p.get_width() / 2., 0.01),
                    ha='center', va='bottom', xytext=(0, 10), textcoords='offset points',
                    rotation=90)

    pos = ser_elos.index.get_loc(bot)
    ax.patches[pos].set_facecolor('#ff0000')

    fig = ax.get_figure()
    fig.tight_layout()
    fig.savefig(f"{base_dir}/bot_elos.pdf")
    save_stats(bot_elos=DataFrame(ser_elos))


def plot_bot_race_winrates(bot: str, df_botrace_winrate: DataFrame):
    plt.figure()
    bot_races = df_botrace_winrate.loc[bot].sort_values(ascending=False)
    ax = bot_races.plot(
        kind="bar",
        figsize=(5, 3),
        title=f"Win rate of bot '{bot}' given a race",
        ylim=(0, 1.1),
        color="#8B96D0"
    )
    ax.set_ylabel("Win rate")
    ax.set_xlabel("")
    fig = ax.get_figure()
    fig.tight_layout()

    for p in ax.patches:
        ax.annotate("%.2f" % p.get_height(),
                    (p.get_x() + p.get_width() / 2., 0.01),
                    ha='center', va='bottom', xytext=(0, 10), textcoords='offset points',
                    rotation=90)
    fig.savefig(f"{base_dir}/bot_races.pdf")
    save_stats(bot_races=DataFrame(bot_races))


def plot_bot_maps_winrates(bot, ser_maps):
    plt.figure()
    map_results = ser_maps.unstack(level=0).transpose()
    bot_maps = map_results.loc[:, bot]
    ax = bot_maps.plot(
        kind="bar",
        figsize=(7, 6),
        ylim=(0, 1.1),
        title=f"Win rate of bot '{bot}' given a map",
        color="#8B96D0")
    ax.set_xlabel("Map name")
    ax.set_ylabel("Win rate")
    fig = ax.get_figure()
    fig.tight_layout()
    for p in ax.patches:
        ax.annotate("%.2f" % p.get_height(),
                    (p.get_x() + p.get_width() / 2., 0.01),
                    ha='center', va='bottom', xytext=(0, 10), textcoords='offset points',
                    rotation=90)
    fig.savefig(f"{base_dir}/bot_maps.pdf")
    save_stats(bot_maps=DataFrame(bot_maps))


def plot_overall_results(ser_overall_winrate, df_race_wintimes, df_gametimes,
                         ser_bot_races, ser_maps, ser_elos):
    plot_rr_overall_winrates(ser_overall_winrate)
    plot_rr_elos(ser_elos)
    plot_rr_race_winrates(df_race_wintimes)
    plot_rr_race_counts(ser_bot_races)
    plot_rr_game_times(df_gametimes)
    plot_rr_maps_winrates(ser_maps)


def plot_bot_results(bot: str, df_rr_winrate, ser_overall_winrate, df_botrace_winrate,
                     ser_maps, ser_elos):
    plot_bot_overall_winrates(bot, ser_overall_winrate)
    plot_bot_elos(bot, ser_elos)
    plot_bot_rr_winrates(bot, df_rr_winrate)
    plot_bot_race_winrates(bot, df_botrace_winrate)
    plot_bot_maps_winrates(bot, ser_maps)
