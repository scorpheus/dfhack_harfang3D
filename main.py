__author__ = 'scorpheus'

from dfhack_connect import *
import kraken_scene
from block_map import *

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

	block = BlockMap(kraken_scene.scene)

	while True:

		UpdateKraken()

		pos = kraken_scene.scene.GetNode('render_camera').transform.GetPosition()
		pos.y -= 10
		df_block = GetBlock(from_world_to_dfworld(pos))
		if df_block is not None:
			block.update_cube_from_blocks_protobuf(tile_type_list, df_block, pos)


finally:
	close_socket()

