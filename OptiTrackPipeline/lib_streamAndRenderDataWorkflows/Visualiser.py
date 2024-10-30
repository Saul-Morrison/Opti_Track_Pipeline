

import matplotlib.pyplot as plt
import copy
import time
import numpy as np
from datetime import datetime
from pyquaternion import quaternion
import matplotlib.animation as animation
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.widgets import CheckButtons as cb
from pyquaternion import Quaternion


class Visualiser:
    def __init__(self, DataHandler):
        self.Data = DataHandler
        self.Data.CreateMocapData()

    def DefineVisibleButtons(self):
        """
        Function Defines the labels for visible Buttons
        """
        VisibleVectors = {}
        for skeleton in self.Data.SkeletonData.skeleton_list:
            VisibleVectors[skeleton.id_num] = True
        for rigid_body in self.Data.RigidBodyData.rigid_body_list:
            VisibleVectors[rigid_body.id_num] = True
        for skeleton_set in self.Data.SkeletonMarkerSet.marker_data_list:
            VisibleVectors[skeleton_set.model_name] = True
        for rigid_body_set in self.Data.RigidBodyMarkerSet.marker_data_list:
            VisibleVectors[rigid_body_set.model_name] = True
        return VisibleVectors

    def GetOffSetsAndQuarts(self, VisibleVectors):
        """
        Function pulls offsets and quaternions from Data
        """
        offsets = np.empty((0, 3))
        rots = np.empty((0,4))
        for skeleton in self.Data.SkeletonData.skeleton_list:
            if VisibleVectors[skeleton.id_num]:
                for bone in skeleton.rigid_body_list:
                    offsets = np.vstack((offsets, bone.pos))
                    rots = np.vstack((rots, bone.rot))
        for rigid_body in self.Data.RigidBodyData.rigid_body_list:
            if VisibleVectors[rigid_body.id_num]:
                offsets = np.vstack((offsets, rigid_body.pos))
                rots = np.vstack((rots, rigid_body.rot))
        for skeleton_set in self.Data.SkeletonMarkerSet.marker_data_list:
            if VisibleVectors[skeleton_set.model_name]:
                for pos in skeleton_set.marker_pos_list:
                    offsets = np.vstack((offsets, pos))
        for rigid_body_set in self.Data.RigidBodyMarkerSet.marker_data_list:
            if VisibleVectors[rigid_body_set.model_name]:
                for pos in rigid_body_set.marker_pos_list:
                    offsets = np.vstack((offsets, pos))
        return offsets, rots
    
    def ToggleVectors(self, label):
        self.VisibleVectors[label] = not self.VisibleVectors[label]
        
    def transformQuiver(self, quaternions, vectors):
        """
        Function transforms quaternions and returns 3D rotation vectors.
        """
        rotated_vectors = np.empty((0,3))
        for i in range(quaternions.shape[0]):
            quaternion = Quaternion(quaternions[i])
            rotated_vector = quaternion.rotate(vectors[i])
            rotated_vectors = np.vstack((rotated_vectors, rotated_vector))
        return np.array(rotated_vectors)

    def visualiseVectorsFrom3DarrayAnimation(self, RelativeView=False, record=False):

        
        # Access the shared memory and get initial values
        self.Data.AccessSharedMem()
        self.Data.CreateMocapData()
        self.Data.UpdateMocapData()
        self.VisibleVectors = self.DefineVisibleButtons()
        offsets, quaternions = self.GetOffSetsAndQuarts(self.VisibleVectors)
        start_time = datetime.now()
        frequency = 0

        if record:
            self.Data.RecordHeaderToCSV()

        # Set up the check buttons for visualisation
        check_axes = plt.axes([0.01, 0.02, 1, 0.5])  # Adjust position as needed
        check = cb(check_axes, list(self.VisibleVectors.keys()), self.VisibleVectors.items())
        check.on_clicked(self.ToggleVectors)

        # Set Reference Vectors
        initial_vectors_start = np.zeros(shape=offsets.shape)
        reference_vectors = initial_vectors_start
        reference_vectors[:,0] = np.ones((offsets.shape[0]))

        def get_arrows(offsets, quaternions, ref_vectors = reference_vectors):
            rotated_vectors = self.transformQuiver(quaternions=quaternions, vectors=ref_vectors)
            if RelativeView:
                x = 0
                y = 0
                z = 0
            else:
                x = offsets[:, 0]
                y = offsets[:, 1]
                z = offsets[:, 2]
            u = rotated_vectors[:, 2]
            v = rotated_vectors[:, 1]
            w = -1 * rotated_vectors[:, 0]
            return x,y,z,u,v,w
        

        def update_graph(num):

            frame_start = time.perf_counter()

            self.Data.UpdateMocapData()
            offsets, quaternions = self.GetOffSetsAndQuarts(self.VisibleVectors)
            


            self.quiver.remove()
            self.quiver = ax.quiver(*get_arrows(offsets=offsets, quaternions=quaternions, ref_vectors=reference_vectors), length=50, normalize=True)
            frame_end = time.perf_counter()
            title.set_text(f'Plotting markers, time={num}\nFrame Frequency = {1/(frame_end-frame_start):.2f}')
           


        # set up the figure
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        title = ax.set_title('Plotting rigid bodies')
        if RelativeView:
            ax.axes.set_xlim3d(left=-1, right=1) 
            ax.axes.set_ylim3d(bottom=-1, top=1) 
            ax.axes.set_zlim3d(bottom=-1, top=1) 
        else:
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

    # def visualise2DDataFrom3DarrayAnimation(self):

    #     self.data.AccessSharedMem()
        

    #     def update_graph(num,):
    #     # function to update location of points frame by frame
    #         df = pd.DataFrame(self.shared_array) 
    #         #print(df)
    #         graph._offsets3d = (df[2], df[0], df[1])
    #         title.set_text('Plotting markers, time={}'.format(num))

    #     # set up the figure
    #     fig = plt.figure()
    #     ax = fig.add_subplot(111, projection='3d')
    #     title = ax.set_title('Plotting markers')
    #     ax.axes.set_xlim3d(left=-10, right=10) 
    #     ax.axes.set_ylim3d(bottom=-10, top=10) 
    #     ax.axes.set_zlim3d(bottom=-10, top=10) 

    #     # plot the first set of data
    #     graph = ax.scatter(df[2], df[0], df[1])

    #     # set up the animation
    #     ani = animation.FuncAnimation(fig, update_graph, 1200, 
    #                                 interval=8, blit=False)

    #     plt.show()

