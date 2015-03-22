__author__ = 'scorpheus'
import kraken_scene
import gs
import math
import proto.build.RemoteFortressReader_pb2 as remote_fortress


class BlockMap():
	def __init__(self, scene):
		# create the node, move it to the right place in the world and the cubes will follow
		self.free = True
		self.corner_pos = gs.Vector3()
		self.block_map_node = gs.Node()
		self.block_map_node.SetName("block_map")

		transform = gs.Transform()
		transform.SetScale(gs.Vector3(16,1,16))
		self.block_map_node.AddComponent(transform)

		self.block_script = gs.RenderScript()
		self.block_script.SetPath("block_renderable_optim_index.lua")
		self.block_map_node.AddComponent(self.block_script)

		scene.AddNode(self.block_map_node)


		self.render_geo = None
		self.object = None

		# self.cubes = []
		# for x in range(16):
		# 	for z in range(16):
		# 		cube = CreateCube(gs.Vector3(x, 0, -z))
		# 		cube.transform.SetParent(self.block_map_node)
		# 		cube.object.SetGeometry(None)   # for the now we want them hidden
		# 		self.cubes.append(cube)

		# self.render_geo = GetGeo('scene/assets/geo-cube.xml')

		self.grid_value = gs.BinaryBlob()

	def get_pos(self):
		return self.corner_pos

	def update_cube_from_blocks_protobuf(self, tile_type_list, block, pos):
		if kraken_scene.render_system_async == 0:
			return

		self.free = False

		self.grid_value.Free()

		if self.render_geo is None:
			self.render_geo = kraken_scene.render_system_async.LoadGeometry('scene/assets/geo-cube.xml', True)
			self.object = gs.Object()
			self.object.SetGeometry(self.render_geo)
			self.block_map_node.AddComponent(self.object)


		# convert pos to 16 * 16 start coordinate
		self.corner_pos = gs.Vector3(math.floor(pos.x/16)*16, math.floor(pos.y), (math.floor(pos.z/16))*16)
		self.block_map_node.transform.SetPosition(self.corner_pos)

		# for tile in block.tiles:
		# 	if tile_type_list.tiletype_list[tile].shape in [remote_fortress.EMPTY]:
		# 	# if tile_type_list.tiletype_list[tile].shape in [remote_fortress.EMPTY] and\
		# 	# 	tile_type_list.tiletype_list[tile].material != remote_fortress.MAGMA:
		# 		self.grid_value.WriteInt(0)
		# 	else:
		# 		self.grid_value.WriteInt(1)

		self.object.SetGeometry(self.render_geo)

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

	def update_geometry(self, top_grid_value):
		if self.block_script.IsReady():
			self.block_script.Set("grid_value", self.grid_value)
			if top_grid_value is not None:
				self.block_script.Set("grid_value_up", top_grid_value)

