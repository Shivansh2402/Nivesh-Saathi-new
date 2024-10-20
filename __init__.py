import gzip
import logging.handlers
import os
from logging import Formatter
from logging.handlers import TimedRotatingFileHandler

from metahackathonfinance.default_config import Settings

from metahackathonfinance.middlewares import get_request_id, get_correlation_id, RequestContextLogMiddleware
from fastapi import FastAPI

app = FastAPI()
app.add_middleware(RequestContextLogMiddleware)

extra = {"props": {"app_name": "meta-hackathon-finance"}}

settings = Settings()

class AppFilter(logging.Filter):
    def filter(self, record):
        record.correlation_id = get_correlation_id()
        record.request_id = get_request_id()
        return True

class GZipRotator:
    def __call__(self, source, dest):
        os.rename(source, dest)
        f_in = open(dest, 'rb')
        f_out = gzip.open("%s.gz" % dest, 'wb')
        f_out.writelines(f_in)
        f_out.close()
        f_in.close()
        os.remove(dest)


gzip_rotator = GZipRotator()

# logger configuration
my_logger = logging.getLogger('metahackathonfinance')

log_level_map = {"DEBUG": logging.DEBUG, "INFO": logging.INFO, "ERROR": logging.ERROR, "WARN": logging.WARN}

# Basic Log level configuration
logging.basicConfig(level=log_level_map.get(settings.log_level), datefmt="%Y-%m-%d %H:%M:%S %z")

# Formatter for application logs
app_formatter = Formatter('[%(asctime)s] [%(levelname)s] [request_id:%(request_id)s] [%(module)s:%(funcName)s:%('
                          'lineno)s] %(message)s')

# Application Logs
app_log_file = os.path.join(settings.log_directory, 'meta-hackathon-finance.log')
app_log_timed_rotating_file_handler = TimedRotatingFileHandler(app_log_file, when="midnight", interval=1,
                                                               backupCount=settings.log_max_history)
app_log_timed_rotating_file_handler.suffix = "%Y-%m-%d"
app_log_timed_rotating_file_handler.addFilter(AppFilter())
app_log_timed_rotating_file_handler.setFormatter(app_formatter)
app_log_timed_rotating_file_handler.rotator = gzip_rotator
my_logger.addHandler(app_log_timed_rotating_file_handler)

my_logger = logging.LoggerAdapter(my_logger, extra)


my_logger.info("meta-hackathon-finance is starting")

from metahackathonfinance.controller import mongo_controller, answers_controller, bing_controller, external_communicator
from metahackathonfinance import healthcheck
