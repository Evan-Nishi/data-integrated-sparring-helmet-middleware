import csv
import os
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from dotenv import load_dotenv

def plot_real_time(is_acc):
    load_dotenv()

    if is_acc:
        threshold = int(os.getenv('IMPACT_THRESHOLD', 1000))
        fname = 'Accelerometer'
    else:
        threshold = int(os.getenv('GYRO_THRESHOLD', 500))
        fname = 'Gyroscope'

    log_file = f'../logs/{fname}.csv'
    window_size = 200  # show only the latest 200 readings

    timestamps, x_vals, y_vals, z_vals = [], [], [], []

    fig, ax = plt.subplots(figsize=(12, 6))

    def animate(i):
        try:
            with open(log_file) as csvfile:
                reader = csv.DictReader(csvfile)
                rows = list(reader)[-window_size:]  # grab last N rows

                timestamps.clear()
                x_vals.clear()
                y_vals.clear()
                z_vals.clear()

                for row in rows:
                    timestamps.append(float(row['ms']))
                    x_vals.append(float(row['x']))
                    y_vals.append(float(row['y']))
                    z_vals.append(float(row['z']))

            ax.clear()
            ax.plot(timestamps, x_vals, label='X', color='r')
            ax.plot(timestamps, y_vals, label='Y', color='g')
            ax.plot(timestamps, z_vals, label='Z', color='b')
            ax.axhline(y=threshold, color='purple', linestyle='--', label='Threshold')
            ax.axhline(y=-threshold, color='purple', linestyle='--')

            ax.set_xlabel('Time (ms)')
            ax.set_ylabel(f'{fname} raw value')
            ax.set_title(f'{fname} Real-Time Readings')
            ax.legend()
            ax.grid(True)
            plt.tight_layout()
        except Exception as e:
            print(f"[ERROR] Could not update plot: {e}")

    ani = animation.FuncAnimation(fig, animate, interval=500)  # update every 500 ms
    plt.show()
