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
    def __init__(self, Shared_Memory_Name