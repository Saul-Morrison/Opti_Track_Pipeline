extends Node3D

var packet := PackedByteArray()
var udp_peer := PacketPeerUDP.new()
var port := 4242
var clients:= []
var buffer_size := 7*4
var frequency
var aug := 1.0


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

func _update_pole_trans(pole: Node3D, packet: PackedByteArray) -> void:
	var floats = []
	var data = []

	for i in range(len(packet) / 4):
		data = packet.decode_float(4*i)
		floats.append(data)
		

	var quaternion = Quaternion(floats[4], floats[5], floats[3], floats[6]).normalized()
	_augment_pole_angle(pole, quaternion)
	_alert_pole_angle(pole)

func _augment_pole_angle(pole: Node3D, quaternion: Quaternion)->void:
	var rotations = quaternion.get_euler()
	var x = rotations.x
	if x > 0:
		x = x + aug * (x**0.7) * exp(-7.3*x)
	else:
		x = -1 * x
		x = x + aug * (x**0.7) * exp(-7.3*x)
		x = x * -1
	var z = rotations.z
	if z > 0:
		z = z + aug * z * exp(-7.3*z)
	else:
		z = -1 * z
		z = z + aug * z * exp(-7.3*z)
		z = z * -1
	pole.rotation.x = x
	pole.rotation.z = z
	pole.rotation.y = rotations.y

func _alert_pole_angle(pole: Node3D)->void:
	
	if (pole.rotation.x >= 0.35 or pole.rotation.x <= -0.35 or pole.rotation.z >= 0.35 or pole.rotation.z <= -0.35):
		_set_background(world_environment.environment, Color(1, 0, 0))
	else:
		_set_background(world_environment.environment, Color(1, 1, 1))

# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(_delta: float) -> void:
	#Accept new clients
	var pole = get_node('Pole')
	while udp_peer.get_available_packet_count() > 0:
		packet = udp_peer.get_packet()
	_update_pole_trans(pole, packet)
			
			
