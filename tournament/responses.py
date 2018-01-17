import logging
from functools import wraps


def argument_logger(fn):
    """
    A decorator which simplifies logging of incoming requests to the API endpoint.

    Each access to a function decorated by this decorator is logged together with the passed parameters.
    """

    @wraps(fn)
    def _logger(*args, **kwargs):
        logger = logging.getLogger()  # use root logger

        # ignore self (1) and take only up to number of args (fn.__code__.co_argcount)
        args_names = fn.__code__.co_varnames[1:fn.__code__.co_argcount]
        all_params = dict(zip(args_names, args))
        all_params.update(kwargs)
        fn_name = fn.__code__.co_name
        fn_file = fn.__code__.co_filename
        fn_line = fn.__code__.co_firstlineno

        if any(all_params):
            serialized_params = " ".join("{%s}={%s}" % (k, v) for k, v in all_params.items())
        else:
            serialized_params = "(no params)"

        logger.info(f"{fn_file}:{fn_name} L{fn_line}: {serialized_params}")

        return fn(*args, **kwargs)

    return _logger
