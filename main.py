import threading
import queue
from routes import dbSession
import os
from dotenv import load_dotenv
import time

import random
from impact import impact

from concurrent.futures import ThreadPoolExecutor, as_completed

load_dotenv()

IMPACT_THRESHOLD = 1000 #threshold for abs magnitude to determine an impact

GYRO_THRESHOLD = 250 #threshold for gyroscope to determine if head is rotating in a direction

impact_queue = queue.Queue()
stop_event = threading.Event()


#single helmet for now, if multiple we can create helmhander and worker for each and set tag for each impact
helmHandler = dbSession()
helmHandler.start_session()

def mock_bluetooth_worker():
    for i in range(10):
        if not stop_event.is_set():
            test_impact = impact(
                x=random.randint(0, 2000),
                y=random.randint(0, 2000),
                z=random.randint(0, 2000),
                gx=random.randint(0, 2000),
                gy=random.randint(0, 2000),
                gz=random.randint(0, 2000)
            )

            impact_queue.put(test_impact)
            print("added to queue, m:", test_impact.magnitude)
            time.sleep(random.randint(1,4))
    print('done sending data!')
    stop_event.set()




def controller():
    round_end = time.time() + int(os.getenv("ROUND_TIME"))
    while not stop_event.is_set() and time.time() < round_end:
        try:
            #waits for impact, if no come by timeout end session
            cur_impact = impact_queue.get(timeout=10)

            #if obj meets threshold, send it off to db!
            if cur_impact.magnitude > IMPACT_THRESHOLD:
                print('yay sent!')
                helmHandler.add_impact_data(cur_impact)
        except:
            print('stopping idle controller')
            stop_event.set()
    print('session ended')
    helmHandler.end_session()

controller_t = threading.Thread(target=controller)
bt_thread = threading.Thread(target=mock_bluetooth_worker)

controller_t.start()
bt_thread.start()

bt_thread.join()
controller_t.join()
print('done!')