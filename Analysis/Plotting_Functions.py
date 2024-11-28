import matplotlib.pyplot as plt
import csv
import numpy as np
import pandas as pd

def mean_error(x, x_pred):
    mse = np.mean((x - x_pred) ** 2)
    return mse

def ProcessDataFrame(gameSaveLocation):
    """
    Function to remove columns containing unnecessary information about the wrong dataType.
    @PARAM: SaveGameLocation - Path to stored csv
    """
    # data_info = pd.read_csv(gameSaveLocation, nrows=1)
    headers_df = np.loadtxt(gameSaveLocation, delimiter=',', max_rows=4, dtype=str)
    headers_df = pd.DataFrame(headers_df)
    simulatedDF = pd.read_csv(gameSaveLocation, delimiter=',',skiprows=5)
    columns_to_delete = []
    time_column = []
    for i in range(simulatedDF.shape[1]):
        if headers_df.iloc[3,i] == 'frame':
            columns_to_delete.append(i)
        if (headers_df.iloc[3,i] == 'Time'
            or headers_df.iloc[3,i] == 'time'):
            time_column = simulatedDF.iloc[:,i]
            columns_to_delete.append(i)
    simulatedDF.drop(simulatedDF.columns[columns_to_delete], axis=1, inplace=True)
    return simulatedDF, time_column


def get_euc_dist(pos1, pos2):
    '''
    Function to find the euclidian distance between two points
    '''
    return abs(np.linalg.norm(pos2 - pos1))

def get_y_x_displacements(data, marknums):
    '''
    Returns two arrays with y and x displacement relative to vertical and starting positition relatively
    @PARAM: data - data of marker position in a pandas dataframe
    @PARAM: markernums - array of form [x marker number, y marker number]
    '''
    relative_xs = []
    relative_ys = []
    x_num = marknums[0]
    y_num = marknums[1]
    xrows = data.iloc[:,3*x_num-3:3*x_num].to_numpy()
    yrows = data.iloc[:,3*y_num-3:3*y_num].to_numpy()

    x_start = data.iloc[0,3*x_num-3:3*x_num].to_numpy()    

    for xrow, yrow in zip(xrows, yrows):
        rel_y = get_euc_dist(xrow + [0, 0, 0.49], yrow) -0.06
        if abs(rel_y) < 0.005:
            x_start = xrow
        relative_xs.append(get_euc_dist(x_start, xrow))
        relative_ys.append(rel_y)

    return relative_xs, relative_ys
    

def plot_y_x_displacement(xs, ys, times):
    '''
    plots y displacement agains x movement, takes in arrays with displacements
    '''
    plt.plot(times, xs, label='x', color='blue', linestyle='--')  # First dataset
    plt.plot(times, ys, label='y', color='red', linestyle='-')    # Second dataset

    # Add labels and legend
    plt.xlabel('Time (s)')
    plt.ylabel('Displacement (m)')
    plt.title('y displacement and x displacement from equilibrium')
    plt.legend()

    # Show the plot
    plt.show()

if __name__ == "__main__":
    datalocation = 'OptiTrackPipeline/test_lib_streamAndRenderDataWorkflows/TFunction2024_11_18_16_07.csv'
    dataframe, times = ProcessDataFrame(datalocation)
    rel_xs, rel_ys = get_y_x_displacements(dataframe, [3,4])
    plot_y_x_displacement(rel_xs, rel_ys, times)