# -*- coding: utf-8 -*-
"""
Documentation:
"""


# ---------------------------------
# import libraries
import os
import logging
import re
import sys
import traceback
from functools import wraps
from datetime import datetime
import time
import threading

# ---------------------------------


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
user_doc = os.path.expanduser('~')
log_dir = os.path.join(user_doc, "Djed")
if not os.path.isdir(log_dir):
    os.makedirs(log_dir)
file_handler = logging.FileHandler(os.path.join(log_dir, "ERROR_"+os.environ.get('USERNAME')+'.log'))
logger.addHandler(file_handler)

def timmer(name):
    def timer_decrt(func):
        @wraps(func)
        def func_wrapper(*args, **kwargs):
            start_time = datetime.now()
            logger.debug("StartTime: {}".format(start_time.strftime("%Y-%m-%d %H:%M:%S")))
            func(*args, **kwargs)
            end_time = datetime.now()
            logger.debug("EndTime: {}".format(end_time.strftime("%Y-%m-%d %H:%M:%S")))
            logger.debug("Duration: {}".format(end_time-start_time))
        return func_wrapper
    return timer_decrt

def error(name):
    try:
        from PySide2.QtWidgets import QMessageBox
    except:
        pass

    def error_decrt(func):
        @wraps(func)
        def func_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                fpath = re.findall(r'File \".*\"', traceback.format_exc())[1].split('"')[-2]
                error_text = '\n'.join([str(e), "*"*100, traceback.format_exc(), "\n", *traceback.format_stack()])

                err = "#"*100+"\n"+"ERROR - {} {}:\n\n {}".format(time.strftime("%d/%m/%y %X"), name, error_text)+"#"*100
                logger.debug(err)
                try:
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Critical)
                    msg.setText(f"Error in <a href=file:///{fpath}>{os.path.basename(fpath)}</a>")
                    msg.setInformativeText(str(error_text))
                    msg.setWindowTitle("Error")
                    msg.exec_()

                except Exception as e:
                    print(e)
                    print(err)
        return func_wrapper
    return error_decrt


def setInterval(interval):
    def decorator(function):
        def wrapper(*args, **kwargs):
            stopped = threading.Event()

            def loop(): # executed in another thread
                while not stopped.wait(interval): # until stopped
                    function(*args, **kwargs)

            t = threading.Thread(target=loop)
            t.daemon = True # stop if the program exits
            t.start()
            return stopped
        return wrapper
    return decorator



def debug(func=None):
    """
    To print the function name
    @param func:
    @return:
    """
    def wrapper(*args, **kwargs):
        try:
            function_name = func.__func__.__qualname__
        except:
            function_name = func.__qualname__
        return func(*args, **kwargs, function_name=function_name)
    return wrapper

def func():
    print('five')

# Main function
def main():
    debug(func)



if __name__ == '__main__':
    print(("-" * 20) + "\nStart of code...\n" + ("-" * 20))
    main()
    print(("-" * 20) + "\nEnd of code.\n" + ("-" * 20))
