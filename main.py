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


	def fill_cube_list_to_draw_in_frustum():
		block_to_draw = []
		camera = kraken_scene.scene.scene.GetCurrentCamera()
		# frustum = gs.Frustum(gs.ZoomFactorToFov(camera.camera.GetZoomFactor()), camera.camera.GetZNear(), camera.camera.GetZFar(), kraken_scene.scene.renderer.GetAspectRatio(), camera.transform.GetCurrent().world)
		frustum = gs.Frustum(gs.ZoomFactorToFov(camera.camera.GetZoomFactor()), 0.5, 20, kraken_scene.scene.renderer.GetAspectRatio(), camera.transform.GetCurrent().world)
		frustum_planes = gs.BuildFrustumPlanes(frustum)

		kraken_scene.red_list = []
		kraken_scene.blue_list = []

		def is_in_block(min_max):
			visibility = gs.ClassifyMinMax(frustum_planes, min_max)

			center = min_max.GetCenter()
			center = gs.Vector3(math.floor(center.x/16)*16, math.floor(center.y), (math.floor(center.z/16))*16)

			if visibility == gs.Outside:
				# kraken_scene.red_list.append(min_max)
				return  # outside, so not interesting

			if visibility == gs.Inside:
				# add all box in the list
				min = min_max.mn
				max = min_max.mx

				for x in range(int(min.x), int(max.x), 16):
					for y in range(int(min.y), int(max.y), 1):
						for z in range(int(min.z), int(max.z), 16):
							new_min_max = gs.MinMax(gs.Vector3(x, y, z), gs.Vector3(x+16, y+1, z+16))
							if gs.ClassifyMinMax(frustum_planes, new_min_max) != gs.Outside:
								kraken_scene.blue_list.append(new_min_max)
								block_to_draw.append(gs.Vector3(x, y, z))
				return

			if visibility == gs.Clipped:
				# check we are not in small box
				min = min_max.mn
				max = min_max.mx
				if max.x - min.x <= 16 or max.y - min.y <= 1 or max.z - min.z <= 16 or \
					center.x == min.x or center.y == min.y or center.z == min.z:
					for x in range(int(min.x), int(max.x), 16):
						for y in range(int(min.y), int(max.y), 1):
							for z in range(int(min.z), int(max.z), 16):
								new_min_max = gs.MinMax(gs.Vector3(x, y, z), gs.Vector3(x+16, y+1, z+16))
								if gs.ClassifyMinMax(frustum_planes, new_min_max) != gs.Outside:
									kraken_scene.blue_list.append(new_min_max)
									block_to_draw.append(gs.Vector3(x, y, z))
					return

				is_in_block(gs.MinMax(min, center))
				is_in_block(gs.MinMax(gs.Vector3(min.x, min.y, center.z), gs.Vector3(center.x, center.y, max.z)))
				is_in_block(gs.MinMax(gs.Vector3(center.x, min.y, min.z), gs.Vector3(max.x, center.y, center.z)))
				is_in_block(gs.MinMax(gs.Vector3(center.x, min.y, center.z), gs.Vector3(max.x, center.y, max.z)))

				is_in_block(gs.MinMax(gs.Vector3(min.x, center.y, min.z), gs.Vector3(center.x, max.y, center.z)))
				is_in_block(gs.MinMax(gs.Vector3(min.x, center.y, center.z), gs.Vector3(center.x, max.y, max.z)))
				is_in_block(gs.MinMax(gs.Vector3(center.x, center.y, min.z), gs.Vector3(max.x, max.y, center.z)))
				is_in_block(gs.MinMax(center, max))

		is_in_block(gs.MinMax(gs.Vector3(0, 0, 0), gs.Vector3(192, 512, 192)))

		return block_to_draw

	pool_blocks = []
	for i in range(700):
		pool_blocks.append(BlockMap(kraken_scene.scene))

	current_block_use = 0
	block_to_draw = []
	while True:

		if not kraken_scene.UpdateKraken():
			continue

		for step in range(10):
			current_block_use += 1
			if current_block_use >= len(block_to_draw) or len(block_to_draw) == 0:
				# check if there block outside the pos
				pos = kraken_scene.scene.scene.GetNode('render_camera').transform.GetPosition()

				for block in pool_blocks:
					if not block.free:
						block_pos = block.get_pos()
						if gs.Vector3.Dist(pos, block_pos) > 60.0:
							block.free = True

				current_block_use = 0

				block_to_draw = fill_cube_list_to_draw_in_frustum()
				print(len(block_to_draw))

			if len(block_to_draw) <= 0:
				continue

			# check if we don't have a block with this pos
			pos = block_to_draw[current_block_use]
			corner_pos = gs.Vector3(pos)
			# corner_pos = gs.Vector3(math.floor(pos.x/16)*16, math.floor(pos.y), (math.floor(pos.z/16))*16)

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

						# Get a valid block under and update it
						down_corner_block = get_block_map_from_corner_pos(corner_pos + gs.Vector3(0, -1, 0))
						if down_corner_block is not None:
							down_corner_block.update_geometry(free_block.grid_value)


finally:
	close_socket()

