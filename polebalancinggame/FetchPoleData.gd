extends Node3D

var udp_peer := PacketPeerUDP.new()
var port := 4242
var clients:= []
var buffer_size = 7*4


# Called when the node enters the scene tree for the first time.
func _ready() -> void:
	var result = udp_peer.bind(port)
	if result == OK:
		print("Server started, listening on port ", port)
	else:
		print("Failed to start server")


# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(_delta: float) -> void:
	var pole = get_node("Pole/MeshInstance3D")
	#Accept new clients
	if udp_peer.get_available_packet_count() > 0:
		print('Available Packets: ', udp_peer.get_available_packet_count())
		var packet = udp_peer.get_packet()
		var floats = []
		var data = []
		for i in range(len(packet) / 4):
			data = packet.decode_float(4*i)
			floats.append(data)
		#print(floats)
		var quaternion = Quaternion(floats[3], floats[4], floats[5], floats[6])
		pole.rotation= quaternion.get_euler()
			
			
