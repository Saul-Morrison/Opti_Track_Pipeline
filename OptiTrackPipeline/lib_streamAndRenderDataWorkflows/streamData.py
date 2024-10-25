"""
This file contains the functionality to stream live data from the motive computer and store in shared memory
There is also functionality to simulate streaming data

"""
# import python specific libraries
import os
import sys
import pandas as pd
import numpy as np
from multiprocessing import shared_memory
import atexit
import time
from lib_streamAndRenderDataWorkflows import quaternions

sys.path.insert(0,'C:\Users\saulm\OneDrive\cambridge\IIB\IIB Project - Augmented Reality\Opti_Track_Pipeline/')

import lib_streamAndRenderDataWorkflows.Client.NatNetClient as NatNetClient
import lib_streamAndRenderDataWorkflows.Client.DataDescriptions as DataDescriptions
import lib_streamAndRenderDataWorkflows.Client.MoCapData as MoCapData
import lib_streamAndRenderDataWorkflows.Client.PythonSample as PythonSample
from lib_streamAndRenderDataWorkflows.config_streaming import *
bodyType_ = None

# define some constants


# function defs below


def fetchLiveData(sharedArray, sharedBlock, simulate = False,simulatedDF = None, timeout = 20.000):
    """
    This function is designed to run continuously in the background and simulates the client which fetches
    data from motive and dumps it in shared memory.
    """

    if simulate and simulatedDF is None:
        raise Exception("Simulated Dataframe data not provided but the fetch live data simulator is called")

    if simulate:
        # this will simulate the process of retrieving live data by retrieving the frame corresponding to the current timestamp 

        is_looping = True
        t_start = time.time()

        while is_looping:
            timestamp = float('%.3f'%(time.time() - t_start))
            if timestamp > timeout:
                is_looping = False
                sharedBlock.close()
                break

            # dump latest data into shared memory
            for i in range(0,simulatedDF.shape[0]):
                timestamp = float('%.3f'%(time.time() - t_start))
                dumpFrameDataIntoSharedMemory(simulate=True, simulatedDF= simulatedDF, frame = i, sharedMemArray=sharedArray)
                time.sleep(0.008) # change this later
                print("Dumped Frame {} into shared memory".format(i))
                print(sharedArray)

            


    else: # functionality for fetching actual data off motive
        
        PythonSample.fetchMotiveData(shared_array_pass=sharedArray, shared_block_pass=sharedBlock)
        


def defineSharedMemory(sharedMemoryName = 'Motive Dump',dataType = 'Bone Marker',noDataTypes = 3, simulate = True,bodyType = None):
    """
    Initialise shared memory

    @PARAM: sharedMemoryName - name to initialise the shared memory
    @PARAM: dataType - type of marker being looked at - e.g. Bone, Bone Marker
    @PARAM: noDataTypes - number of each type of marker, e.g. if bone marker selected then in an
    upper skeleton there are 25
    """
    global bodyType_
    bodyType_ = bodyType # either labeled_marker, rigid_body, skeleton or marker_set
    if simulate:

        varsPerDataType = None
        if dataType == "Bone Marker":
            varsPerDataType = 3 # doesn't have rotations, only x,y,z
        elif dataType == "Bone":
            varsPerDataType = 7 # 4 rotations and 3 positions
        dataEntries = varsPerDataType * noDataTypes # calculate how many data entries needed for each timestamp

        SHARED_MEM_NAME = sharedMemoryName
        try:
            shared_block = shared_memory.SharedMemory(size= dataEntries * 8, name=sharedMemoryName, create=True)
        except FileExistsError:
            Warning(FileExistsError)
            userInput = input("Do you want to instead use the existing shared memory, Saying anything other than y will end the program? - y/n ")
            if userInput == "y":
                shared_block = shared_memory.SharedMemory(size= dataEntries * 8, name=sharedMemoryName, create=False)
            else:
                raise Exception(FileExistsError)
        shared_array = np.ndarray(shape=(noDataTypes,varsPerDataType), dtype=np.float64, buffer=shared_block.buf)

    else:
        pass
    return shared_block,shared_array
    


def dumpFrameDataIntoSharedMemory(simulate = False,simulatedDF = None,frame = 0,sharedMemArray = None,mocapData = None,quaternionsUnit = None,preprocessedSharedArray = False):
    if simulate:
        if preprocessedSharedArray:
            rowData =np.array(simulatedDF.iloc[frame,:][0:])
        else:
            rowData = simulatedDF.iloc[frame,:][2:]
        lengthRowData = rowData.shape[0]
        noTypes,noDims = sharedMemArray.shape
        if preprocessedSharedArray: 
            noDims = 6
        count = 0
        i = 0
        while count < lengthRowData:
            for j in range(0,noDims):
                sharedMemArray[i][j] = rowData[count+j]
            i += 1
            count += noDims
    else:

        #print("Program brought into this loop")
        # first extract all components of mocap data

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
    



    





def retrieveSharedMemoryData(sharedMemoryName = 'MotiveDump'):
    pass

def extractDataFrameFromCSV(dataLocation,includeCols = 'Bone Marker',preprocessed = True):
    """
    @PARAM: dataLocation: relative path to csv data
    @PARAM: includeCols: Includes columns of a specific type, e.g. Bone, Bone Marker

    RETURN: a dataframe 
    """
    if preprocessed is True:
        # extract the experimental data onto a df, test file will check whether 
        # rows skipped will need to be updated in the future
        df = pd.read_csv(dataLocation,skiprows=[0,1,4],header = None)

        # the first row contains the type of each marker, i.e. marker/bone etc.
        markerType = df.iloc[0].values
        # the second row has the names of each part so extract this
        bodyParts = df.iloc[1].values
        # extract the kinematic nature of each column (rotation or position)
        kinematicType = df.iloc[2].values
        # extract the variable in fourth row
        kinematicVariable = df.iloc[3].values

        # create a header array to store a simplified header for each column
        headerArray = []
        headerArray.append('Frame')
        headerArray.append('Time (Seconds)')
        
        # create an index to find when to truncate column
        colStartTruncateIndex = None
        colEndTruncateIndex = None


        for i in range(2,df.shape[1]):
            currHeader = bodyParts[i] + ' ' + kinematicType[i] + ' ' + kinematicVariable[i]
            headerArray.append(currHeader)
            if includeCols == None or includeCols == markerType[i]:
                if colStartTruncateIndex == None:
                    colStartTruncateIndex = i
            elif colStartTruncateIndex is not None and colEndTruncateIndex == None:
                colEndTruncateIndex = i


        # now create dataframe removing the previous rows of metadata and reassigning the
        # column titles

        # include only the frame data
        df = df.iloc[4:]

        # rename columns to a more descriptive label: body part, kinematic type, kinematic variable
        df.columns = headerArray
        df = df.astype(float)
        if includeCols != None:
            df_firstCols = df.iloc[:,:2]
            if colStartTruncateIndex is None: colStartTruncateIndex, colEndTruncateIndex = 0,0
            df = df.iloc[:,colStartTruncateIndex:colEndTruncateIndex]
            df = pd.concat([df_firstCols,df],axis=1)
    else:
        df = pd.read_csv(dataLocation,header = None)
        df = df.iloc[1:,1:]

    return df