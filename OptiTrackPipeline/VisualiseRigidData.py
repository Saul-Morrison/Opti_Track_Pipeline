import sys
sys.path.append("c:/users/saulm/appdata/local/programs/python/python310/lib/site-packages")
import argparse
from lib_streamAndRenderDataWorkflows.DataHandler import DataHandler
from lib_streamAndRenderDataWorkflows.Visualiser import Visualiser
import argparse

parser = argparse.ArgumentParser(description="A script to demonstrate command line arguments.")
parser.add_argument('--record', action='store_true', help='Enable the record feature.')
parser.add_argument('--relativeview', action='store_true', help='Enable the relative view feature.')

# Parse the arguments
args = parser.parse_args()


Charlie_Demo = DataHandler(SharedMemName='Motive Dump')
Animator = Visualiser(Charlie_Demo)

if __name__ == "__main__":
    Animator.visualiseVectorsFrom3DarrayAnimation(RelativeView=args.relativeview, record=args.record)
    #Charlie_Demo.visualise2DDataFrom3DarrayAnimation()