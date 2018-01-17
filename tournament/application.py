import logging
import traceback

from multiprocessing import Process

logger = logging.getLogger(__name__)


class Worker:
    def run(self) -> None:
        raise NotImplemented


class MultiprocApplication:
    def __init__(self, rabbitmq_worker: type, n_processes: int):
        self.worker = rabbitmq_worker
        self.n_processes = n_processes
        self.worker_pool = []
        self.process_pool = []

    def run(self) -> None:
        try:
            self.start()
        except Exception:
            exc = traceback.format_exc()
            logger.error("Unhandled exception occurred in running server:")
            logger.error(exc)

    def start(self) -> None:
        logger.info("Starting rabbitmq rabbitmq")

        for i in range(self.n_processes):
            worker_instance = self.worker()
            p = Process(target=worker_instance.run)
            p.start()
            # todo: proper shutdown?
            self.process_pool.append(p)
            self.worker_pool.append(worker_instance)
