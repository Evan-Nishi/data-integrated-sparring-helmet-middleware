import csv
import time


class Logger:
    def __init__(self, fname, headers):
        if headers[0] != 'ms':
            headers.insert(0, 'ms')

        
        self.fname = fname
        self.log = open(fname, mode='w', newline='')
        self.writer = csv.writer(self.log)
        self.writer.writerow(headers)

        self.start = time.time()

    def log_entry(self, row):
        row.insert(0, 1000 * (time.time() - self.start))
        self.writer.writerow(row)

    def close(self):
        self.log.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
