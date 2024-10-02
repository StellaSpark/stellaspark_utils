# Standard Library imports
import collections
import io
import logging
import sys
import threading


def get_threadlogger():
    """Get logger if it already exists for this thread, create if not."""
    thread_id = threading.get_ident()
    logger = logging.getLogger(str(thread_id))

    if not logger.hasHandlers():
        logger.setLevel(logging.INFO)

        # Log to backend
        log_stream = FIFOIO(5000)  # Only show last 5000 chars of log
        backend_handler = logging.StreamHandler(log_stream)
        backend_handler.setLevel(logging.INFO)
        backend_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s - %(message)s", "%Y-%m-%d %H:%M:%S"))
        logger.addHandler(backend_handler)

        # Log to console
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(
            logging.Formatter(
                "[%(threadName)s] %(asctime)s %(levelname)s - %(message)s",
                "%Y-%m-%d %H:%M:%S",
            )
        )
        logger.addHandler(console_handler)

    return logger


class FIFOIO(io.TextIOBase):
    """Rolling in-memory log."""

    def __init__(self, size, *args):
        self.maxsize = size
        io.TextIOBase.__init__(self, *args)
        self.deque = collections.deque()

    def getvalue(self):  # noqa
        return "".join(self.deque)

    def clear(self):  # noqa
        self.deque.clear()

    def write(self, x):  # noqa
        self.deque.append(x)
        self.shrink()

    def shrink(self):
        """Reduce FIFO log to max size."""
        if self.maxsize is None:
            return
        size = sum(len(x) for x in self.deque)
        while size > self.maxsize:
            x = self.deque.popleft()
            size -= len(x)
