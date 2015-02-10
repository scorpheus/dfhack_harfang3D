__author__ = 'scorpheus'
from kraken_scene import *
import proto.build.RemoteFortressReader_pb2 as remote_fortress


class BlockMap():
	def __init__(self, scene):
		# create the node, move it to the right place in the world and the cubes will follow
		self.free = True
		self.corner_pos = gs.Vector3()
		self.block_map_node = gs.Node()
		self.block_map_node.SetName("block_map")

		transform = gs.Transform()
		self.block_map_node.AddComponent(transform)

		self.block_script = gs.Script()
		self.block_script.SetPath("block_renderable_optim_index.lua")
		self.block_map_node.AddComponent(self.block_script)

		scene.AddNode(self.block_map_node)
		#
		# self.cubes = []
		# for x in range(16):
		# 	for z in range(16):
		# 		cube = CreateCube(gs.Vector3(x, 0, -z))
		# 		cube.transform.SetParent(self.block_map_node)
		# 		cube.object.SetGeometry(None)   # for the now we want them hidden
		# 		self.cubes.append(cube)

		self.render_geo = GetGeo('scene/assets/geo-cube.xml')

	def get_pos(self):
		return self.corner_pos

	def update_cube_from_blocks_protobuf(self, tile_type_list, block, pos):
		self.free = False

		grid_value = self.block_script.Get("grid_value")
		if grid_value is not None:
			grid_value.Free()

			# convert pos to 16 * 16 start coordinate
			self.corner_pos = gs.Vector3(math.floor(pos.x/16)*16, math.floor(pos.y), (math.floor(pos.z/16))*16)
			self.block_map_node.transform.SetPosition(self.corner_pos)

			for tile in block.tiles:
				if tile_type_list.tiletype_list[tile].shape in [remote_fortress.EMPTY] and\
					tile_type_list.tiletype_list[tile].material != remote_fortress.MAGMA:
					grid_value.WriteInt(0)
				else:
					grid_value.WriteInt(1)
			self.block_script.Set("grid_value", grid_value)
			#
		# for tile, cube in zip(block.tiles, self.cubes):
		# 	if tile_type_list.tiletype_list[tile].shape in [remote_fortress.EMPTY] and\
		# 		tile_type_list.tiletype_list[tile].material != remote_fortress.MAGMA:
		# 		# cube.SetEnabled(False)
		# 		if cube.object.GetGeometry() is not None:
		# 			cube.object.SetGeometry(None)
		# 	else:
		# 		# cube.SetEnabled(True)
		# 		if cube.object.GetGeometry() is None:
		# 			cube.object.SetGeometry(self.render_geo)


