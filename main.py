__author__ = 'scorpheus'

from dfhack_connect import *
from kraken_scene import *
import numpy as np


try:
	connect_socket()
	Handshake()
	# dfversion = GetDFVersion()

	# get once to use after (material list is huge)
	tile_type_list = GetTiletypeList()
	# material_list = GetMaterialList()


	size_area = gs.Vector3(20, 20, 10)

	InitialiseKraken()

	# Update a structure for gs
	cube_matrix = np.empty([size_area.x, size_area.y, size_area.z], dtype=object)
	for x in range(int(size_area.x)):
		for y in range(int(size_area.y)):
			for z in range(int(size_area.z)):
				cube_matrix[x, y, z] = CreateCube(gs.Vector3(x, z, y))


	render_geo = GetGeo('scene/assets/geo-cube.xml')
	while True:
		UpdateKraken()

		list_unit = GetListUnits()

		pos = gs.Vector3(list_unit.value[12].pos_x, list_unit.value[12].pos_y, list_unit.value[12].pos_z)
		p_min = (pos - size_area*0.5)
		p_max = (pos + size_area*0.5)

		blocklist = GetBlockList(p_min, p_max)

		for x in range(int(size_area.x)):
			for y in range(int(size_area.y)):
				for z in range(int(size_area.z)):
					#find good block
					start_x = int((p_min.x + x)/16)*16
					start_y = int((p_min.y + y)/16)*16
					start_z = int(p_min.z + z)
					for block in blocklist.map_blocks:
						if start_x == block.map_x and start_y == block.map_y and start_z == block.map_z:
							# print(tile_type_list.tiletype_list[block.tiles[int(p_min.x - start_x + x + (p_min.y - start_y + y)*16)]].shape)

							# if tile_type_list.tiletype_list[block.tiles[int(p_min.x - start_x + x + (p_min.y - start_y + y)*16)]].shape in \
							# 		[remote_fortress.FLOOR, remote_fortress.BOULDER, remote_fortress.PEBBLES, remote_fortress.WALL, remote_fortress.FORTIFICATION]:
							# 	cube_matrix[x, y, z].object.SetGeometry(render_geo)
							# else:
							# 	cube_matrix[x, y, z].object.SetGeometry(None)

							if tile_type_list.tiletype_list[block.tiles[int(p_min.x - start_x + x + (p_min.y - start_y + y)*16)]].shape in \
									[remote_fortress.EMPTY]:
								cube_matrix[x, y, z].object.SetGeometry(None)
							else:
								cube_matrix[x, y, z].object.SetGeometry(render_geo)

							break
finally:
	close_socket()

