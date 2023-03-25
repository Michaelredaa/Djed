# -*- coding: utf-8 -*-
"""
Documentation:
"""

import unreal
import socket
import traceback
from threading import Thread
from queue import Queue


class Timer():
    handle = None

    def __init__(self, fn, delay=0.0, repeat=False):
        self.fn = fn
        self.delay = delay
        self.repeat = repeat
        self.passed = 0.0
        self.handle = unreal.register_slate_post_tick_callback(self.tick)

    def stop(self):
        self.fn = None
        if not self.handle:
            return
        unreal.unregister_slate_post_tick_callback(self.handle)
        self.handle = None

    def tick(self, delta_time):
        if not self.fn:
            self.stop()
            return

        self.passed += delta_time
        if self.passed < self.delay:
            return

        try:
            self.fn()
        except:
            print(traceback.format_exc())

        if self.repeat:
            self.passed = 0.0
        else:
            self.stop()


class UnrealSocket():
    Instance = []

    def __init__(self, host='172.0.0.1', port=55100):
        self.__class__.Instance.append(self)

        self.host = host
        self.port = port

        self.live = False
        self.queue = Queue()

    def start(self):
        if self.live:
            raise RuntimeError
        self.live = True

        try:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._socket.bind((self.host, self.port))
            self._socket.listen(1)
        except Exception as e:
            print(f'Socket error: {(self.host, self.port)}', e)
            print(traceback.format_exc())
            return

        self._thread = Thread(target=self.receive)
        self._thread.start()
        self._timer = Timer(self.execute, delay=0.3, repeat=True, )

    def stop(self):
        self.live = False
        self._timer.stop()
        self._socket.close()

    def receive(self):
        while self.live:
            conn, address = self._socket.accept()
            while self.live:
                data = conn.recv(4096)
                if data:
                    self.queue.put(data)
                    # exec(data.decode())
                else:
                    break

    def execute(self):
        syslib = unreal.SystemLibrary()

        if not self.live:
            return self._timer.stop()

        if not self.queue.qsize():
            return
        data = self.queue.get_nowait()
        cmd = data.decode()
        # syslib.print_string(None, string=cmd, print_to_screen=True, print_to_log=True,
        #                     text_color=[255.0, 255.0, 0.0, 255.0], duration=2.0)
        syslib.execute_console_command(None, cmd)


def __del__(self):
    self.live = False
    self._timer.stop()
    self._socket.shutdown(socket.SHUT_RDWR)
    self._socket.close()


def listen(host="127.0.0.1", port=55100):
    prev = getattr(unreal, "udp_2_cmd_listener", None)
    if prev:
        prev.__del__()

    unreal.udp_2_cmd_listener = UnrealSocket(host, port)
    unreal.udp_2_cmd_listener.start()


if __name__ == '__main__':
    listen()
    print(__name__)
