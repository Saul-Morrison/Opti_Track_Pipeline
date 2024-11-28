import numpy as np
import matplotlib.pyplot as plt 
import scipy.optimize as scop
from scipy.signal import lsim
import control as ctrl
import os
import copy
from Plotting_Functions import ProcessDataFrame, get_y_x_displacements, mean_error
from scipy.interpolate import interp1d
from scipy.optimize import minimize



class system_identifier():

    def __init__(self, path_to_inital_data, path_to_compare=None, path_to_folder=None):
        self.path_init = path_to_inital_data
        self.path_to_compare = path_to_compare
        self.path_to_folder = path_to_folder
        self.times = np.array([])
        self.folder_path = path_to_folder
        self.K_p = 5
        self.k_d = 3
        self.D = 0.1
        self.cut_off = 0.01
        self.init_xs = np.array([])
        self.init_ys = np.array([])
    
    def show_graph(self, xs, ys, x_pred ,show_MSE=False):

        plt.figure(figsize=(10, 6))
        plt.plot(self.times, xs, label='Measured Output', linewidth=2)
        plt.plot(self.times, np.abs(x_pred), label=f'Fitted Model (K_p={self.K_p:.3f}, D={self.D:.3f}, k_d={self.k_d:.3f}),  cut off={self.cut_off:.5f})', linestyle='--', linewidth=2)
        plt.plot(self.times, ys, label='Original Input', linewidth=2, color='red')
        if show_MSE is not None:
            plt.title(f'Fitted Proportional Delay Model, MSE: {show_MSE}')
        plt.xlabel('Time (s)')
        plt.ylabel('Output')
        plt.legend()
        plt.grid()
        plt.show()

    def quantise_2_datas(self, times1, times2, x1, x2):

        quantised_timestamps = np.arange(0, 20, 0.008)
        interpolation_func1 = interp1d(times1, x1, kind='linear', fill_value='extrapolate')
        interpolation_func2 = interp1d(times2, x2, kind='linear', fill_value='extrapolate')
        smoothed_values1 = interpolation_func1(quantised_timestamps)
        smoothed_values2 = interpolation_func2(quantised_timestamps)
        self.times = quantised_timestamps

        return smoothed_values1, smoothed_values2
    
    def loss_function(self,params, ys, xs):
        K_p, k_d, cut_off = params
        x_pred = self.system_model(ys, K_p, k_d,cut_off)
        loss = mean_error(x_pred, xs)
        return loss

    def system_model(self, y, K_p, k_d, cut_off):
        new_y = copy.deepcopy(y)
        dy_dt = np.gradient(y, self.times)
        for i in range(len(new_y)):
            if abs(new_y[i]) <= cut_off:
                new_y[i]=0
        results = []

        for i in range(len(new_y)):
            results.append(K_p * new_y[i-round(self.D/0.008)] + k_d * dy_dt[i-round(self.D/0.008)])
        return np.array(results)
    
    def find_average_mse(self):
        init_xs, init_ys, init_times = self.find_init_model_fit()
        self.iterate_through_folders(init_xs, init_ys, init_times)


    def iterate_through_folders(self, init_xs, init_ys, init_times):
        MSEs = []
        for filename in os.listdir(self.path_to_folder):
            file_path = os.path.join(self.path_to_folder, filename)  # Full path to file
            dataframe, times = ProcessDataFrame(file_path)
            xs, ys = get_y_x_displacements(dataframe, [3,4], 0.49, 0.06)

            quant_initx, xs = self.quantise_2_datas(init_times, times, init_xs, xs)
            quant_inity, ys = self.quantise_2_datas(init_times, times, init_ys, ys)

            x_pred = self.system_model(ys, self.K_p, self.k_d, self.cut_off)
            MSEs.append(mean_error(xs, x_pred))
            # self.show_graph(xs, ys, x_pred, mean_error(xs, x_pred))

        print(f'Average MSE: {np.mean(MSEs)}')

    def find_init_model_fit(self):
        dataframe, times = ProcessDataFrame(self.path_init)
        init_xs, init_ys = get_y_x_displacements(dataframe, [3,4], 0.49, 0.06)
        self.times = times
        result = minimize(self.loss_function, [5, 10, 0.0065],args=(init_ys, init_xs))
        self.K_p, self.k_d, self.cut_off = result.x

        return init_xs, init_ys, times

    def plot_init_model_fit(self):
        init_xs, init_ys, self.times = self.find_init_model_fit()
        x_pred = self.system_model(init_ys, self.K_p, self.k_d, self.cut_off)
        MSE = mean_error(init_xs, x_pred)

        self.show_graph(init_xs, init_ys, x_pred, show_MSE=MSE)

    def compare_model_to_new(self):

        init_xs, init_ys, times1 = self.find_init_model_fit()

        dataframe, times2 = ProcessDataFrame(self.path_to_compare)
        xs, ys = get_y_x_displacements(dataframe, [3,4], 0.49, 0.06)

        init_xs, xs = self.quantise_2_datas(times1, times2, init_xs, xs)
        init_ys, ys = self.quantise_2_datas(times1, times2, init_ys, ys)
       
        x_pred = self.system_model(ys, self.K_p, self.k_d, self.cut_off)

        MSE = mean_error(xs, x_pred)


        self.show_graph(xs, ys, x_pred, MSE)