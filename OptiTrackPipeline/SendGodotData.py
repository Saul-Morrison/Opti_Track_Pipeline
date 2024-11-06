import sys
sys.path.append("C:/users/saulm/appdata/local/programs/python/python310/lib/site-packages")
import argparse
from lib_streamAndRenderDataWorkflows.DataHandler import DataHandler
from lib_streamAndRenderDataWorkflows import GodotClient, config_streaming
import argparse

parser = argparse.ArgumentParser(description="A script to demonstrate command line arguments.")
parser.add_argument('--HOST', type=str, default='127.0.0.1', help="Arguement for host godot server")
parser.add_argument('--PORT', type=int, default='4242', help="Arguement for godot Port")
parser.add_argument('--record', action='store_true', help='Enable the record feature.')

args = parser.parse_args()

Data = DataHandler(SharedMemName='Motive Dump')

if __name__ == "__main__":
    GodotClient.ConnectToGodot(Data, config_streaming.GameData, HOST=args.HOST, PORT=args.PORT)