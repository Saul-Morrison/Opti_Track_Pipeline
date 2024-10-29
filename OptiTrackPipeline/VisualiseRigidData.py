from lib_streamAndRenderDataWorkflows.DataHandler import DataHandler
from lib_streamAndRenderDataWorkflows.Visualiser import Visualiser
import argparse

parser = argparse.ArgumentParser(description="A script to demonstrate command line arguments.")
parser.add_argument('--record', action='store_true', help='Enable the specific feature.')

# Parse the arguments
args = parser.parse_args()

if args.record:
    record = True
else:
    record = False


Charlie_Demo = DataHandler(SharedMemName='Motive Dump')
Animator = Visualiser(Charlie_Demo)

if __name__ == "__main__":
    Animator.visualiseVectorsFrom3DarrayAnimation(RelativeView=False, record=record)
    #Charlie_Demo.visualise2DDataFrom3DarrayAnimation()