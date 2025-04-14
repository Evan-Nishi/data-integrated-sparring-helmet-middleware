import time
import random

from routes import dbSession

import matplotlib.pyplot as plt

import time
import random

from impact import impact

def perf_test(spacing, queries):
    '''
    spacing(int) : ms spacing between queries
    queries(int) : number of queries
    '''
    test_session = dbSession(1)
    success = 0

    test_session.start_session()

    req_time = []

    total_s = time.time()

    try:
        for i in range(queries):

            start = time.time()
            test_impact = impact(
                x=random.randint(0, 2000),
                y=random.randint(0, 2000),
                z=random.randint(0, 2000),
                gx=random.randint(0, 2000),
                gy=random.randint(0, 2000),
                gz=random.randint(0, 2000)
            )
            success += test_session.add_impact_data(
                test_impact
            )
            end = time.time()

            req_time.append(end - start)

            time.sleep(spacing/1000)

    finally:
        test_session.end_session()

    avg_time = sum(req_time) / len(req_time) if req_time else 0
    print("average time:", 1000 * avg_time,'ms')
    print("success rate:", success/queries * 100,'%')
    print("total time:", time.time() - total_s,'s')
    plot_request_times(req_time=req_time, spacing=spacing)

    

#success rate, average time to query, query_time[0], query_time[1] ... query_time[n]
def log_performance(success, average, query_time):
    try:
        with open("./logs/performance_log.txt", "a") as file:
            query_times_str = ",".join(map(str, query_time))
            file.write(f"{success},{average},{query_times_str}\n")
    except:
        print("performance log failed to write")


def plot_request_times(req_time, spacing):
    plt.figure(figsize=(10, 5))
    plt.plot(req_time, color='red')
    plt.title(f'Request Time per Query, {spacing}ms between requests')
    plt.xlabel("Query Number")
    plt.ylabel("Time (seconds)")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

perf_test(10,1000)