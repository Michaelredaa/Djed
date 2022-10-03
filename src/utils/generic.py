# -*- coding: utf-8 -*-
"""
Documentation:
"""
import time


def wait_until(somepredicate, timeout, period=0.25, **kwargs):
    mustend = time.time() + timeout
    while time.time() < mustend:
        if somepredicate(**kwargs):
            return True
        time.sleep(period)
    return False


if __name__ == '__main__':
    print(__name__)
