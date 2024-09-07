import os 
import sys 

sys.path.append("/home/star/dc-etcd/python-etcd3")

import time 
import threading
import traceback

from concurrent.futures import ThreadPoolExecutor, wait, as_completed

import etcd3

from loguru import logger

logger.remove()

logger.add("my.log")

etcd = etcd3.client()

etcd.get('foo')
etcd.put('bar', 'doot')
etcd.delete('bar')

# locks
lock = etcd.lock('thing')
lock.acquire()
if lock.is_acquired():
    print("lock is acquired.")
else:
    print("failed to acquire lock.")
lock.release()


from threading import Timer

class RepeatTimer(Timer):
    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)


def blocking_func(num):
    LOCK_TTL = 5
    try:
        lock = etcd.lock('my-blocking-lock', ttl=LOCK_TTL)

        def keepalive():
            while True:
                logger.info(lock.lease.remaining_ttl)
                time.sleep(1)
                if lock.lease.remaining_ttl < LOCK_TTL/3:
                    lock.refresh()

        lock.acquire(timeout=None)
        logger.info(f"num: {num}, thread id: {threading.current_thread().ident}, acquired: {lock.is_acquired()}")
        if lock.is_acquired():
            timer = RepeatTimer(1, keepalive)
            timer.daemon = True
            timer.start()
            
            time.sleep(10)

            timer.cancel()
            lock.release()

    except Exception as e:
        logger.error(traceback.format_exc())


def non_blocking_func(num):
    try:
        lock = etcd.lock('my-blocking-lock', ttl=60)
        lock.acquire(timeout=0)
        logger.info(f"num: {num}, thread id: {threading.current_thread().ident}, acquired: {lock.is_acquired()}")
        if lock.is_acquired():
            time.sleep(2)
            lock.release()
            
    except Exception:
        logger.error(traceback.format_exc())


start_ts = time.time()
with ThreadPoolExecutor(2) as executor:
    executor.map(blocking_func, [i for i in range(4)])
    # futures = [executor.submit(blocking_func, i) for i in range(20)]
    # wait(futures)

print(f"total time of blocking: {time.time() -start_ts}")

start_ts = time.time()
with ThreadPoolExecutor(10) as executor:
    executor.map(non_blocking_func, [i for i in range(20)])
print(f"total time of non-blocking: {time.time() -start_ts}")




# def dummyfn(msg="foo"):
#     print(msg)

# timer = RepeatTimer(1, dummyfn)
# timer.start()
# time.sleep(5)
# timer.cancel()
