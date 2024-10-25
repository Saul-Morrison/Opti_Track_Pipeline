from lib_streamAndRenderDataWorkflows.Visualiser import Visualiser


Charlie_Demo = Visualiser(SharedMemName='Motive Dump', NoDataTypes=1, VarsPerDataType=7)

if __name__ == "__main__":
    Charlie_Demo.visualiseVectorsFrom3DarrayAnimation(RelativeView=True)
    #Charlie_Demo.visualise2DDataFrom3DarrayAnimation()