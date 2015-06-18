__author__ = 'scorpheus'

from dfhack_connect import *
import gs
import gs.plus.render as render
import gs.plus.input as input
import gs.plus.camera as camera
import gs.plus.clock as clock
import gs.plus.geometry as geometry
import geometry_iso

import threading
import numpy as np


def from_world_to_dfworld(new_pos):
	return gs.Vector3(new_pos.x, new_pos.z, new_pos.y)


try:
	connect_socket()
	Handshake()
	# dfversion = GetDFVersion()

	# get once to use after (material list is huge)
	tile_type_list = GetTiletypeList()
	# material_list = GetMaterialList()

	render.init(1024, 768, "pkg.core")
	gs.MountFileDriver(gs.StdFileDriver("."))

	fps = camera.fps_controller(112, 62, 112)
	fps.rot = gs.Vector3(0.5, 0, 0)

	cube = render.create_geometry(geometry.create_cube(1, 1, 1, "iso.mat"))

	pos = gs.Vector3(112//16, 62, 112//16)


	def hash_from_pos(x, y, z):
		return str(x + y * 2048 + z * 2048 * 2048)


	def hash_from_layer(layer_pos, x, z):
		return hash_from_pos(layer_pos.x + x - (layer_size - 1) / 2, layer_pos.y, layer_pos.z + z - (layer_size - 1) / 2)


	def get_block_simple(new_pos):
		_pos = gs.Vector3(new_pos)
		_pos.x *= 16
		_pos.z *= 16

		block = GetBlock(from_world_to_dfworld(_pos))

		array_has_geo = np.full((18, 18), 1)

		if block is not None:
			x, z = 1, 1
			for tile in block.tiles:
				if tile_type_list.tiletype_list[tile].shape in [remote_fortress.EMPTY] and\
					tile_type_list.tiletype_list[tile].material != remote_fortress.MAGMA:
					array_has_geo[x, z] = 0
				else:
					array_has_geo[x, z] = 1

				x += 1
				if x == 17:
					x = 1
					z += 1

		array_has_geo[:, 0] = array_has_geo[:, 1]
		array_has_geo[:, -1] = array_has_geo[:, -2]
		array_has_geo[0, :] = array_has_geo[1, :]
		array_has_geo[-1, :] = array_has_geo[-2, :]

		return array_has_geo


	class UpdateBlockFromDF(threading.Thread):
		def __init__(self, name_block, new_pos):
			threading.Thread.__init__(self)
			self.name_block = name_block
			self.block = None
			self.pos = gs.Vector3(new_pos)

		def run(self):
			self.block = get_block_simple(self.pos)

	block_drawn = 0


	def draw_geo_block(geo_block, x, y, z):
		x *= 16
		z *= 16

		render.geometry3d(x - 1, y, z - 1, geo_block)

		global block_drawn
		block_drawn += 1


	def draw_block(block, x, y, z):
		x *= 16
		z *= 16

		global block_drawn

		it = np.nditer(block, flags=['multi_index'])
		while not it.finished:
			if it[0] == 0:
				block_drawn += 1
				render.geometry3d(it.multi_index[0] + x, y, it.multi_index[1] + z, cube)
			it.iternext()

	block_fetched = 0
	layer_size = 5
	cache_block = {}
	cache_geo_block = {}
	update_cache_block = {}
	current_update_threads = [None] * 6


	class Layer:
		def __init__(self):
			self.pos = gs.Vector3()

		def update(self, new_pos):
			self.pos = gs.Vector3(new_pos)

		def fill(self):
			global update_cache_block

			block_pos = gs.Vector3()
			block_pos.x = self.pos.x - (layer_size - 1) / 2
			block_pos.y = self.pos.y
			block_pos.z = self.pos.z - (layer_size - 1) / 2

			global block_fetched
			for z in range(layer_size):
				for x in range(layer_size):
					name_block = hash_from_layer(self.pos, x, z)
					if name_block not in cache_block and name_block not in update_cache_block:
						update_cache_block[name_block] = gs.Vector3(block_pos)

					block_pos.x += 1
				block_pos.x -= layer_size
				block_pos.z += 1
			return False

		def draw(self):
			for z in range(layer_size):
				for x in range(layer_size):
					name_block = hash_from_layer(self.pos, x, z)
					if name_block in cache_geo_block:
						draw_geo_block(cache_geo_block[name_block], self.pos.x + x - (layer_size - 1) / 2, self.pos.y, self.pos.z + z - (layer_size - 1) / 2)

	layers = []
	for i in range(20):
		layers.append(Layer())

	def get_cache_block_needed():
		global block_fetched
		global current_update_thread
		count = 0
		for update_thread in current_update_threads:
			if update_thread is not None:
				if not update_thread.is_alive():
					name_block = update_thread.name_block
					block_pos = update_thread.pos
					current_block = cache_block[name_block] = update_thread.block

					current_update_threads[count] = None

					# update neighbour array
					north_name = hash_from_pos(block_pos.x, block_pos.y, block_pos.z-1)
					if north_name in cache_block:
						cache_block[north_name][:, -1] = current_block[:, 1]
						current_block[:, 0] = cache_block[north_name][:, -2]
					south_name = hash_from_pos(block_pos.x, block_pos.y, block_pos.z+1)
					if south_name in cache_block:
						cache_block[south_name][:, 0] = current_block[:, -2]
						current_block[:, -1] = cache_block[south_name][:, 1]
					west_name = hash_from_pos(block_pos.x-1, block_pos.y, block_pos.z)
					if west_name in cache_block:
						cache_block[west_name][-1, :] = current_block[1, :]
						current_block[0, :] = cache_block[west_name][-2, :]
					east_name = hash_from_pos(block_pos.x+1, block_pos.y, block_pos.z)
					if east_name in cache_block:
						cache_block[east_name][0, :] = current_block[-2, :]
						current_block[-1, :] = cache_block[east_name][1, :]

					update_cache_block.pop(name_block)
					block_fetched += 1

			elif len(update_cache_block) > count:
				iter_update_block = iter(update_cache_block.items())
				name_block, block_pos = None, None
				for i in range(count + 1):
					name_block, block_pos = next(iter_update_block)

				update_thread = UpdateBlockFromDF(name_block, block_pos)
				update_thread.run()
				current_update_threads[count] = update_thread

			count += 1


	def get_geo_from_blocks(name_geo, block, upper_block):
		array_has_geo = np.empty((18, 2, 18))
		array_has_geo[:, 0, :] = block
		array_has_geo[:, 1, :] = upper_block

		if array_has_geo.sum() == 0 or np.average(array_has_geo) == 1:
			return render.create_geometry(gs.CoreGeometry())
		else:
			return geometry_iso.create_iso(array_has_geo, 18, 2, 18, 1.0, "iso.mat", name_geo)


	def update_geo_layer(current_layer, upper_layer):
		for z in range(layer_size):
			for x in range(layer_size):
				current_layer_block_name = hash_from_layer(current_layer.pos, x, z)
				upper_layer_block_name = hash_from_layer(upper_layer.pos, x, z)

				if current_layer_block_name not in cache_geo_block\
					and current_layer_block_name in cache_block and upper_layer_block_name in cache_block:
					def check_block_can_generate_geo(layer_pos):
						# can update the geo block because it has all the neighbour
						counter_update = 0
						if hash_from_layer(layer_pos, x, z-1) in cache_block:
							counter_update += 1
						if hash_from_layer(layer_pos, x, z+1) in cache_block:
							counter_update += 1
						if hash_from_layer(layer_pos, x-1, z) in cache_block:
							counter_update += 1
						if hash_from_layer(layer_pos, x+1, z) in cache_block:
							counter_update += 1
						return counter_update == 4

					if check_block_can_generate_geo(current_layer.pos) and check_block_can_generate_geo(upper_layer.pos):
						cache_geo_block[current_layer_block_name] = get_geo_from_blocks(current_layer_block_name, cache_block[current_layer_block_name], cache_block[upper_layer_block_name])
						return


	old_pos = gs.Vector3()
	while not input.key_press(gs.InputDevice.KeyEscape):
		render.clear()

		dt_sec = clock.update()
		fps.update(dt_sec)
		render.set_camera3d(fps.pos.x, fps.pos.y, fps.pos.z, fps.rot.x, fps.rot.y, fps.rot.z)

		# pos -> blocks dans lequel on peux se deplacer
		pos.x = fps.pos.x // 16
		pos.y = (fps.pos.y - 10) // 1
		pos.z = fps.pos.z // 16

		#
		if pos.y > old_pos.y:
			for i in range(len(layers) - 1):
				layers[i] = layers[i + 1]
			layers[-1] = Layer()
		elif pos.y < old_pos.y:
			for i in range(len(layers) - 1, 0, -1):
				layers[i] = layers[i - 1]
			layers[0] = Layer()

		old_pos = gs.Vector3(pos)

		#
		block_fetched, block_drawn = 0, 0

		for i, layer in enumerate(layers):
			layer.update(pos + gs.Vector3(0, i, 0))
			layer.fill()
			layer.draw()

		get_cache_block_needed()

		# update layer geo
		for i in range(0, len(layers) - 1):
			update_geo_layer(layers[i], layers[i + 1])

		render.text2d(0, 45, "FPS: %.2fHZ - BLOCK FETCHED: %d - BLOCK DRAWN: %d" % (1 / dt_sec, block_fetched, block_drawn), color=gs.Color.Red)
		render.text2d(0, 25, "FPS.X = %f, FPS.Z = %f" % (fps.pos.x, fps.pos.z), color=gs.Color.Red)
		render.text2d(0, 5, "POS.X = %f, POS.Z = %f" % (pos.x, pos.z), color=gs.Color.Red)

		render.flip()

finally:
	close_socket()

