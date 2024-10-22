from VisualiseDataWorkFlows.Visualiser import Visualiser


Charlie_Demo = Visualiser(SharedMemName='Motive Dump', NoDataTypes=51, VarsPerDataType=7)

if __name__ == "__main__":
    Charlie_Demo.visualiseVectorsFrom3DarrayAnimation()
    #Charlie_Demo.visualise2DDataFrom3DarrayAnimation()