__author__ = 'scorpheus'

from dfhack_connect import *
import template_app
from block_map import *


def from_world_to_dfworld(pos):
	return gs.Vector3(pos.x, pos.z, pos.y)


class KrakenApp(template_app.AppTemplate):

	red_list = []
	blue_list = []

	def setup(self):
		self.pool_free_blocks = []
		self.used_blocks = []
		for i in range(700):
			self.pool_free_blocks.append(BlockMap(self))

		self.current_block_use = 0
		self.block_to_draw = []

	def on_frame_complete(self):
		# pass
		self.render_system.GetRenderer().SetWorldMatrix(gs.Matrix4.Identity)

		# for red in self.red_list:
		# 	gs.DrawBox(self.render_system, red, gs.Color.Red)
		for blue in self.blue_list:
			gs.DrawBox(self.render_system, blue, gs.Color.Blue)

	def fill_cube_list_to_draw_in_frustum(self):
		block_to_draw = []
		camera = self.scene.GetCurrentCamera()
		# frustum = gs.Frustum(gs.ZoomFactorToFov(camera.camera.GetZoomFactor()), camera.camera.GetZNear(), camera.camera.GetZFar(), kraken_scene.scene.renderer.GetAspectRatio(), camera.transform.GetCurrent().world)
		frustum = gs.Frustum(gs.ZoomFactorToFov(camera.camera.GetZoomFactor()), 0.5, 20, self.renderer.GetAspectRatio(), camera.transform.GetCurrent().world)
		frustum_planes = gs.BuildFrustumPlanes(frustum)

		self.red_list = []
		self.blue_list = []

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
								self.blue_list.append(new_min_max)
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
									self.blue_list.append(new_min_max)
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

	def on_update(self):

		if not self.scene.IsReady():
			return

		for step in range(10):
			self.current_block_use += 1
			if self.current_block_use >= len(self.block_to_draw) or len(self.block_to_draw) == 0:
				# check if there block outside the pos
				cam_pos = self.scene.GetNode('render_camera').transform.GetPosition()

				# remove too far block
				temp_used_blocks = []
				for block in self.used_blocks:
					if gs.Vector3.Dist2(cam_pos, block.get_pos()) > 60.0 * 60.0:
						self.pool_free_blocks.append(block)
					else:
						temp_used_blocks.append(block)
				self.used_blocks = temp_used_blocks

				self.current_block_use = 0

				self.block_to_draw = self.fill_cube_list_to_draw_in_frustum()
				print(len(self.block_to_draw))

			if len(self.block_to_draw) <= 0 or len(self.pool_free_blocks) == 0:
				break

			# check if we don't have a block with this pos
			pos = self.block_to_draw[self.current_block_use]
			corner_pos = gs.Vector3(pos)

			def get_block_map_from_corner_pos(corner_pos):
				for block in self.used_blocks:
					if gs.Vector3.Dist2(block.get_pos(), corner_pos) < 1.0:
						return block
				return None

			if get_block_map_from_corner_pos(corner_pos) is None:
				# Get block from df
				# df_block = GetBlock(from_world_to_dfworld(pos))
				df_block = None
				# if df_block is not None:
				if df_block is None:

					# Get a free block
					free_block = self.pool_free_blocks.pop()
					self.used_blocks.append(free_block)

					# update the grid
					free_block.update_cube_from_blocks_protobuf(tile_type_list, df_block, pos)

					# update the geometry
					# Get a grid_value from the block up
					# up_corner_block = get_block_map_from_corner_pos(corner_pos + gs.Vector3(0, 1, 0))
					# grid_value_up = None if up_corner_block is None else up_corner_block.grid_value
					#
					# free_block.update_geometry(grid_value_up)
					#
					# # Get a valid block under and update it
					# down_corner_block = get_block_map_from_corner_pos(corner_pos + gs.Vector3(0, -1, 0))
					# if down_corner_block is not None:
					# 	down_corner_block.update_geometry(free_block.grid_value)



try:
	connect_socket()
	Handshake()
	# dfversion = GetDFVersion()

	# get once to use after (material list is huge)
	tile_type_list = GetTiletypeList()
	# material_list = GetMaterialList()

	app = KrakenApp("pkg.core")
	app.open_window_and_initialize_scene(1024, 768)
	app.load_scene('scene/world_scene.scn')

	app.main_loop()


finally:
	close_socket()

