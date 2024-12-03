extends Camera3D

@export var smoothing: float = 5.0 # Higher values make the movement smoother


# Called when the node enters the scene tree for the first time.
func _ready() -> void:
	pass # Replace with function body.


# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta: float) -> void:
	var target = get_node('../../../Pole')
	var target_position = target.transform.origin
	# Get the target's global position
	look_at(target_position, Vector3(0,1,0))
	pass
