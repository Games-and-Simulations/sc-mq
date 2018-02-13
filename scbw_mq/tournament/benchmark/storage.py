import logging
import os
import shutil
from os.path import exists
from typing import Optional

from scbw.map import check_map_exists
from scbw.player import check_bot_exists
from scbw.utils import download_extract_zip

from ...utils import read_lines

logger = logging.getLogger(__name__)


class BenchmarkException(Exception):
    pass


class RerunningBenchmarkException(BenchmarkException):
    pass


class Benchmark:
    bot_file: str
    map_file: str
    elo_file: str
    repeat_games: int

    bot_dir: str
    map_dir: str
    result_dir: str

    def check_structure(self):
        if not exists(f"{self.bot_file}"):
            raise BenchmarkException(f"Bot file cannot be found in {self.bot_file}")
        if not exists(self.map_file):
            raise BenchmarkException(f"Map file cannot be found in {self.map_file}")
        if not exists(self.elo_file):
            raise BenchmarkException(f"Elo file cannot be found in {self.elo_file}")
        if not exists(self.bot_dir):
            raise BenchmarkException(f"Bot dir cannot be found in {self.bot_dir}")
        if not exists(f"{self.map_dir}"):
            raise BenchmarkException(f"Map dir cannot be found in {self.map_dir}")
        if not exists(f"{self.result_dir}"):
            raise BenchmarkException(f"Result dir cannot be found in {self.result_dir}")

        bots = read_lines(self.bot_file)
        for bot in bots:
            check_bot_exists(bot, self.bot_dir)

        maps = read_lines(self.map_file)
        for map_file in maps:
            check_map_exists(f"{self.map_dir}/{map_file}")

    def has_results(self):
        return len(os.listdir(self.result_dir)) > 0


class BenchmarkStorage:
    def find_benchmark(self, name: str) -> Optional[Benchmark]:
        raise NotImplemented

    def get_benchmark(self, local_benchmark_dir):
        with open(f'{local_benchmark_dir}/BENCHMARK_REPEAT_GAMES', 'r') as f:
            repeat_games = int(f.read().strip())

        benchmark = Benchmark()
        benchmark.bot_file = f"{local_benchmark_dir}/BENCHMARK_BOTS"
        benchmark.map_file = f"{local_benchmark_dir}/BENCHMARK_MAPS"
        benchmark.elo_file = f"{local_benchmark_dir}/BENCHMARK_ELOS"
        benchmark.bot_dir = f"{local_benchmark_dir}/bots"
        benchmark.map_dir = f"{local_benchmark_dir}/maps"
        benchmark.result_dir = f"{local_benchmark_dir}/results"
        benchmark.repeat_games = repeat_games

        return benchmark


class LocalBenchmarkStorage(BenchmarkStorage):
    def __init__(self, base_dir: str):
        self.base_dir = base_dir

    def find_benchmark(self, name: str) -> Optional[Benchmark]:
        if exists(self.benchmark_dir(name)):
            return self.get_benchmark(self.benchmark_dir(name))

        return None

    def benchmark_dir(self, benchmark_name: str):
        return f'{self.base_dir}/{benchmark_name}'


class SscaitBenchmarkStorage(LocalBenchmarkStorage):
    BASE_URL = "http://sscaitournament.com/benchmarks"

    def find_benchmark(self, name: str) -> Optional[Benchmark]:
        if not name.startswith("SSCAIT"):
            return None

        if exists(self.benchmark_dir(name)):
            return self.get_benchmark(self.benchmark_dir(name))

        return self.try_download(name)

    def try_download(self, name: str) -> Optional[Benchmark]:
        benchmark_dir = self.benchmark_dir(name)
        try:
            os.makedirs(benchmark_dir, exist_ok=False)
            download_extract_zip(f"{self.BASE_URL}/{name}.zip", benchmark_dir)
            return self.get_benchmark(benchmark_dir)

        except Exception as e:
            logger.exception(f"Failed to download benchmark {name}")
            logger.exception(e)

            logger.info(f"Cleaning up dir {benchmark_dir}")
            shutil.rmtree(self.benchmark_dir(name))

            return None

# Feel free to include other benchmark sources!
# But they need to respect benchmark / bot structure :)
