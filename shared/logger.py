import logging
from datetime import datetime

class ServiceLogger:
    def __init__(self, service_name):
        self.logger = logging.getLogger(service_name)
        self.setup_logger()

    def setup_logger(self):
        c_handler = logging.StreamHandler()
        f_handler = logging.FileHandler(f'logs/{datetime.now().strftime("%Y-%m-%d")}.log')
        
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        c_format = logging.Formatter(log_format)
        f_format = logging.Formatter(log_format)
        c_handler.setFormatter(c_format)
        f_handler.setFormatter(f_format)

        self.logger.addHandler(c_handler)
        self.logger.addHandler(f_handler)
        self.logger.setLevel(logging.INFO)

    def info(self, message):
        self.logger.info(message)

    def error(self, message):
        self.logger.error(message)

    def warning(self, message):
        self.logger.warning(message)

    def debug(self, message):
        self.logger.debug(message)
