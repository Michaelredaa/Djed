# -*- coding: utf-8 -*-
"""
Documentation:
"""

import logging
import os
import sys
import traceback

DJED_ROOT = os.getenv('DJED_ROOT')




class Logger(object):
    def __init__(self, name=None, filepath=None, use_file=False):

        sys.excepthook = self.handel_exception

        self.log = logging.getLogger(__name__)
        if name:
            self.log = logging.getLogger(name)

        log_file_path = DJED_ROOT + '/test/logs/log.log'
        if filepath:
            log_file_path = filepath

        if not os.path.isdir(os.path.dirname(log_file_path)):
            os.makedirs(os.path.dirname(log_file_path))

        if not len(self.log.handlers):  # To stop the duplicates of logs
            self.log.setLevel(logging.INFO)

            # console
            stream_handler = logging.StreamHandler()
            formatter = logging.Formatter('[Djed] %(message)s')
            stream_handler.setFormatter(formatter)
            self.log.addHandler(stream_handler)

            if use_file:
                # file
                self.log.setLevel(logging.DEBUG)

                file_handler = logging.FileHandler(log_file_path)
                file_handler.setLevel(logging.DEBUG)
                formatter = logging.Formatter('%(asctime)s - %(name)s -%(levelname)s - %(message)s',
                                              "%Y-%m-%d %H:%M:%S")
                file_handler.setFormatter(formatter)
                self.log.addHandler(file_handler)



    def handel_exception(self, exc_type, exc_value, exc_traceback):
        tb = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        self.log.error(tb)

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
    log = Logger(use_file=True)
    log.debug('foo')
    1/0
    print(__name__)
