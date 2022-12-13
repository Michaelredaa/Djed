# -*- coding: utf-8 -*-
"""
Documentation:
"""

# ---------------------------------
# import libraries
import sys
import os
import site
import traceback
import socket
import struct
import time
import threading

DJED_ROOT = os.getenv('DJED_ROOT')

site.addsitedir(os.path.join(DJED_ROOT, 'venv', 'python39', 'Lib', 'site-packages'))

from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtGui import *

WAIT_TIME = 0.025
READ_BODY_TIMEOUT_S = 5.0
SOCKET_TIMEOUT_S = 30.0

App = QCoreApplication(sys.argv)
class WorkerSignals(QObject):
    """
    Defines the signals available from a running worker thread.

    Supported signals are:

    finished
        No data

    error
        tuple (exctype, value, traceback.format_exc() )

    result
        object data returned from processing, anything

    progress
        int indicating % progress

    """
    finished = Signal()
    error = Signal(tuple)
    result = Signal(object)
    progress = Signal(int)


class Worker(QRunnable):
    """
    Worker thread

    Inherits from QRunnable to handler worker thread setup, signals and wrap-up.

    :param callback: The function callback to run on this worker thread. Supplied args and
                     kwargs will be passed through to the runner.
    :type callback: function
    :param args: Arguments to pass to the callback function
    :param kwargs: Keywords to pass to the callback function

    """

    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()

        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

        # Add the callback to our kwargs
        self.kwargs['progress_callback'] = self.signals.progress

    @Slot()
    def run(self):
        '''
        Initialise the runner function wif passed args, kwargs.
        '''

        # Retrieve args/kwargs here; and fire processing using them
        try:
            result = self.fn(*self.args, **self.kwargs)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)  # Return the result of the processing
        finally:
            self.signals.finished.emit()  # Done


class Timer(QTimer):
    """
    To execute certain function ever with time interval
    """

    def __init__(self, fun, *args, **kwargs):
        super(Timer, self).__init__()

        self.timer = QTimer()
        self.timer.timeout.connect(fun, *args, **kwargs)

    def set_time(self, t=1):
        self.timer.setInterval(int(t))

    def start(self):
        self.timer.start()

    def stop(self):
        self.timer.stop()


class HServer_old(threading.Thread):
    def __init__(self, host='172.0.0.1', port=19091):
        threading.Thread.__init__(self)

        self.host = host
        self.port = port

        self._socket = None
        self.thread_running = True
        # self.__guid = uuid.uuid4()

        # start thread
        self.setDaemon(True)
        self.start()

    def stop(self):
        self.thread_running = False
        if self._socket:
            self._socket.close()

    def run(self):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self._socket.bind((self.host, self.port))
            self._socket.listen(1)
        except socket.error:
            self._socket.close()
            self._socket = None
            self.thread_running = False
            return

        while self.thread_running:
            conn, address = self._socket.accept()
            while self.thread_running:
                data = conn.recv(4096)

                if data:
                    exec(data.decode())
                else:
                    break


class SocketServer():
    Instance = []

    def __init__(self, host='172.0.0.1', port=19091):
        self.__class__.Instance.append(self)

        self.host = host
        self.port = port

        self.thread_running = True
        self.start_socket()

        self.threadpool = QThreadPool()

    def start_socket(self):
        try:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._socket.bind((self.host, self.port))
            self._socket.listen(1)
        except Exception as e:
            print(e)
            self.thread_complete()

    def receive(self, progress_callback):
        while self.thread_running:
            conn, address = self._socket.accept()
            while self.thread_running:
                data = conn.recv(4096)
                if data:
                    exec(data.decode())
                else:
                    break

    def print_output(self, s):
        print("output: ", s)

    def thread_complete(self):
        self.thread_running = False
        self._socket.close()
        print("THREAD COMPLETE!")

    def run(self):
        # Pass the function to execute
        worker = Worker(self.receive)  # Any other args, kwargs are passed to the run function
        worker.signals.result.connect(self.print_output)
        worker.signals.finished.connect(self.thread_complete)

        # Execute
        # self.threadpool.start(worker)
        QThreadPool.globalInstance().start(worker)

class OpenSocket:
    def __init__(self, host='172.0.0.1', port=39390):
        """
        Default constructor. By default, tries to connect to localhost:55000
        """
        self.status = False
        self.mode = False  # True: Statement False: Script
        self.connect(host, int(port))

    def connect(self, host, port):
        """
        Connect to the command port of a host
        :param host: (str) The name or the IP address of the remote host
        :param port: (int) The command port set on the remote host
        return: None
        """
        self.close()
        self.status = False
        try:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._socket.settimeout(SOCKET_TIMEOUT_S)
            self._socket.connect((host, int(port)))

        except:
            raise ValueError('Failed to connect to ' + host + ':' + str(port))
        self.status = True

    def close(self):
        """
        Close the connection to the command port.
        return: None
        """
        if self.status:
            self._socket.close()

    def run(self, script):
        """
        Run the specified python script on a host.
        :param script: (str) script command to execute on host remotely.
        return: None
        """
        self.mode = 0
        self._send(script, self.mode)
        received = self._receive()

    def evaluate(self, statement):
        """
        Evaluate the input statement on the remote host and return the result as string.
        :param statement: (str) string to evaluted
        return:(str) the result as string
        """

        self.mode = 1
        self._send(statement, self.mode)
        return self._receive()

    def send(self, command):
        self._send(command)

    def _send(self, command, mode=None):
        """
        internal method used to communicate with the remove command port
        :param command: (str) command to send
        :param mode: (bool) Statement(True), Script(False)
        return: (str) the result as string
        """

        if not self.status:
            raise RuntimeError('Not connected to Host')

        # send the command
        # command_size = len(command) + 1
        # command_size = struct.pack("<I", command_size)
        # self._socket.sendall(command_size)
        packet = command
        self._socket.send(bytes(packet.encode()))

    def _receive(self):
        """
        To receive result string from host
        return: (str) the result as string
        """
        if not self.status:
            raise RuntimeError('Not connected to Host')

        # receive result size
        result_size = self._socket.recv(4)
        if not result_size:
            raise RuntimeError("Could not retrieve message header.")
        result_size = struct.unpack("<I", result_size)[0]

        time_read_start = time.time()

        # receive result
        result = b''
        while result_size:
            chunk = self._socket.recv(result_size)
            if not chunk:
                """
                If the content_length indicates a bigger message than
                has actually been sent, we might hang in this loop
                forever, unless we time out.
                """
                time_read_duration = time.time() - time_read_start
                if time_read_duration > READ_BODY_TIMEOUT_S:
                    raise TimeoutError("Failed to retrieve full message. ")

            result += chunk
            result_size -= len(chunk)

        return result


# Main function
def main():
    pass
    # socket = OpenSocket(host='127.0.0.1', port=4435)
    # socket.send('''python("cmds.polySphere()")''')

    # link = LiveLink(host='127.0.0.1', port=13290)
    # link.link_called.connect(print_string)
    # link.start()

    # socket = OpenSocket(host='localhost', port=55000)
    # socket.send('''exec('print("hello")')''')

    s = OpenSocket(host='127.0.0.1', port=55100)
    s.send('unreal.log("Hello Djed...")')



if __name__ == '__main__':
    
    main()
    
