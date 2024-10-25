from lib_streamAndRenderDataWorkflows.DataStreamer import DataStreamer
import argparse

parser = argparse.ArgumentParser(description="A script to demonstrate command line arguments.")

parser.add_argument("--simulate", type=str, default=None, help="Argument to Simulate data from csv")
parser.add_argument("--timeout", type = float, default = 20, help="Argument to set timeout for simulation")
args = parser.parse_args()

gameSaveLocation = args.simulate
timeout = args.timeout
streamer = DataStreamer(SharedMemoryName='Motive Dump', dataType='Rigid Body', noDataTypes=1)

if __name__ == "__main__":
    if gameSaveLocation is not None:
        streamer.SimulateLiveData(gameSavelocation=gameSaveLocation, timeout=1000.000 )
    else:
        streamer.FetchLiveData()

