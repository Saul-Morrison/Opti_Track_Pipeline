from lib_streamAndRenderDataWorkflows.DataStreamer import DataStreamer
import argparse
import time

parser = argparse.ArgumentParser(description="A script to demonstrate command line arguments.")

parser.add_argument("--simulate", type=str, default=None, help="Argument to Simulate data from csv")
parser.add_argument("--timeout", type = float, default = 1000, help="Argument to set timeout for simulation")
args = parser.parse_args()

gameSaveLocation = args.simulate
# gameSaveLocation = 'OptiTrackPipeline/test_lib_streamAndRenderDataWorkflows/GameTest12024_12_03_13_48.csv'
timeout = args.timeout
streamer = DataStreamer(SharedMemoryName='Motive Dump')

if __name__ == "__main__":
    if gameSaveLocation is not None:
        streamer.SimulateLiveData(gameSavelocation=gameSaveLocation, timeout=timeout)
    else:
        streamer.FetchLiveData()

