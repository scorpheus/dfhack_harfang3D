
def parse_block(fresh_block, big_block):
	world_block_pos = from_dfworld_to_world(gs.Vector3(fresh_block.map_x, fresh_block.map_y, fresh_block.map_z))
	# world_block_pos.x *= 16
	# world_block_pos.z *= 16

	x, z = 15, 0
	for tile, magma, water, material in zip(fresh_block.tiles, fresh_block.magma, fresh_block.water, fresh_block.materials):
		if tile != 0:
			type = tile_type_list.tiletype_list[tile]

			# choose a material
			block_mat = 0
			if magma > 0:
				block_mat = 2
			elif water > 0:
				block_mat = 4
			elif type.shape == remote_fortress.FLOOR:
				block_mat = 1
			elif type.shape == remote_fortress.RAMP:
				block_mat = 6
			elif type.shape == remote_fortress.RAMP_TOP:
				block_mat = 7
			elif type.shape == remote_fortress.BOULDER:
				block_mat = 3
				# array_props.append((gs.Vector3(block_pos.x*16 + x, block_pos.y, block_pos.z*16 + z), 0))
			elif type.shape == remote_fortress.PEBBLES:
				block_mat = 3
				# array_props.append((gs.Vector3(block_pos.x*16 + x, block_pos.y, block_pos.z*16 + z), 1))
			elif type.shape == remote_fortress.WALL or type.shape == remote_fortress.FORTIFICATION:
				block_mat = 3
			# if type.material == remote_fortress.PLANT:
			# 	block_mat = 2
			elif type.shape == remote_fortress.SHRUB or type.shape == remote_fortress.SAPLING:
				block_mat = 1

			if type.material == remote_fortress.TREE_MATERIAL or type.shape == remote_fortress.TRUNK_BRANCH or\
				type.shape == remote_fortress.TWIG:
				block_mat = 5

			# if it's not air, add it to draw it
			tile_pos = gs.Vector3(world_block_pos.x + x, world_block_pos.y, world_block_pos.z + z)
			id_tile = hash_from_pos(tile_pos.x, tile_pos.y, tile_pos.z)
			if block_mat != 0:
				big_block["blocks"][id_tile] = {"m": gs.Matrix4.TranslationMatrix(tile_pos), "mat": block_mat}
			else:
				if id_tile in big_block["blocks"]:
					del big_block["blocks"][id_tile]

			# add props
			# if building != -1:
			# 	array_building.append((gs.Vector3(block_pos.x*16 + x, block_pos.y, block_pos.z*16 + z), building))

		x -= 1
		if x < 0:
			x = 15
			z += 1
