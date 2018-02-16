import harfang as hg
from harfang_shortcut import *

status_to_parse = 1
status_parsing = 2
status_ready = 3

mats_path = ["@assets/empty.mat", "@assets/floor.mat", "@assets/magma.mat", "@assets/rock.mat", "@assets/water.mat", "@assets/tree.mat", "@assets/floor.mat", "@assets/floor.mat"]
size_big_block = vec3(16 * 1, 1, 16 * 1)


def hash_from_pos(x, y, z):
	return int(x + y * 2048 + z * 2048**2)


def hash_from_pos_v(v):
	return hash_from_pos(v.x, v.y, v.z)


def from_world_to_dfworld(new_pos):
	return vec3(new_pos.x, new_pos.z, new_pos.y)


def from_dfworld_to_world(new_pos):
	return vec3(new_pos.x, new_pos.z, new_pos.y)

