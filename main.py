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

HELMET_TAG = os.getenv('HELMET_MAC_ADDRESS').lower()

JITTER_THRESHOLD = 30
HIT_COOLDOWN_MS = 100
IMPACT_THRESHOLD = int(os.getenv('IMPACT_THRESHOLD', 1900)) #threshold for abs magnitude to determine an impact
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
        self.target_ind = target_ind

    def on_update(self, feature, sample):
        self.target_arr[self.target_ind] = sample._data

class HelmManager(ManagerListener):
    def __init__(self, target_addr):
        super().__init__()
        self.target_addr = target_addr

    def on_discovery_change(self, manager, enabled):
        print('Discovery %s.' % ('started' if enabled else 'stopped'))
        if not enabled:
            print()

    def on_node_discovered(self, manager, node):
        print('New device discovered: %s.' % (node.get_tag()))

        if node.get_tag().lower() == self.target_addr:
            print("target helm discovered")

class MyNodeListener(NodeListener):
    def on_connect(self, node):
        print('Device %s connected.' % (node.get_name()))

    def on_disconnect(self, node, unexpected=False):
        print('Device %s disconnected%s.' % \
            (node.get_name(), ' unexpectedly' if unexpected else ''))
        if unexpected:
            # Exiting.
            print('\nBluetooth device exiting...\n')

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
    manager_listener = HelmManager(HELMET_TAG)
    manager.add_listener(manager_listener)

    manager.discover(15)

    discovered = manager.get_nodes()

    found = False
    helm = None

    if not discovered:
        raise SystemError('error: no devices found')


    for device in discovered:
        if device.get_tag().lower() == HELMET_TAG:
            print('helmet found!')
            found = True
            helm = device
            break

    if not found or helm is None:
        raise SystemError('error: helmet not found')

    print('connecting to helmet')

    helm_listener = MyNodeListener()
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

    accelerometer.add_listener(AGFeatureListener(curr_impact, 0))
    gyroscope.add_listener(AGFeatureListener(curr_impact, 1))

    helm.enable_notifications(accelerometer)
    helm.enable_notifications(gyroscope)

    while not stop_event.is_set():
        #wait for notification
        if helm.wait_for_notifications(0.5):
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
                curr_impact[0] = None
                curr_impact[1] = None
    #cleanup
    print("removing listener")
    manager.remove_listener(manager_listener)



def controller():
    round_end = time.time() + int(os.getenv("ROUND_TIME", 180))
    has_dropped = False
    prev_impact = None
    prev_prev_impact = None

    prev_logged_hit = 0

    while not stop_event.is_set() and time.time() < round_end:
        try:
            cur_impact = impact_queue.get(timeout=130)

            last_hit = 0

            if prev_impact is not None and (prev_impact.magnitude - cur_impact.magnitude) > JITTER_THRESHOLD:
                has_dropped = True


            

            if prev_prev_impact is not None and prev_impact is not None:
                if prev_impact.magnitude > prev_prev_impact.magnitude and prev_impact.magnitude > cur_impact.magnitude:
                    curr = time.time_ns()
                    elapsed_ms = (curr - last_hit) / 1_000_000
                    if prev_impact.magnitude > IMPACT_THRESHOLD and has_dropped and elapsed_ms > HIT_COOLDOWN_MS:
                        print('yay sent (peak detected)!')
                        helmHandler.add_impact_data(prev_impact)
                        has_dropped = False
                        last_hit = curr

            prev_prev_impact = prev_impact
            prev_impact = cur_impact

        except Exception as e:
            print('controller thread Exception:', e)
            print('stopping idle controller')
            stop_event.set()

    print('session ended')

    if not stop_event.is_set():
        print('controller killed thread')
        stop_event.set()

    helmHandler.end_session()


controller_t = threading.Thread(target=controller)
bt_thread = threading.Thread(target=bluetooth_worker)

controller_t.start()
bt_thread.start()

bt_thread.join()
controller_t.join()
print('done!')