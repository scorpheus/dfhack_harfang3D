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

	# nb_block = gs.Vector3(4, 4, 4)
	# nb_block = gs.Vector3(5, 8, 5)
	# nb_block = gs.Vector3(5, 20, 5)

	# pos_around_camera = []
	# for x in range(-math.floor(nb_block.x * 0.5), math.floor(nb_block.x * 0.5)):
	# 	for y in range(-math.floor(nb_block.y * 0.5), math.floor(nb_block.y * 0.5)):
	# 		for z in range(-math.floor(nb_block.z * 0.5), math.floor(nb_block.z * 0.5)):
	# 			pos_around_camera.append(gs.Vector3(x*16, y, z*16))
	#
	# 			# print('start: %.2f, %.2f, %.2f' % (x*16, y, z*16))

	pool_blocks = []
	for i in range(5*5*10):
		pool_blocks.append(BlockMap(kraken_scene.scene))

	def fill_cube_list_to_draw_in_frustum():
		block_to_draw = []
		camera = kraken_scene.scene.GetCurrentCamera()
		frustum = gs.Frustum(gs.ZoomFactorToFov(camera.camera.GetZoomFactor()), camera.camera.GetZNear(), camera.camera.GetZFar(), kraken_scene.egl.GetAspectRatio(), camera.transform.GetCurrent().world)
		frustum_planes = gs.BuildFrustumPlanes(frustum)

		camera_right = camera.transform.GetCurrent().world.GetX()
		camera_up = camera.transform.GetCurrent().world.GetY()
		camera_front = camera.transform.GetCurrent().world.GetZ()
		camera_pos = camera.transform.GetCurrent().world.GetTranslation()
		nb_block = gs.Vector3(5, 5, 100)

		for x in range(-math.floor(nb_block.x * 0.5), math.floor(nb_block.x * 0.5)):
			for y in range(-math.floor(nb_block.y * 0.5), math.floor(nb_block.y * 0.5)):


				for z in range(-math.floor(nb_block.z * 0.5), math.floor(nb_block.z * 0.5)):
					dir = camera_right * x * 16 + camera_up * y + camera_front * z * 16
					pos = camera_pos + dir
					min_max = gs.MinMax(pos, pos + gs.Vector3(16, 1, 16))

					if gs.ClassifyMinMax(frustum_planes, min_max) != gs.Outside:
						block_to_draw.append(pos)

		return block_to_draw

	current_block_use = 0
	do_once = False
	while True:

		UpdateKraken()
		if not kraken_scene.scene.IsReady():
			continue

		if not do_once:
			block_to_draw = fill_cube_list_to_draw_in_frustum()
			do_once = True
		if len(block_to_draw) <= 0:
			continue

		current_block_use += 1
		if current_block_use >= len(block_to_draw):

			# check if there block outside the pos
			pos = kraken_scene.scene.GetNode('render_camera').transform.GetPosition()

			for block in pool_blocks:
				if not block.free:
					block_pos = block.get_pos()
					if gs.Vector3.Dist(pos, block_pos) > 100.0:
						block.free = True

			current_block_use = 0

		# pos = kraken_scene.scene.GetNode('render_camera').transform.GetPosition()
		# pos.y -= 10

		# check if we don't have a block with this pos
		pos = block_to_draw[current_block_use]
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


finally:
	close_socket()

