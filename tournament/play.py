import logging
from argparse import Namespace
from typing import Dict

from scbw import DockerException, GameException

from .rabbitmq_consumer import JsonConsumer, consumer_error
from .responses import argument_logger

logger = logging.getLogger(__name__)


