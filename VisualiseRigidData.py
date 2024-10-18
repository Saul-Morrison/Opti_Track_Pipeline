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

def visualise2DDataFrom3DarrayAnimation(sharedMemoryName = None,noDataTypes = None, varsPerDataType = None):

    # access the shared memory    
    dataEntries = varsPerDataType * noDataTypes
    SHARED_MEM_NAME = sharedMemoryName
    shared_block = shared_memory.SharedMemory(size= dataEntries * 8, name=SHARED_MEM_NAME, create=False)
    shared_array = np.ndarray(shape=(noDataTypes,varsPerDataType), dtype=np.float64, buffer=shared_block.buf)

    # load the most recent shared memory onto a dataframe
    df = pd.DataFrame(shared_array)

    def update_graph(num):
        # function to update location of points frame by frame
        df = pd.DataFrame(shared_array) 
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

def transformQuiver(quaternions, vectors):
    rotated_vectors = []
    for i in range(quaternions.shape[1]):
        quaternion = Quaternion(quaternions[:,i])
        rotated_vector = quaternion.rotate(vectors[:,i])
        rotated_vectors.append(rotated_vector)
    print(np.array(rotated_vectors).shape)

    return np.transpose(np.array(rotated_vectors))


def visualiseVectorsFrom3DarrayAnimation(sharedMemoryName = None,noDataTypes = None, varsPerDataType = None):

    # access the shared memory    
    dataEntries = varsPerDataType * noDataTypes
    SHARED_MEM_NAME = sharedMemoryName
    shared_block = shared_memory.SharedMemory(size= dataEntries * 8, name=SHARED_MEM_NAME, create=False)
    shared_array = np.ndarray(shape=(noDataTypes,varsPerDataType), dtype=np.float64, buffer=shared_block.buf)

     # extract quaternions and offsets from dataframe
    df = pd.DataFrame(shared_array)
    offsets = np.array([df[2], df[0], df[1]])
    quaternions = np.array([df[3],df[4],df[5],df[6]])
    print(offsets.shape, quaternions.shape)

     # initialise reference vectors
    initial_vectors_start = np.zeros(shape=offsets.shape)
    reference_vectors = initial_vectors_start
    reference_vectors[0,:] = np.ones((offsets.shape[1]))

    # load the most recent shared memory onto a dataframe
    

    def get_arrows(offsets, quaternions, ref_vectors = reference_vectors):
        rotated_vectors = transformQuiver(quaternions=quaternions, vectors=ref_vectors)
        x = offsets[0]
        y = offsets[1]
        z = offsets[2]
        u = offsets[0]+rotated_vectors[0]
        v = offsets[1]+rotated_vectors[1]
        w = offsets[2]+rotated_vectors[2]
        return x,y,z,u,v,w

    def update_graph(num, offsets, ref_vectors):
        # function to update location of points frame by frame
        df = pd.DataFrame(shared_array) 
        print(df)
        # extract quaternions and offsets from dataframe
        offsets = np.array([df[2], df[0], df[1]])
        quaternions = np.array([df[3],df[4],df[5],df[6]])
        
        title.set_text('Plotting markers, time={}'.format(num))
        global quiver
        quiver.remove()
        quiver = ax.quiver(*get_arrows(offsets=offsets, quaternions=quaternions, ref_vectors=reference_vectors), length=1, normalize=True)


   
    # set up the figure
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    title = ax.set_title('Plotting rigid bodies')
    ax.axes.set_xlim3d(left=-3, right=0) 
    ax.axes.set_ylim3d(bottom=-2, top=2) 
    ax.axes.set_zlim3d(bottom=-2, top=2) 

    # plot the first set of data
    rotated_vectors = transformQuiver(quaternions=quaternions, vectors=reference_vectors)
    quiver = ax.quiver(*get_arrows(offsets=offsets, quaternions=quaternions, ref_vectors=reference_vectors),length=1, normalize=True)

    # set up the animation
    ani = animation.FuncAnimation(fig, update_graph, 1200, 
                                interval=8, blit=False)

    plt.show()


if __name__ == "__main__":
    # visualiseVectorsFrom3DarrayAnimation(sharedMemoryName= 'Motive Dump',noDataTypes=25,varsPerDataType=7)
    visualise2DDataFrom3DarrayAnimation(sharedMemoryName= 'Motive Dump',noDataTypes=41,varsPerDataType=3)