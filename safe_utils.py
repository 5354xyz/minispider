# -*- coding: utf-8 -*-
"""
This file is for good coder.Achieve the mini spider.

Authors: xiaoyizong(xiaoyizong@baidu.com)
Date:    2015/10/08 14:00:06
"""
import thread

def decorate_all(obj):
    """
    decorate_all function to thread safe function
    """
    lock = thread.allocate_lock()
    fnc_names = [fnctn for fnctn in dir(obj) if '__' not in fnctn]
    for name in fnc_names:
        fnc = getattr(obj, name)
        setattr(obj, name, decorate(fnc, lock))
    return obj


def decorate(fnctn, lock):
    """
    decorate  function to thread safe function
    """
    def decorated(*args):
        """decorated with args"""
        lock.acquire()
        try:
            return fnctn(*args)
        finally:
            lock.release()
    return decorated


def thread_safe(superclass):
    """
    outter interface
    """
    lock = thread.allocate_lock()
    class ThreadSafe(superclass):
        """inner safe thead class"""
        def __init__(self, *args, **kwargs):
            """father function"""
            super(ThreadSafe, self).__init__(*args, **kwargs)
    return decorate_all(ThreadSafe)
