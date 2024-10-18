from lib_streamAndRenderDataWorkflows.DataStreamer import DataStreamer
import numpy as np
import pandas as pd
import time

gameSaveLocation = "test_lib_streamAndRenderDataWorkflows\charlie_suit_and_wand_demo.csv"
data = np.loadtxt(gameSaveLocation, delimiter=',',skiprows=7)
simulatedDF = pd.DataFrame(data)


streamer = DataStreamer(SharedMemoryName='MotiveDump', dataType='Bone', noDataTypes=51)
streamer.SimulateLiveData(simulatedDF, timeout = 20.000)
print(streamer.shared_block)