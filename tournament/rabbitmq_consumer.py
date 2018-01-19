import logging
from typing import Sequence, Callable, Any

import pika
from pika import ConnectionParameters
from pika.adapters.blocking_connection import BlockingChannel
from pika.spec import Basic, BasicProperties

logger = logging.getLogger(__name__)


class ExampleConsumer(object):
    QUEUE = 'text'

    def __init__(self, connection_params: ConnectionParameters):
        self._connection = None
        self._channel = None
        self._consumer_tag = None
        self._connection_params = connection_params

    def connect(self):
        self._connection = pika.BlockingConnection(self._connection_params)
        self._channel = self._connection.channel()
        self._channel.basic_qos(prefetch_count=1)
        self._consumer_tag = self._channel.basic_consume(self.on_message, self.QUEUE)

    def start_consuming(self):
        self._channel.start_consuming()

    def stop_consuming(self):
        self._channel.stop_consuming()

    def on_message(self, unused_channel, basic_deliver, properties, body):
        logger.info('Received message # %s from %s: %s',
                    basic_deliver.delivery_tag, properties.app_id, body)
        self.acknowledge_message(basic_deliver.delivery_tag)

    def acknowledge_message(self, delivery_tag):
        logger.info('Acknowledging message %s', delivery_tag)
        self._channel.basic_ack(delivery_tag)

    def close(self):
        logger.info('Closing connection')
        self._connection.close()


class AckConsumer(ExampleConsumer):
    # noinspection PyUnusedLocal
    def on_message(self, channel: BlockingChannel,
                   method: Basic.Deliver,
                   properties: BasicProperties,
                   body: bytes):

        # noinspection PyBroadException
        try:
            # Finally call the handler with payload from RMQ message
            self.handle_message(body.decode("utf-8"))

        except ConsumerException as e:
            logger.warning(f"Client sent invalid request raising a ControllerException!\n"
                           f"The message is rejected and sent to dead queue'.",
                           exc_info=True, extra={"data": {"message-body": body.decode("utf-8")}})
            channel.basic_reject(delivery_tag=method.delivery_tag, requeue=False)
        except Exception as e:
            logger.error(f"Unhandled exception occurred in running server!\n"
                         f"The message is rejected and sent to dead queue'.",
                         exc_info=True, extra={"data": {"message-body": body.decode("utf-8")}})
            channel.basic_reject(delivery_tag=method.delivery_tag, requeue=False)
        else:
            channel.basic_ack(delivery_tag=method.delivery_tag)

    def handle_message(self, msg: str):
        raise NotImplemented


class ConsumerException(Exception):
    pass


def consumer_error(*exceptions: Sequence[Exception]) -> Callable[..., Any]:
    """
    This decorator encapsulates exceptions thrown in decorated function
    as :py:class:`ControllerException` which have different error handling.
    """

    def _controller_error(fn) -> Callable[..., Any]:
        def wrapped(*args, **kwargs) -> Callable[..., Any]:
            try:
                return fn(*args, **kwargs)
            except exceptions as e:
                raise ConsumerException(e)

        return wrapped

    return _controller_error
