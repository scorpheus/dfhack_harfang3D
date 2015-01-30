__author__ = 'scorpheus'

from dfhack_connect import *
import kraken_scene
from block_map import *
import numpy as np


def from_world_to_dfworld(pos):
	return gs.Vector3(pos.x, pos.z, pos.y)


try:
	connect_socket()
	Handshake()
	# dfversion = GetDFVersion()

	# get once to use after (material list is huge)
	tile_type_list = GetTiletypeList()
	# material_list = GetMaterialList()

	kraken_scene.InitialiseKraken()

	nb_block = gs.Vector3(2, 8, 2)
	# nb_block = gs.Vector3(5, 20, 5)

	pos_around_camera = []
	for x in range(-math.floor(nb_block.x * 0.5), math.floor(nb_block.x * 0.5)):
		for y in range(-math.floor(nb_block.y * 0.5), math.floor(nb_block.y * 0.5)):
			for z in range(-math.floor(nb_block.z * 0.5), math.floor(nb_block.z * 0.5)):
				pos_around_camera.append(gs.Vector3(x*16, y, z*16))

	pool_blocks = []
	for i in range(len(pos_around_camera)):
		pool_blocks.append(BlockMap(kraken_scene.scene))


	current_block_use = 0
	while True:

		UpdateKraken()

		pos = kraken_scene.scene.GetNode('render_camera').transform.GetPosition()
		pos.y -= 10
		pos += pos_around_camera[current_block_use]
		df_block = GetBlock(from_world_to_dfworld(pos))
		if df_block is not None:
			pool_blocks[current_block_use].update_cube_from_blocks_protobuf(tile_type_list, df_block, pos)

		current_block_use += 1
		if current_block_use >= len(pool_blocks):
			current_block_use = 0

finally:
	close_socket()

