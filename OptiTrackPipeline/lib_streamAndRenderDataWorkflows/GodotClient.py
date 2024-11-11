import socket
import struct
import time

def SendRigidBodyToGodot(GameData, data, s, HOST, PORT):
    '''
    Function to send Rigid Body data to Godot Game engine
    @PARAM: GameData - array of id numbers of rigid bodies to use
    @PARAM: Data     - instance of DataHandler class
    @PARAM: s        - instance of socket class to send data over
    '''

    datatosendArray = []
    for RigidBody in data.RigidBodyData.rigid_body_list:
        if RigidBody.id_num in GameData:
            datatosendArray.extend(RigidBody.pos)
            datatosendArray.extend(RigidBody.rot)

    datatosend = struct.pack('7f', *datatosendArray)

    s.sendto(datatosend, (HOST, PORT))


def ConnectToGodot(data, GameData, HOST='127.0.0.1', PORT=4242):
    '''
    Function to send Rigid Body data to Godot Game engine
    @PARAM: GameData - Array of id numbers of rigid bodies to use
    @PARAM: Data     - Instance of DataHandler class
    @PARAM: HOST     - Godot server ip (local host if running on same device)
    @Param: PORT     - Port used by Godot server
    '''
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        try:
            print("Connected to Godot server.")

            # Example: Sending rotation data in a loop
            while True:
                # Replace with real rotation values
                data.UpdateMocapData()
                start_t = time.perf_counter()
                SendRigidBodyToGodot(GameData, data, s, HOST, PORT)
                end_t = time.perf_counter()
                # print('latency: ', end_t - start_t)

        except ConnectionRefusedError:
            print("Connection to Godot server failed. Ensure the server is running.")