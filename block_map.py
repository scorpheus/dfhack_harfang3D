__author__ = 'scorpheus'
from kraken_scene import *
import proto.build.RemoteFortressReader_pb2 as remote_fortress


class BlockMap():
	def __init__(self, scene):
		# create the node, move it to the right place in the world and the cubes will follow
		self.block_map_node = gs.Node()
		self.block_map_node.SetName("block_map")

		transform = gs.Transform()
		self.block_map_node.AddComponent(transform)

		scene.AddNode(self.block_map_node)

		self.cubes = []
		for x in range(16):
			for z in range(16):
				cube = CreateCube(gs.Vector3(x, 0, -z))
				cube.transform.SetParent(self.block_map_node)
				cube.object.SetGeometry(None)   # for the now we want them hidden
				self.cubes.append(cube)

		self.render_geo = GetGeo('scene/assets/geo-cube.xml')

	def update_cube_from_blocks_protobuf(self, tile_type_list, block, pos):
		# convert pos to 16 * 16 start coordinate
		corner_pos = gs.Vector3(int(pos.x/16)*16, int(pos.y), (int(pos.z/16)+1)*16)
		self.block_map_node.transform.SetPosition(corner_pos)

		for tile, cube in zip(block.tiles, self.cubes):
			if tile_type_list.tiletype_list[tile].shape in [remote_fortress.EMPTY] and\
				tile_type_list.tiletype_list[tile].material != remote_fortress.MAGMA:
				if cube.object.GetGeometry() is not None:
					cube.object.SetGeometry(None)
			else:
				if cube.object.GetGeometry() is None:
					cube.object.SetGeometry(self.render_geo)


