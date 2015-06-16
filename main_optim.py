__author__ = 'scorpheus'

from dfhack_connect import *
import gs
import gs.plus.render as render
import gs.plus.input as input
import gs.plus.camera as camera
import gs.plus.scene as scene
import gs.plus.clock as clock
import gs.plus.geometry as geometry

import numpy as np


def from_world_to_dfworld(pos):
	return gs.Vector3(pos.x, pos.z, pos.y)


try:
	connect_socket()
	Handshake()
	# dfversion = GetDFVersion()

	# get once to use after (material list is huge)
	tile_type_list = GetTiletypeList()
	# material_list = GetMaterialList()

	render.init(1920, 1080, "pkg.core")
	gs.MountFileDriver(gs.StdFileDriver("."))

	fps = camera.fps_controller(112, 62, 112)
	fps.rot = gs.Vector3(0.5, 0, 0)

	cube = render.create_geometry(geometry.create_cube(1, 1, 1, "iso.mat"))

	pos = gs.Vector3(112//16, 62, 112//16)
	size_display = gs.Vector3(16, 14, 16)


	def get_block_simple(pos):
		_pos = gs.Vector3(pos)
		_pos.x *= 16
		_pos.z *= 16

		block = GetBlock(from_world_to_dfworld(_pos))

		array_has_geo = np.full((16, 1, 16), 0)

		if block is not None:
			x, y, z = 0, 0, 0
			for tile in block.tiles:
				if tile_type_list.tiletype_list[tile].shape in [remote_fortress.EMPTY] and\
					tile_type_list.tiletype_list[tile].material != remote_fortress.MAGMA:
					array_has_geo[x, y, z] = 0
				else:
					array_has_geo[x, y, z] = 1

				x += 1
				if x == 16:
					x = 0
					z += 1

		return array_has_geo

	block_drawn = 0

	def draw_block(block, x, y, z):
		x *= 16
		z *= 16

		global block_drawn

		it = np.nditer(block, flags=['multi_index'])
		while not it.finished:
			if it[0] == 1:
				block_drawn += 1
				render.geometry3d(it.multi_index[0] + x, it.multi_index[1] + y, it.multi_index[2] + z, cube)
			it.iternext()


	block_fetched = 0
	layer_size = 5


	class Layer:
		def __init__(self):
			self.layer = [None] * (layer_size * layer_size)

			self.old_pos = gs.Vector3()
			self.pos = gs.Vector3()

		def update(self, pos):
			self.pos = gs.Vector3(pos)

			if self.pos != self.old_pos:
				if self.pos.x > self.old_pos.x:
					for z in range(layer_size):
						for x in range(layer_size - 1):
							self.layer[x + z * layer_size] = self.layer[x + 1 + z * layer_size]
						self.layer[layer_size - 1 + z * layer_size] = None
				elif self.pos.x < self.old_pos.x:
					for z in range(layer_size):
						for x in range(layer_size - 1, 0, -1):
							self.layer[x + z * layer_size] = self.layer[x - 1 + z * layer_size]
						self.layer[0 + z * layer_size] = None

				if self.pos.z > self.old_pos.z:
					for x in range(layer_size):
						for z in range(layer_size - 1):
							self.layer[x + z * layer_size] = self.layer[x + (z + 1) * layer_size]
						self.layer[x + (layer_size - 1) * layer_size] = None
				elif self.pos.z < self.old_pos.z:
					for x in range(layer_size):
						for z in range(layer_size - 1, 0, -1):
							self.layer[x + z * layer_size] = self.layer[x + (z - 1) * layer_size]
						self.layer[x] = None

				# if self.pos.y != self.old_pos.y:  # FIXME
				# 	self.layer = [None] * (layer_size * layer_size)

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
					if self.layer[i] is None:
						self.layer[i] = get_block_simple(block_pos)
						block_fetched += 1
						return

					block_pos.x += 1

				block_pos.x -= layer_size
				block_pos.z += 1

		def draw(self):
			for z in range(layer_size):
				for x in range(layer_size):
					i = x + z * layer_size
					if self.layer[i] is not None:
						draw_block(self.layer[i], self.pos.x + x - (layer_size - 1) / 2, self.pos.y, self.pos.z + z - (layer_size - 1) / 2)


	layers = []
	for i in range(8):
		layers.append(Layer())

	old_pos = gs.Vector3()
	while not input.key_press(gs.InputDevice.KeyEscape):
		render.clear()

		if input.key_press(gs.InputDevice.KeyK):
			layer = [None] * (layer_size * layer_size)
			pos.y += 1
		if input.key_press(gs.InputDevice.KeyL):
			layer = [None] * (layer_size * layer_size)
			pos.y -= 1
		"""
		if input.key_press(gs.InputDevice.KeyO):
			pos.x += 1
		if input.key_press(gs.InputDevice.KeyI):
			pos.x -= 1
		"""

		dt_sec = clock.update()
		fps.update(dt_sec)
		render.set_camera3d(fps.pos.x, fps.pos.y, fps.pos.z, fps.rot.x, fps.rot.y, fps.rot.z)

		# pos -> block dans lequel on peux se deplacer
		pos.x = fps.pos.x // 16
		pos.y = (fps.pos.y - 20) // 1
		pos.z = fps.pos.z // 16

		if pos.y < old_pos.y:
			for i in range(len(layers) - 1):
				layers[i] = layers[i + 1]
			layers[-1] = Layer()
		elif pos.y > old_pos.y:
			for i in range(len(layers) - 1, 0, -1):
				layers[i] = layers[i - 1]
			layers[0] = Layer()

		old_pos = gs.Vector3(pos)

		#
		block_fetched, block_drawn = 0, 0

		for i, layer in enumerate(layers):
			layer.update(pos + gs.Vector3(0, -i, 0))
			layer.fill()
			layer.draw()

		render.text2d(0, 45, "FPS: %.2fHZ - BLOCK FETCHED: %d - BLOCK DRAWN: %d" % (1 / dt_sec, block_fetched, block_drawn), color=gs.Color.Red)
		render.text2d(0, 25, "FPS.X = %f, FPS.Z = %f" % (fps.pos.x, fps.pos.z), color=gs.Color.Red)
		render.text2d(0, 5, "POS.X = %f, POS.Z = %f" % (pos.x, pos.z), color=gs.Color.Red)

		render.flip()

finally:
	close_socket()

