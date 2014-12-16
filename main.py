__author__ = 'scorpheus'

from dfhack_connect import *
from kraken_scene import *
import numpy as np
import time


try:
	connect_socket()
	Handshake()
	# dfversion = GetDFVersion()

	# get once to use after (material list is huge)
	tile_type_list = GetTiletypeList()
	# material_list = GetMaterialList()


	size_area = gs.Vector3(40, 40, 10)

	InitialiseKraken()

	# Update a structure for gs
	cube_matrix = np.empty([size_area.x, size_area.y, size_area.z], dtype=object)
	for x in range(int(size_area.x)):
		for y in range(int(size_area.y)):
			for z in range(int(size_area.z)):
				cube_matrix[x, y, z] = CreateCube(gs.Vector3(x, z, -y))


	render_geo = GetGeo('scene/assets/geo-cube.xml')

	phase_update = 0

	while True:

		UpdateKraken()

		if phase_update == 0:
			list_unit = GetListUnits()

			pos = gs.Vector3(list_unit.value[0].pos_x, list_unit.value[0].pos_y, list_unit.value[0].pos_z)
			p_min = (pos - size_area*0.5)
			p_max = (pos + size_area*0.5)

		elif phase_update == 1:
			blocklist = GetBlockList(p_min, p_max)

		elif phase_update == 2:
			for block in blocklist.map_blocks:
				for x in range(16):
					if p_min.x <= block.map_x + x < p_max.x:
						for y in range(16):
							if p_min.y <= block.map_y + y < p_max.y:
								if p_min.z <= block.map_z < p_max.z:
									matrix_x = block.map_x + x - p_min.x
									matrix_y = block.map_y + y - p_min.y
									matrix_z = block.map_z - p_min.z

									# yo = material_list.material_list[block.materials[int(x + y*16)].mat_index]
									if tile_type_list.tiletype_list[block.tiles[int(x + y*16)]].shape in [remote_fortress.EMPTY] and\
										tile_type_list.tiletype_list[block.tiles[int(x + y*16)]].material != remote_fortress.MAGMA:
										cube_matrix[matrix_x, matrix_y, matrix_z].object.SetGeometry(None)
									else:
										cube_matrix[matrix_x, matrix_y, matrix_z].object.SetGeometry(render_geo)
			phase_update = -1

		phase_update += 1
		#
		# time_process1 = time.perf_counter() - time_process
		# time_process = time.perf_counter()
		#
		# # use the flag unactive, lose 0.002 sec perf
		# for block in blocklist.map_blocks:
		# 	for x in range(16):
		# 		if p_min.x <= block.map_x + x < p_max.x:
		# 			for y in range(16):
		# 				if p_min.y <= block.map_y + y < p_max.y:
		# 					if p_min.z <= block.map_z < p_max.z:
		# 						matrix_x = block.map_x + x - p_min.x
		# 						matrix_y = block.map_y + y - p_min.y
		# 						matrix_z = block.map_z - p_min.z
		#
		# 						if tile_type_list.tiletype_list[block.tiles[int(x + y*16)]].shape in \
		# 								[remote_fortress.EMPTY]:
		# 							cube_matrix[matrix_x, matrix_y, matrix_z].SetFlag(gs.Node.FlagIsActive, False)
		# 							# cube_matrix[matrix_x, matrix_y, matrix_z].object.SetGeometry(None)
		# 						else:
		# 							cube_matrix[matrix_x, matrix_y, matrix_z].SetFlag(gs.Node.FlagIsActive, True)
		# 							# cube_matrix[matrix_x, matrix_y, matrix_z].object.SetGeometry(render_geo)

		#
		# use the first naive method, lose 0.13 sec perf
		# for x in range(int(size_area.x)):
		# 	for y in range(int(size_area.y)):
		# 		for z in range(int(size_area.z)):
		# 			#find good block
		# 			start_x = int((p_min.x + x)/16)*16
		# 			start_y = int((p_min.y + y)/16)*16
		# 			start_z = int(p_min.z + z)
		# 			for block in blocklist.map_blocks:
		# 				if start_x == block.map_x and start_y == block.map_y and start_z == block.map_z:
		# 					# print(tile_type_list.tiletype_list[block.tiles[int(p_min.x - start_x + x + (p_min.y - start_y + y)*16)]].shape)
		#
		# 					# if tile_type_list.tiletype_list[block.tiles[int(p_min.x - start_x + x + (p_min.y - start_y + y)*16)]].shape in \
		# 					# 		[remote_fortress.FLOOR, remote_fortress.BOULDER, remote_fortress.PEBBLES, remote_fortress.WALL, remote_fortress.FORTIFICATION]:
		# 					# 	cube_matrix[x, y, z].object.SetGeometry(render_geo)
		# 					# else:
		# 					# 	cube_matrix[x, y, z].object.SetGeometry(None)
		#
		# 					if tile_type_list.tiletype_list[block.tiles[int(p_min.x - start_x + x + (p_min.y - start_y + y)*16)]].shape in \
		# 							[remote_fortress.EMPTY]:
		# 						cube_matrix[x, y, z].object.SetGeometry(None)
		# 					else:
		# 						cube_matrix[x, y, z].object.SetGeometry(render_geo)
		#
		# 					break

finally:
	close_socket()

