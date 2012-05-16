import logging

class NullHandler(logging.Handler):
    def emit(self, record):
        pass

logger = logging.getLogger("django_cachebust")
logger.addHandler(NullHandler())
