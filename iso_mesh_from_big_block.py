import geometry_iso
import numpy as np
import gs
from helpers import *


def create_iso_geo_from_block(id_block, id_block_up, array_world_big_block):

	array_has_geo = np.empty((17, 2, 17))
	array_has_geo[:, 0, :] = list(array_world_big_block[id_block]["blocks"].values())[0]["iso_array"]
	array_has_geo[:, 1, :] = list(array_world_big_block[id_block_up]["blocks"].values())[0]["iso_array"]

	array_mats = np.empty((17, 2, 17))
	array_mats[:, 0, :] = list(array_world_big_block[id_block]["blocks"].values())[0]["iso_array_mat"]
	array_mats[:, 1, :] = list(array_world_big_block[id_block_up]["blocks"].values())[0]["iso_array_mat"]

	return geometry_iso.create_iso_c(array_has_geo, 17, 2, 17, array_mats, 0.5, mats_path, array_world_big_block[id_block]["min_pos"])
	# return geometry_iso.create_iso(array_has_geo, 17, 2, 17, array_mats, 0.5, mats_path, id_block)


def update_iso_mesh(array_world_big_block, id_block, pos):
	# if neighbourgh up, update his own iso
	up_id = hash_from_pos(pos.x, pos.y + 1, pos.z)
	if up_id in array_world_big_block and array_world_big_block[up_id]["status"] == status_ready:
		array_world_big_block[id_block]["new_iso_mesh"] = create_iso_geo_from_block(id_block, up_id, array_world_big_block)

	# if neighbourgh down, update the iso under
	down_id = hash_from_pos(pos.x, pos.y - 1, pos.z)
	if down_id in array_world_big_block and array_world_big_block[down_id]["status"] == status_ready:
		array_world_big_block[down_id]["new_iso_mesh"] = create_iso_geo_from_block(down_id, id_block, array_world_big_block)


def make_big_block_iso(array_world_big_block, big_block):
	# check if all the neighbourgh exists
	pos = gs.Vector3(big_block["min_pos"])
	pos.x = int(pos.x / size_big_block.x)
	pos.y = int(pos.y / size_big_block.y)
	pos.z = int(pos.z / size_big_block.z)
	id_block = hash_from_pos(pos.x, pos.y, pos.z)

	# update neighbour array
	north_id = hash_from_pos(pos.x, pos.y, pos.z - 1)
	south_name = hash_from_pos(pos.x, pos.y, pos.z + 1)
	west_name = hash_from_pos(pos.x - 1, pos.y, pos.z)
	east_name = hash_from_pos(pos.x + 1, pos.y, pos.z)

	if north_id in array_world_big_block and array_world_big_block[north_id]["status"] == status_ready:
		list(array_world_big_block[north_id]["blocks"].values())[0]["iso_array"][:, -1] = list(array_world_big_block[id_block]["blocks"].values())[0]["iso_array"][:, 0]
		list(array_world_big_block[north_id]["blocks"].values())[0]["iso_array_mat"][:, -1] = list(array_world_big_block[id_block]["blocks"].values())[0]["iso_array_mat"][:, 0]
		update_iso_mesh(array_world_big_block, north_id, gs.Vector3(pos.x, pos.y, pos.z - 1))

	if south_name in array_world_big_block and array_world_big_block[south_name]["status"] == status_ready:
		list(array_world_big_block[id_block]["blocks"].values())[0]["iso_array"][:, -1] = list(array_world_big_block[south_name]["blocks"].values())[0]["iso_array"][:, 0]
		list(array_world_big_block[id_block]["blocks"].values())[0]["iso_array_mat"][:, -1] = list(array_world_big_block[south_name]["blocks"].values())[0]["iso_array_mat"][:, 0]

	if west_name in array_world_big_block and array_world_big_block[west_name]["status"] == status_ready:
		list(array_world_big_block[west_name]["blocks"].values())[0]["iso_array"][-1, :] = list(array_world_big_block[id_block]["blocks"].values())[0]["iso_array"][0, :]
		list(array_world_big_block[west_name]["blocks"].values())[0]["iso_array_mat"][-1, :] = list(array_world_big_block[id_block]["blocks"].values())[0]["iso_array_mat"][0, :]
		update_iso_mesh(array_world_big_block, west_name, gs.Vector3(pos.x - 1, pos.y, pos.z))

	if east_name in array_world_big_block and array_world_big_block[east_name]["status"] == status_ready:
		list(array_world_big_block[id_block]["blocks"].values())[0]["iso_array"][-1, :] = list(array_world_big_block[east_name]["blocks"].values())[0]["iso_array"][0, :]
		list(array_world_big_block[id_block]["blocks"].values())[0]["iso_array_mat"][-1, :] = list(array_world_big_block[east_name]["blocks"].values())[0]["iso_array_mat"][0, :]

	update_iso_mesh(array_world_big_block, id_block, pos)
