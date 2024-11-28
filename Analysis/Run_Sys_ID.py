from System_Identification import system_identifier

path_init = 'OptiTrackPipeline/test_lib_streamAndRenderDataWorkflows/TFunctions/TFunction2024_11_18_16_07.csv'
compare_path = 'OptiTrackPipeline/test_lib_streamAndRenderDataWorkflows/TFunctions/TFunction2024_11_18_16_05.csv'
path_to_folder = 'OptiTrackPipeline/test_lib_streamAndRenderDataWorkflows/TFunctions'

sys_id = system_identifier(path_init, compare_path, path_to_folder=path_to_folder)

if __name__ == '__main__':
    sys_id.plot_init_model_fit()
    sys_id.compare_model_to_new()
    sys_id.find_average_mse()