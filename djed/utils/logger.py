# -*- coding: utf-8 -*-
"""
Documentation:
"""

import logging
import os

DJED_ROOT = os.getenv('DJED_ROOT')

log_file_path = DJED_ROOT + '/test/logs/log.log'


class Logger(object):
    def __init__(self, name=None):
        self.log = logging.getLogger(__name__)
        if name:
            self.log = logging.getLogger(name)

        if not len(self.log.handlers):  # To stop the duplicates of logs
            self.log.setLevel(logging.INFO)

            # console
            stream_handler = logging.StreamHandler()
            formatter = logging.Formatter('%(message)s')
            stream_handler.setFormatter(formatter)
            self.log.addHandler(stream_handler)

            # file
            file_handler = logging.FileHandler(log_file_path)
            file_handler.setLevel(logging.DEBUG)
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', "%Y-%m-%d %H:%M:%S")
            file_handler.setFormatter(formatter)
            self.log.addHandler(file_handler)

    def info(self, message):
        self.log.info(message)

    def debug(self, message):
        self.log.debug(message)

    def warning(self, message):
        self.log.warning(message)

    def error(self, message):
        self.log.setLevel(logging.ERROR)
        self.log.error(message)


if __name__ == '__main__':
    log = Logger()
    log.error('foo')
    print(__name__)
