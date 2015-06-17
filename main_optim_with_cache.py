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
		def __init__(self, new_pos):
			threading.Thread.__init__(self)
			self.block = None
			self.pos = new_pos

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
			if it[0] == 1:
				block_drawn += 1
				render.geometry3d(it.multi_index[0] + x, y, it.multi_index[1] + z, cube)
			it.iternext()

	block_fetched = 0
	layer_size = 5
	cache_block = {}
	cache_geo_block = {}


	class Layer:
		def __init__(self):
			self.blocks = [None] * (layer_size * layer_size)
			self.update_block_threads = [None] * (layer_size * layer_size)
			self.geo_blocks = [None] * (layer_size * layer_size)
			self.old_pos = gs.Vector3()
			self.pos = gs.Vector3()

		def switch_tile(self, tile_from, tile_to):
			self.blocks[tile_to] = self.blocks[tile_from]
			self.geo_blocks[tile_to] = self.geo_blocks[tile_from]
			self.update_block_threads[tile_to] = self.update_block_threads[tile_from]

		def clean_or_check_cache(self, x, z):
			name_block = hash_from_layer(self.pos, x, z)

			i = x + z * layer_size
			if name_block in cache_block:
				self.blocks[i] = cache_block[name_block]
			else:
				self.blocks[i] = None

			self.geo_blocks[i] = None
			# self.blocks[i] = None
			self.update_block_threads[i] = None

			# if name_block in cache_geo_block:
			# 	self.geo_blocks[i] = cache_geo_block[name_block]
			# else:
			# 	self.geo_blocks[i] = None

		def update(self, new_pos):
			self.pos = gs.Vector3(new_pos)

			if self.pos != self.old_pos:
				if self.pos.x > self.old_pos.x:
					for z in range(layer_size):
						for x in range(layer_size - 1):
							self.switch_tile(x + 1 + z * layer_size, x + z * layer_size)
						self.clean_or_check_cache(layer_size-1, z)
				elif self.pos.x < self.old_pos.x:
					for z in range(layer_size):
						for x in range(layer_size - 1, 0, -1):
							self.switch_tile(x - 1 + z * layer_size, x + z * layer_size)
						self.clean_or_check_cache(0, z)

				if self.pos.z > self.old_pos.z:
					for x in range(layer_size):
						for z in range(layer_size - 1):
							self.switch_tile(x + (z + 1) * layer_size, x + z * layer_size)
							self.clean_or_check_cache(x, layer_size - 1)
				elif self.pos.z < self.old_pos.z:
					for x in range(layer_size):
						for z in range(layer_size - 1, 0, -1):
							self.switch_tile(x + (z - 1) * layer_size, x + z * layer_size)
						self.clean_or_check_cache(x, 0)

			self.old_pos = gs.Vector3(self.pos)

		def fill(self):
			block_pos = gs.Vector3()
			block_pos.x = self.pos.x - (layer_size - 1) / 2
			block_pos.y = self.pos.y
			block_pos.z = self.pos.z - (layer_size - 1) / 2

			global block_fetched
			for z in range(layer_size):
				for x in range(layer_size):
					i = x + z * layer_size
					if self.blocks[i] is None:
						name_block = hash_from_layer(self.pos, x, z)
						if name_block in cache_block:
							self.blocks[i] = cache_block[name_block]
						elif self.update_block_threads[i] is None:
							self.update_block_threads[i] = UpdateBlockFromDF(block_pos)
							self.update_block_threads[i].run()
						elif not self.update_block_threads[i].is_alive():
							self.blocks[i] = self.update_block_threads[i].block
							cache_block[name_block] = self.blocks[i]

							# update neighbour array
							north_name = hash_from_layer(self.pos, x, z-1) in cache_block
							if north_name in cache_block:
								cache_block[north_name][:, -1] = self.blocks[i][:, 1]
								self.blocks[i][:, 0] = cache_block[north_name][:, -2]
							south_name = hash_from_layer(self.pos, x, z+1) in cache_block
							if south_name in cache_block:
								cache_block[south_name][:, 0] = self.blocks[i][:, -2]
								self.blocks[i][:, -1] = cache_block[south_name][:, 1]
							west_name = hash_from_layer(self.pos, x-1, z) in cache_block
							if west_name in cache_block:
								cache_block[west_name][-1, :] = self.blocks[i][1, :]
								self.blocks[i][0, :] = cache_block[west_name][-2, :]
							east_name = hash_from_layer(self.pos, x+1, z) in cache_block
							if east_name in cache_block:
								cache_block[east_name][0, :] = self.blocks[i][-2, :]
								self.blocks[i][-1, :] = cache_block[east_name][1, :]

							block_fetched += 1

							if name_block in cache_geo_block:
								self.geo_blocks[i] = cache_geo_block[name_block]
							else:
								self.geo_blocks[i] = None
						return True

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
					# i = x + z * layer_size
					# if self.geo_blocks[i] is not None:
					# 	draw_geo_block(self.geo_blocks[i], self.pos.x + x - (layer_size - 1) / 2, self.pos.y, self.pos.z + z - (layer_size - 1) / 2)


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
				i = x + z * layer_size
				if current_layer.geo_blocks[i] is None\
					and current_layer.blocks[i] is not None and upper_layer.blocks[i] is not None:
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
						name_block = hash_from_layer(current_layer.pos, x, z)
						current_layer.geo_blocks[i] = get_geo_from_blocks(name_block, current_layer.blocks[i], upper_layer.blocks[i])
						cache_geo_block[name_block] = current_layer.geo_blocks[i]
						return


	layers = []
	for i in range(20):
		layers.append(Layer())


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
			layer.draw()

		count = 0
		for layer in layers:
			if layer.fill():
				count += 1
				if count > 3:
					break

		# update layer geo
		for i in range(0, len(layers) - 1):
			update_geo_layer(layers[i], layers[i + 1])

		render.text2d(0, 45, "FPS: %.2fHZ - BLOCK FETCHED: %d - BLOCK DRAWN: %d" % (1 / dt_sec, block_fetched, block_drawn), color=gs.Color.Red)
		render.text2d(0, 25, "FPS.X = %f, FPS.Z = %f" % (fps.pos.x, fps.pos.z), color=gs.Color.Red)
		render.text2d(0, 5, "POS.X = %f, POS.Z = %f" % (pos.x, pos.z), color=gs.Color.Red)

		render.flip()

finally:
	close_socket()

