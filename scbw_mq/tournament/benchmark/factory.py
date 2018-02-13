from typing import Iterable

from .storage import BenchmarkStorage, Benchmark


def retrieve_benchmark(benchmark_name: str,
                       benchmark_storages: Iterable[BenchmarkStorage]) -> Benchmark:
    benchmark = None
    for bot_storage in benchmark_storages:
        maybe_benchmark = bot_storage.find_benchmark(benchmark_name)
        if maybe_benchmark is not None:
            benchmark = maybe_benchmark
            break

    if benchmark is None:
        raise Exception(f"Could not find benchmark '{benchmark_name}'")

    # make sure everything is ok :)
    benchmark.check_structure()

    return benchmark
