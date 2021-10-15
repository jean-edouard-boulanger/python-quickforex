import logging


logger = logging.getLogger("quickforex")


def get_module_logger(name) -> logging.Logger:
    return logger.getChild(name)
