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

	list_unit = GetListUnits()

	size_area = gs.Vector3(10, 10, 5)
	pos = gs.Vector3(list_unit.value[0].pos_x, list_unit.value[0].pos_y, list_unit.value[0].pos_z)
	p_min = (pos - size_area*0.5)
	p_max = (pos + size_area*0.5)

	p_min.x = int(p_min.x / 16)
	p_min.y = int(p_min.y / 16)
	p_min.z = int(p_min.z / 16)
	p_max.x = int(p_max.x / 16)+1
	p_max.y = int(p_max.y / 16)+1
	p_max.z = int(p_max.z / 16)+1

	blocklist = GetBlockList(p_min, p_max)

	yo = tile_type_list.tiletype_list[blocklist.map_blocks[0].tiles[0]]

	InitialiseKraken()

	# Update a structure for gs
	cube_matrix = np.empty([size_area.x, size_area.y, size_area.z], dtype=object)
	for x in range(int(size_area.x)):
		for y in range(int(size_area.y)):
			for z in range(int(size_area.z)):
				cube_matrix[x, y, z] = CreateCube(gs.Vector3(x, y, z))


	CreateCube(gs.Vector3(0, 0, 0))

	while True:
		UpdateKraken()



finally:
	close_socket()

