"""
Enabling functionality to render data 
"""
import numpy as np
from lib_streamAndRenderDataWorkflows import config_streaming
from multiprocessing import shared_memory
import csv
import os
from datetime import datetime
from pyquaternion import Quaternion
from lib_streamAndRenderDataWorkflows.Client import MoCapData

class DataHandler:

    def __init__(self, SharedMemName):
        self.SharedMemName = SharedMemName
        self.DataTypesArray = config_streaming.DataTypesArray
        self.NumTypesArray = config_streaming.NumDataTypesArray
        time = datetime.now()
        time = time.strftime('%Y_%m_%d_%H_%M')
        self.pathtorecord = config_streaming.RecordingPath + str(time) + '.csv'
        self.CalculateArrayShape()
        self.AccessSharedMem()
        self.CreateMocapData()

    def CalculateVarsPerData(self):
        """
        Function determines how many variables there are per datatype (either markers or rigid bodies).
        """
        for DataType in self.DataTypesArray:
            if 'Marker' in DataType:
                return 3
        return 7

    def CalculateArrayShape(self):
        """
        Function to calculate how many different data entries there are.
        Same as number of datatypes multiplied by num of variables per datatype
        """
        self.VarsPerDataType = self.CalculateVarsPerData()
        self.dataEntries = 0
        for Numtypes in self.NumTypesArray:
            self.dataEntries += (Numtypes * self.VarsPerDataType)

    def AccessSharedMem(self):
        """
        Function to access the shared memory.
        """  
        self.shared_block = shared_memory.SharedMemory(size= self.dataEntries * 8, name=self.SharedMemName, create=False)
        self.shared_array = np.ndarray(shape=(sum(self.NumTypesArray),self.VarsPerDataType), dtype=np.float64, buffer=self.shared_block.buf)        

    def transformQuiver(self, quaternions, vectors):
        """
        Function transforms quaternions and returns 3D rotation vectors.
        """
        rotated_vectors = []
        for i in range(quaternions.shape[1]):
            quaternion = Quaternion(quaternions[:,i])
            rotated_vector = quaternion.rotate(vectors[:,i])
            rotated_vectors.append(rotated_vector)
        # print(np.array(rotated_vectors).shape)
        return np.transpose(np.array(rotated_vectors))
    
    def CreateMocapData(self):
        self.SkeletonData = MoCapData.SkeletonData()
        self.RigidBodyData = MoCapData.RigidBodyData()
        self.SkeletonMarkerSet = MoCapData.MarkerSetData()
        self.RigidBodyMarkerSet = MoCapData.MarkerSetData()
        SkeletonCounter = 0
        for DataType, NumTypes in zip(self.DataTypesArray, self.NumTypesArray):
            if DataType == "Bone":
                Skeleton = MoCapData.Skeleton('Skeleton'+str(SkeletonCounter))
                for i in range(NumTypes):
                    id = config_streaming.BodyPartsIDs[i]
                    pos = np.zeros(3)
                    rot = np.zeros(4)
                    RigidBone = MoCapData.RigidBody(id,pos,rot)
                    Skeleton.add_rigid_body(RigidBone)
                SkeletonCounter += 1
                self.SkeletonData.add_skeleton(Skeleton)
            if DataType == "Rigid Body":
                for i in range(NumTypes):
                    id = config_streaming.RigidBodyIDs[i]
                    pos = np.zeros(3)
                    rot = np.zeros(4)
                    RigidBody = MoCapData.RigidBody(id,pos,rot)
                    self.RigidBodyData.add_rigid_body(RigidBody)
            if DataType == "Bone Marker":
                for i in range(NumTypes):
                    id = 'Skeleton'+str(i)+'Markers'
                    pos = np.zeros(3)
                    BoneMarkers = MoCapData.MarkerData()
                    BoneMarkers.model_name=id
                    BoneMarkers.add_pos(pos)
                self.SekeletonMarkerSet.add_marker_data(BoneMarkers)
            if DataType == "Rigid Body Marker":
                for i in range(NumTypes):
                    id = 'Rigid Body'+str(i)+'Markers'
                    pos = np.zeros(3)
                    RigidBodyMarkers = MoCapData.MarkerData()
                    RigidBodyMarkers.model_name = id
                    RigidBodyMarkers.add_pos(pos)
                self.RigidBodyMarkerSet.add_marker_data(RigidBodyMarkers)
    
    def UpdateMocapData(self):
        SkeletonCounter = 0
        RigidBodyCounter = 0
        SkeletonMarkerSetCounter = 0
        RigidBodyMarkerSetCounter = 0
        counter = 0
        for DataType, NumTypes in zip(self.DataTypesArray, self.NumTypesArray):
            if DataType == "Bone":
                for i in range(NumTypes):
                    self.SkeletonData.skeleton_list[SkeletonCounter].rigid_body_list[i].pos = self.shared_array[counter+i][:3]
                    self.SkeletonData.skeleton_list[SkeletonCounter].rigid_body_list[i].rot = self.shared_array[counter+i][3:]
                SkeletonCounter += 1
            elif DataType == "Rigid Body":
                for i in range(NumTypes):
                    self.RigidBodyData.rigid_body_list[RigidBodyCounter].pos = self.shared_array[counter+i][:3]
                    self.RigidBodyData.rigid_body_list[RigidBodyCounter].rot = self.shared_array[counter+i][3:]
                RigidBodyCounter += 1
            elif DataType == "Bone Marker":
                for i in range(NumTypes):
                    self.SkeletonMarkerSet.marker_data_list[SkeletonMarkerSetCounter][i].pos = self.shared_array[counter+i]
                SkeletonMarkerSetCounter += 1
            elif DataType == "Rigid Body Marker":
                for i in range(NumTypes):
                    self.SkeletonMarkerSet.marker_data_list[RigidBodyMarkerSetCounter][i].pos = self.shared_array[counter+i]
                RigidBodyMarkerSetCounter = 0
            counter += NumTypes

    def MakeInfoHeader(self):
        #------------------------------Fill out with format version, etc....--------------------------
        info = []
        return info
        
    def MakeHeaders(self):
        DataTypeHeader = ['','type']
        IDHeader = ['','ID']
        InfoTypeHeader = ['','']
        XYZHeader = ['frame','time']
        SkeletonCounter=0
        RigidBodyCounter=0
        SkeletonMarkerSetCounter = 0
        RigidBodyMarkerSetCounter = 0
        for DataType in self.DataTypesArray:
            if DataType == 'Bone':
                Skeleton = self.SkeletonData.skeleton_list[SkeletonCounter]
                for bone in Skeleton.rigid_body_list:
                    DataTypeHeader += [DataType] * 7
                    IDHeader += [bone.id_num] * 7
                    InfoTypeHeader += ['Rotation','Rotation','Rotation','Rotation','Position','Position','Position']
                    XYZHeader += ['X','Y','Z','W','X','Y','Z']
                SkeletonCounter+=1
            elif DataType == 'Rigid Body':
                DataTypeHeader += [DataType] * 7
                IDHeader += [self.RigidBodyData.rigid_body_list[RigidBodyCounter]] * 7
                InfoTypeHeader += ['Rotation','Rotation','Rotation','Rotation','Position','Position','Position']
                XYZHeader += ['X','Y','Z','W','X','Y','Z']
                RigidBodyCounter += 1
            elif DataType == 'Bone Marker':
                MarkerSet = self.SkeletonMarkerSet.marker_data_list[RigidBodyCounter]
                for marker in MarkerSet:
                    IDHeader += [marker.model_name] * 3
                    DataTypeHeader += [DataType] * 3
                    InfoTypeHeader += ['Position','Position','Position']
                    XYZHeader += ['X','Y','Z']
                SkeletonMarkerSetCounter += 1
            elif DataType == 'Rigid Body Marker':
                MarkerSet = self.RigidBodyMarkerSet.marker_data_list[RigidBodyMarkerSetCounter]
                for marker in MarkerSet:
                    IDHeader += [marker.model_name] * 3
                    DataTypeHeader += [DataType] * 3
                    InfoTypeHeader += ['Position','Position','Position']
                    XYZHeader += ['X','Y','Z']
                SkeletonMarkerSetCounter += 1
        return [DataTypeHeader, IDHeader, InfoTypeHeader, XYZHeader]
    
    def RecordHeaderToCSV(self):
        info = self.MakeInfoHeader()
        fullheader = self.MakeHeaders()
        with open(self.pathtorecord, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(fullheader)
    
    def RecordLineToCSV(self, run_time, num):
        info = self.MakeInfoHeader()
        with open(self.pathtorecord, mode='a', newline='') as file:
            writer = csv.writer(file)
            csv_list = self.shared_array.flatten().tolist()
            csv_list.insert(0,run_time)
            csv_list.insert(0, num)
            writer.writerows([csv_list])