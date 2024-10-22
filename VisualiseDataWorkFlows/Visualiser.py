"""
Enabling functionality to render data 
"""
import numpy as np
import matplotlib.pyplot as plt    
import matplotlib.animation as animation
from multiprocessing import shared_memory
from mpl_toolkits.mplot3d import Axes3D
import pandas as pd
from pyquaternion import Quaternion

class Visualiser:
    def __init__(self, SharedMemName, NoDataTypes, VarsPerDataType):
        self.SharedMemName = SharedMemName
        self.NoDataTypes = NoDataTypes
        self.VarsPerDataType = VarsPerDataType
        self.dataEntries = VarsPerDataType * NoDataTypes
        self.AccessSharedMem()
    
    def AccessSharedMem(self):
        # access the shared memory    
        self.shared_block = shared_memory.SharedMemory(size= self.dataEntries * 8, name=self.SharedMemName, create=False)
        self.shared_array = np.ndarray(shape=(self.NoDataTypes,self.VarsPerDataType), dtype=np.float64, buffer=self.shared_block.buf)        

    def transformQuiver(self, quaternions, vectors):
        rotated_vectors = []
        for i in range(quaternions.shape[1]):
            quaternion = Quaternion(quaternions[:,i])
            rotated_vector = quaternion.rotate(vectors[:,i])
            rotated_vectors.append(rotated_vector)
        print(np.array(rotated_vectors).shape)
        return np.transpose(np.array(rotated_vectors))
    
    def visualise2DDataFrom3DarrayAnimation(self):

        self.AccessSharedMem()
        # load the most recent shared memory onto a dataframe
        df = pd.DataFrame(self.shared_array)

        def update_graph(num,):
        # function to update location of points frame by frame
            df = pd.DataFrame(self.shared_array) 
            print(df)
            graph._offsets3d = (df[2], df[0], df[1])
            title.set_text('Plotting markers, time={}'.format(num))

        # set up the figure
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        title = ax.set_title('Plotting markers')
        ax.axes.set_xlim3d(left=-1000, right=1000) 
        ax.axes.set_ylim3d(bottom=-1000, top=1000) 
        ax.axes.set_zlim3d(bottom=-1000, top=1000) 

        # plot the first set of data
        graph = ax.scatter(df[2], df[0], df[1])

        # set up the animation
        ani = animation.FuncAnimation(fig, update_graph, 1200, 
                                    interval=8, blit=False)

        plt.show()

    def visualiseVectorsFrom3DarrayAnimation(self):

        # access the shared memory    
        self.AccessSharedMem()

        # extract quaternions and offsets from dataframe
        df = pd.DataFrame(self.shared_array)
        offsets = np.array([df[4], df[5], df[6]])
        quaternions = np.array([df[0],df[1],df[2],df[3]])
        print(offsets.shape, quaternions.shape)

        # initialise reference vectors
        initial_vectors_start = np.zeros(shape=offsets.shape)
        reference_vectors = initial_vectors_start
        reference_vectors[0,:] = np.ones((offsets.shape[1]))

        # load the most recent shared memory onto a dataframe
        

        def get_arrows(offsets, quaternions, ref_vectors = reference_vectors):
            rotated_vectors = self.transformQuiver(quaternions=quaternions, vectors=ref_vectors)
            x = offsets[0]
            y = offsets[1]
            z = offsets[2]
            u = offsets[0]+rotated_vectors[0]
            v = offsets[1]+rotated_vectors[1]
            w = offsets[2]+rotated_vectors[2]
            return x,y,z,u,v,w
        

        def update_graph(num):
            # function to update location of points frame by frame
            df = pd.DataFrame(self.shared_array) 
            print(df)
            # extract quaternions and offsets from dataframe
            offsets = np.array([df[6], df[4], df[5]])
            quaternions = np.array([df[0],df[1],df[2],df[3]])
            
            title.set_text('Plotting markers, time={}'.format(num))

            self.quiver.remove()
            self.quiver = ax.quiver(*get_arrows(offsets=offsets, quaternions=quaternions, ref_vectors=reference_vectors), length=100, normalize=True)


    
        # set up the figure
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        title = ax.set_title('Plotting rigid bodies')
        ax.axes.set_xlim3d(left=-1000, right=1000) 
        ax.axes.set_ylim3d(bottom=-1000, top=1000) 
        ax.axes.set_zlim3d(bottom=-1000, top=1000) 

        # plot the first set of data
        rotated_vectors = self.transformQuiver(quaternions=quaternions, vectors=reference_vectors)
        self.quiver = ax.quiver(*get_arrows(offsets=offsets, quaternions=quaternions, ref_vectors=reference_vectors),length=1, normalize=True)

        # set up the animation
        ani = animation.FuncAnimation(fig, update_graph, 1200, 
                                    interval=8, blit=False)

        plt.show()

