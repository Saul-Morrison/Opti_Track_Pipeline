import sys
sys.path.append("C:/users/saulm/appdata/local/programs/python/python310/lib/site-packages")
import argparse
from lib_streamAndRenderDataWorkflows.DataHandler import DataHandler
import time

parser = argparse.ArgumentParser(description="A script to demonstrate command line arguments.")
parser.add_argument('--timeout', type=float, default=100, help="recording time period")
parser.add_argument('--game', action='store_true', default=False, help='If used, game will stop when pole has fallen')

args = parser.parse_args()

data = DataHandler(SharedMemName='Motive Dump')

data.AccessSharedMem()
data.CreateMocapData()
data.RecordHeaderToCSV()


for j in range(5):
    print('Count Down: ', 5-j)
    time.sleep(1)

start_t = time.perf_counter()
i = 1

while __name__ == "__main__":
    frame_start = time.perf_counter()
    while True:
        if time.perf_counter() - frame_start >= 0.008:
            break
    data.UpdateMocapData()
    data.RecordLineToCSV(time.perf_counter() - start_t, i)
    if not data.CheckFallen():
        print(f'Time of: {time.perf_counter() - start_t}')
        break
    i += 1
    if time.perf_counter() - start_t > args.timeout:
        break