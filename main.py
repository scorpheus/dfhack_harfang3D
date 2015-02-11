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

	nb_block = gs.Vector3(4, 4, 4)
	# nb_block = gs.Vector3(5, 8, 5)
	# nb_block = gs.Vector3(5, 20, 5)

	pos_around_camera = []
	for x in range(-math.floor(nb_block.x * 0.5), math.floor(nb_block.x * 0.5)):
		for y in range(-math.floor(nb_block.y * 0.5), math.floor(nb_block.y * 0.5)):
			for z in range(-math.floor(nb_block.z * 0.5), math.floor(nb_block.z * 0.5)):
				pos_around_camera.append(gs.Vector3(x*16, y, z*16))

				# print('start: %.2f, %.2f, %.2f' % (x*16, y, z*16))

	pool_blocks = []
	for i in range(len(pos_around_camera)):
		pool_blocks.append(BlockMap(kraken_scene.scene))


	current_block_use = 0
	while True:

		UpdateKraken()

		pos = kraken_scene.scene.GetNode('render_camera').transform.GetPosition()
		# pos.y -= 10

		# check if we don't have a block with this pos
		pos += pos_around_camera[current_block_use]
		corner_pos = gs.Vector3(math.floor(pos.x/16)*16, math.floor(pos.y), (math.floor(pos.z/16))*16)

		def get_block_map_from_corner_pos(corner_pos):
			for block in pool_blocks:
				if not block.free:
					if gs.Vector3.Dist2(block.get_pos(), corner_pos) < 1.0:
						return block
			return None

		corner_block = get_block_map_from_corner_pos(corner_pos)
		already_have_this_pos = False if corner_block is None else True

		if not already_have_this_pos:
			# Get a free block
			free_block = None
			for block in pool_blocks:
				if block.free:
					free_block = block
					break

			if free_block is not None:
				# print('update: %.2f, %.2f, %.2f' % (corner_pos.x, corner_pos.y, corner_pos.z))
				# Get block from df
				df_block = GetBlock(from_world_to_dfworld(pos))

				if df_block is not None:
					# update the grid
					free_block.update_cube_from_blocks_protobuf(tile_type_list, df_block, pos)

					# update the geometry
					# Get a grid_value from the block up
					up_corner_block = get_block_map_from_corner_pos(corner_pos + gs.Vector3(0, 1, 0))
					grid_value_up = None if corner_block is None else corner_block.grid_value

					free_block.update_geometry(grid_value_up)

					# Get a valid block under
					down_corner_block = get_block_map_from_corner_pos(corner_pos + gs.Vector3(0, -1, 0))
					if down_corner_block is not None:
						down_corner_block.update_geometry(free_block.grid_value)

		current_block_use += 1
		if current_block_use >= len(pool_blocks):

			# check if there block outside the pos
			pos = kraken_scene.scene.GetNode('render_camera').transform.GetPosition()
			# pos.y -= 10
			# print('pos: %.2f, %.2f, %.2f' % (pos.x, pos.y, pos.z))


			min_pos = gs.Vector3(math.floor((pos.x+pos_around_camera[0].x)/16)*16, math.floor((pos.y+pos_around_camera[0].y)), (math.floor((pos.z+pos_around_camera[0].z)/16))*16)
			max_pos = gs.Vector3(math.floor((pos.x+pos_around_camera[len(pos_around_camera)-1].x)/16)*16, math.floor((pos.y+pos_around_camera[len(pos_around_camera)-1].y)), (math.floor((pos.z+pos_around_camera[len(pos_around_camera)-1].z)/16))*16)
		
			for block in pool_blocks:
				if not block.free:
					block_pos = block.get_pos()
					if min_pos.x > block_pos.x or max_pos.x < block_pos.x or \
						min_pos.y > block_pos.y or max_pos.y < block_pos.y or \
						min_pos.z > block_pos.z or max_pos.z < block_pos.z:
						block.free = True

			current_block_use = 0

finally:
	close_socket()

