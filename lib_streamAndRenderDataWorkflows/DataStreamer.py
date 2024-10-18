'''
This object streams from motive and puts data into shared memory.
There is also an option to simulate a livestreamed data from motive.
Much of this is taken from Ashwin's StreamData file
'''

import os
import sys
import pandas as pd
import numpy as np
from multiprocessing import shared_memory
import atexit
import time

class DataStreamer:

    def __init__(self, SharedMemoryName = 'motive dump', dataType = 'Bone', noDataTypes = 3):
        """
        Class to stream data and dump into a shared memory
        @PARAM: SharedMemoryName - Name of the shared memory
        @PARAM: dataType - Type of data analysed (Bones have rotations and positions)
        @PARAM: noDataTypes - How many different data types that are recorded (i.g. how many bones)
        """
        self.SharedMemName = SharedMemoryName
        self.dataType = dataType
        self.noDataTypes = noDataTypes
        self.shared_block, self.sharedArray = self.defineSharedMemory()

    def SimulateLiveData(self, simulatedDF, timeout = 20.000):
        """
        Function to simulate live data from a given csv file
        @PARAM: timeout - How long to run the simulation for
        @PARAM: simulatedDF - Dataframe containing each frame with index, time stamp and associated values
        """
        is_looping = True
        t_start = time.time()

        while is_looping:
            timestamp = float('%.3f'%(time.time() - t_start))
            if timestamp > timeout:
                is_looping = False
                self.shared_block.close()
                break

            # dump latest data into shared memory
            for i in range(0,simulatedDF.shape[0]):
                timestamp = float('%.3f'%(time.time() - t_start))
                self.SimulateRowSharedMemoryDump(simulatedDF=simulatedDF, frame = i)
                time.sleep(0.008) # change this later
                if i%100 == 0:
                    print("Dumped Frame {} into shared memory".format(i))
                    print(self.sharedArray)


    def SimulateRowSharedMemoryDump(self, simulatedDF, preprocessedSharedArray = False, frame = 0,):
        """
        Function to dump one row into the shared memory

        @PARAM: simulatedDF - Dataframe containing each frame with index, time stamp and associated values
        @PARAM: preprocessedSharedArray - Change to True if Dataframe does not have index and time stamp for each frame
        @PARAM: frame - Current frame being dumped into shared memory
        """

        if preprocessedSharedArray:
            rowData =np.array(simulatedDF.iloc[frame,:][0:self.varsPerDataType*self.noDataTypes])
        else:
            rowData = simulatedDF.iloc[frame,:][2:2+self.varsPerDataType*self.noDataTypes].reset_index(drop=True)
        lengthRowData = rowData.shape[0]
        noTypes,noDims = self.sharedArray.shape
        if preprocessedSharedArray: 
            noDims = 6
        count = 0
        i = 0
        while count < lengthRowData:
            for j in range(0,noDims):
                self.sharedArray[i][j] = rowData[count+j]
            i += 1
            count += noDims
        
    def defineSharedMemory(self, simulate = True,bodyType = None):
        """
        Initialise shared memory

        @PARAM: sharedMemoryName - name to initialise the shared memory
        @PARAM: dataType - type of marker being looked at - e.g. Bone, Bone Marker
        @PARAM: noDataTypes - number of each type of marker, e.g. if bone marker selected then in an
        upper skeleton there are 25
        """
        if simulate:

            self.varsPerDataType = None
            if self.dataType == "Bone Marker":
                self.varsPerDataType = 3 # doesn't have rotations, only x,y,z
            elif self.dataType == "Bone":
                self.varsPerDataType = 7 # 4 rotations and 3 positions
            dataEntries = self.varsPerDataType * self.noDataTypes # calculate how many data entries needed for each timestamp

            SHARED_MEM_NAME = self.SharedMemName
            try:
                shared_block = shared_memory.SharedMemory(size= dataEntries * 8, name=self.SharedMemName, create=True)
            except FileExistsError:
                Warning(FileExistsError)
                userInput = input("Do you want to instead use the existing shared memory, Saying anything other than y will end the program? - y/n ")
                if userInput == "y":
                    shared_block = shared_memory.SharedMemory(size= dataEntries * 8, name=self.SharedMemName, create=False)
                else:
                    raise Exception(FileExistsError)
            shared_array = np.ndarray(shape=(self.noDataTypes,self.varsPerDataType), dtype=np.float64, buffer=shared_block.buf)

        else:
            pass
        return shared_block,shared_array
        

    def dumpFrameDataIntoSharedMemory(self, simulate = False,simulatedDF = None,frame = 0,sharedMemArray = None,mocapData = None,quaternionsUnit = None,preprocessedSharedArray = False):
        
        # first extract labeled_markers
        global bodyType_
        if bodyType_ == None:
            labeledMarkerData = mocapData.labeled_marker_data.labeled_marker_list
            rigidBodyData = mocapData.rigid_body_data.rigid_body_list
            skeletonData = mocapData.skeleton_data.skeleton_list
            markerSetData = mocapData.marker_set_data.marker_data_list
            if bool(labeledMarkerData):
                bodyType_ = 'labeled_marker'
            elif bool(rigidBodyData):
                bodyType_ = 'rigid_body'
            elif bool(skeletonData):
                bodyType_ = 'skeleton'
            elif bool(markerSetData):
                bodyType_ = 'marker_set'
            else:
                raise Exception("No data recieved")
        elif bodyType_ == 'labeled_marker':
            labeledMarkerData = mocapData.labeled_marker_data.labeled_marker_list
        elif bodyType_ == 'rigid_body':
            rigidBodyData = mocapData.rigid_body_data.rigid_body_list
        elif bodyType_ == 'skeleton':
            skeletonData = mocapData.skeleton_data.skeleton_list
        elif bodyType_ == 'marker_set':
            markerSetData = mocapData.marker_set_data.marker_data_list

        if bodyType_ == 'labeled_marker':
            for marker in labeledMarkerData:
                searchArray = list(sharedMemArray[:,0])
                if marker.id_num not in searchArray:
                    idx = searchArray.index(0)
                    sharedMemArray[idx][0] = marker.id_num
                    sharedMemArray[idx][1:5] = marker.pos
                    colIdx += 1
                elif marker.id_num in searchArray:
                    idx = searchArray.index(marker.id_num)
                    sharedMemArray[idx][0] = marker.id_num
                    sharedMemArray[idx][1:5] = marker.pos

        elif bodyType_ == 'rigid_body':
            pass
        elif bodyType_ == 'skeleton':
            colIdx = 0
            for skeletonIdx in range(0,len(skeletonData)):
                skeleton = skeletonData[skeletonIdx].rigid_body_list
                if False: # default method of pushing all rigid  bodies to shared mem without any processing
                    for rigidBody in skeleton:
                        sharedMemArray[colIdx][0:4] = rigidBody.rot
                        sharedMemArray[colIdx][4:7] = rigidBody.pos
                        colIdx += 1
                
                else:  # feature to stream rigid body data as vectors
                    for i,idx in enumerate(simpleBodyParts):
                        q = quaternions.quaternionVector(loc = list(skeleton[idx].pos),quaternion= [skeleton[idx].rot[3],skeleton[idx].rot[0],skeleton[idx].rot[1],skeleton[idx].rot[2]])
                        vector = q.qv_mult(q.quaternion,quaternionsUnit[i]) 
                        sharedMemArray[idx][0:3] = skeleton[idx].pos
                        sharedMemArray[idx][3:6] = vector
                        #print(sharedMemArray)

        elif bodyType_ == 'marker_set':
            pass



    