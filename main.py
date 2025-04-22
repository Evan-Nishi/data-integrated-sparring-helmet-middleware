import threading
import queue
from routes import dbSession
import os
from dotenv import load_dotenv
import time

import random
from impact import impact

from blue_st_sdk.features.feature_accelerometer import FeatureAccelerometer
from blue_st_sdk.features.feature_gyroscope import FeatureGyroscope

from blue_st_sdk.manager import Manager
from blue_st_sdk.manager import ManagerListener
from blue_st_sdk.node import NodeListener
from blue_st_sdk.feature import FeatureListener

#from analytics.graph_sensor import plot_real_time

#from analytics.log_sensor import Logger


load_dotenv()

HELMET_TAG = os.getenv('HELMET_MAC_ADDRESS')

JITTER_THRESHOLD = 30

IMPACT_THRESHOLD = int(os.getenv('IMPACT_THRESHOLD', 1000)) #threshold for abs magnitude to determine an impact
GYRO_THRESHOLD = int(os.getenv('GYRO_THRESHOLD', 250)) #threshold for gyroscope to determine if head is rotating in a direction

''' if manually grabbing from features
import math

CHARACTERISTIC_MASK = "-0001-11e1-ac36-0002a5d5c51b"


FEATURE_MASKS = {
    f"00800000{CHARACTERISTIC_MASK}": "accelerometer",
    f"00400000{CHARACTERISTIC_MASK}" : "gyroscope",
    f"00020000{CHARACTERISTIC_MASK}" : "battery"
}

'''

impact_queue = queue.Queue()
stop_event = threading.Event()


#single helmet for now, if multiple we can create helmhander and worker for each and set tag for each impact
helmHandler = dbSession()
helmHandler.start_session()


class AGFeatureListener(FeatureListener):
    def __init__(self, target_arr, target_ind):
        super().__init__()
        self.target_arr = target_arr
        self.ind = target_ind

    def on_update(self, feature, sample):
        self.target_arr[self.target_ind] = sample

#for testing only!
def mock_bluetooth_worker():

    #acc_test_logger = Logger('Accelerometer', ['x', 'y', 'z'])
    #gyro_test_logger = Logger('Gyroscope', ['x', 'y', 'z'])

    #plot_real_time(is_acc=True)
    
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
            #acc_test_logger.log([test_impact.x, test_impact.y, test_impact.z])
            #gyro_test_logger.log([test_impact.gx, test_impact.gy, test_impact.gz])

            impact_queue.put(test_impact)
            print("added to queue, m:", test_impact.magnitude)
            time.sleep(random.randint(1,4))
    print('done sending data!')
    stop_event.set()


def bluetooth_worker():
    manager = Manager.instance()
    manager_listener = ManagerListener()
    manager.add_listener(manager_listener)

    manager.discover(20)
    discovered = manager.get_nodes()

    found = False
    helm = None

    if not discovered:
        raise SystemError('error: no devices found')
    for device in discovered:
        if device.get_tag() == HELMET_TAG:
            print('helmet found!')
            found = True
            helm = device
            break

    if not found or helm is None:
        raise SystemError('error: helmet not found')
    
    print('connecting to helmet')

    helm_listener = NodeListener()
    helm.add_listener(helm_listener)

    if not helm.connect():
        print('connection failed')
        raise SystemError('error: found but not connect to helmet')

    features = helm.get_features()

    gyroscope = None
    accelerometer = None

    for feature in features:
        if isinstance(feature, FeatureGyroscope):
            print('gyroscope found!')
            gyroscope = feature
        elif isinstance(feature, FeatureAccelerometer):
            print('accelerometer found')
            accelerometer = feature

        if gyroscope is not None and accelerometer is not None:
            break


    if gyroscope is None:
        raise SystemError('error: gyroscope not found')
    if accelerometer is None:
        raise SystemError('error: accelerometer not found')

    #first should be for accelerometer, second for gyro
    curr_impact = [None, None]

    gyroscope.add_listener(AGFeatureListener(curr_impact, 0))
    gyroscope.add_listener(AGFeatureListener(curr_impact, 1))

    while not stop_event.is_set():
        #wait for notification
        if helm.wait_for_notifications(0.05):
            #if recieved check if payload complete
            if curr_impact[0] is not None and curr_impact[1] is not None:
                #if payload complete, put it in queue to be put to server
                impact_queue.put(impact(
                    x=curr_impact[0][0],
                    y=curr_impact[0][1],
                    z=curr_impact[0][2],
                    gx=curr_impact[1][0],
                    gy=curr_impact[1][1],
                    gz=curr_impact[1][2]
                ))

                curr_impact = [None, None]
        
    #cleanup
    manager.remove_listener(manager_listener)
    


def controller():
    round_end = time.time() + int(os.getenv("ROUND_TIME"))
    has_dropped = True
    prev_mag = 0
    while not stop_event.is_set() and time.time() < round_end:
        try:
            #waits for impact, if no come by timeout end session
            cur_impact = impact_queue.get(timeout=30)
            
            if (prev_mag - cur_impact.magnitude) > JITTER_THRESHOLD:
                has_dropped = True

            #if obj meets threshold, send it off to db!
            if cur_impact.magnitude > IMPACT_THRESHOLD and has_dropped:
                print('yay sent!')
                helmHandler.add_impact_data(cur_impact)

                #make sure that the object is above threshold AND has dropped since last log to prevent multiple logs of same impact
                has_dropped = False

            prev_mag = cur_impact.magnitude
        except:
            print('stopping idle controller')
            stop_event.set()
    print('session ended')
    
    #make sure to signal stop
    if not stop_event.is_set():
        stop_event.set()

    helmHandler.end_session()

controller_t = threading.Thread(target=controller)
bt_thread = threading.Thread(target=mock_bluetooth_worker)

controller_t.start()
bt_thread.start()

bt_thread.join()
controller_t.join()
print('done!')