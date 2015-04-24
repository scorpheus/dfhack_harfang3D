__author__ = 'scorpheus'
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
		transform.SetScale(gs.Vector3(1, 1, 1))
		self.block_map_node.AddComponent(transform)

		self.block_script = gs.RenderScript()
		self.block_script.SetPath("block_renderable_optim_index.lua")
		self.block_map_node.AddComponent(self.block_script)

		scene.scene.AddNode(self.block_map_node)

		self.grid_value = gs.BinaryBlob()

	def get_pos(self):
		return self.corner_pos

	def update_cube_from_blocks_protobuf(self, tile_type_list, block, pos):
		if block is None:
			return

		self.free = False

		self.grid_value.Free()

		# convert pos to 16 * 16 start coordinate
		self.corner_pos = gs.Vector3(pos)
		# self.corner_pos = gs.Vector3(math.floor(pos.x/16)*16, math.floor(pos.y), (math.floor(pos.z/16))*16)
		self.block_map_node.transform.SetPosition(self.corner_pos)

		for tile in block.tiles:
			if tile_type_list.tiletype_list[tile].shape in [remote_fortress.EMPTY] and\
				tile_type_list.tiletype_list[tile].material != remote_fortress.MAGMA:
				self.grid_value.WriteInt(0)
			else:
				self.grid_value.WriteInt(1)

	def update_geometry(self, top_grid_value):
		if self.block_script.GetState() == gs.Ready:
			self.block_script.Set("grid_value", self.grid_value)
			if top_grid_value is not None:
				self.block_script.Set("grid_value_up", top_grid_value)

