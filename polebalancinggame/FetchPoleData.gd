extends Node3D

var udp_peer := PacketPeerUDP.new()
var port := 4242
var clients:= []
var buffer_size := 7*4
var frequency

@onready var frame_rate = $CanvasLayer/RichTextLabel
@onready var world_environment = $WorldEnvironment

func _set_background(environment: Environment,bcolor: Color)->void:
	environment.background_mode = 1
	environment.background_color = bcolor

# Called when the node enters the scene tree for the first time.
func _ready() -> void:
	var result = udp_peer.bind(port)
	if result == OK:
		print("Server started, listening on port ", port)
	else:
		print("Failed to start server")
	_set_background(world_environment.environment, Color(1,1,1))

func _update_pole_trans(pole: Node3D, udp_peer: PacketPeerUDP) -> void:
	var packet = udp_peer.get_packet()
	var floats = []
	var data = []
	for i in range(len(packet) / 4):
		data = packet.decode_float(4*i)
		floats.append(data)
	var quaternion = Quaternion(floats[3], floats[5], floats[4], floats[6])
	pole.rotation= quaternion.get_euler()

func _alert_pole_angle(pole: Node3D)->void:
	if (pole.rotation.x >= 0.15 or pole.rotation.x <= -0.15 or pole.rotation.z >= 0.15 or pole.rotation.z <= -0.15):
		_set_background(world_environment.environment, Color(1, 0, 0))
	else:
		_set_background(world_environment.environment, Color(1, 1, 1))

# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(_delta: float) -> void:
	#Accept new clients
	var pole = get_node('Pole')
	while udp_peer.get_available_packet_count() > 0:
		_update_pole_trans(pole, udp_peer)
		frame_rate.text = 'FPS: ' + str(1 / _delta)
	_alert_pole_angle(pole)
	
			
			
