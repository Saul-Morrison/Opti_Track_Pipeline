from lib_streamAndRenderDataWorkflows.DataStreamer import DataStreamer


gameSaveLocation = "test_lib_streamAndRenderDataWorkflows\charlie_suit_and_wand_demo.csv"
streamer = DataStreamer(SharedMemoryName='Motive Dump', dataType='Bone', noDataTypes=51)

if __name__ == "__main__":
    streamer.SimulateLiveData(gameSaveLocation, timeout = 100000)
