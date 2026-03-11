
import logging
import json
import time

class ColoredFormatter(logging.Formatter):

    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    # bold_red = "\x1b[31;1m"
    bold_red = "\x1b[1;37;41m"
    reset = "\x1b[0m"
    format = "%(levelname)s - %(message)s"
    # format = "%(levelname)s - %(message)s (%(filename)s:%(lineno)d)"
    # format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"

    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: grey + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
logging.getLogger("urllib3").setLevel(logging.WARNING)
# logging.basicConfig(
#     level=logging.INFO,
#     # format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
#     format="%(levelname)s | %(name)s | %(message)s"
# )

handler = logging.StreamHandler()
handler.setFormatter(
    ColoredFormatter("%(asctime)s - %(levelname)s - %(message)s")
)

log.addHandler(handler)

def printj(dic, sort_keys = True):
    print(json.dumps(dic, indent=4, sort_keys=sort_keys))


timers = {}

def timerstart(name = "default"):
    timers[name] = time.time()

def timerend(name = "default"):
    now = time.time()
    log.debug(f'\033[94mTIMER {name} = {now - timers.get(name, 0)} s\033[0m')