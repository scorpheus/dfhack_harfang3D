__author__ = 'scorpheus'

from dfhack_connect import *
import gs
import gs.plus.render as render
import gs.plus.input as input
import gs.plus.camera as camera
import gs.plus.scene as scene
import gs.plus.clock as clock
import geometry_iso

import numpy as np

world_tile = np.full((255, 150, 255), 0)

corner_iso_array = {}

def update_block(df_block, block, corner_pos):
	x, z = 0, 0
	array_iso = np.empty((18, 3, 18))
	array_tile = np.empty((16, 16))

	if world_tile[corner_pos.x // 16][corner_pos.y + 1][corner_pos.z // 16] != 0:
		array_iso[:, 2, :] = world_tile[corner_pos.x // 16][corner_pos.y + 1][corner_pos.z // 16]

	for tile in df_block.tiles:
		if tile_type_list.tiletype_list[tile].shape in [remote_fortress.EMPTY] and\
			tile_type_list.tiletype_list[tile].material != remote_fortress.MAGMA:
			array_tile[x][z] = 0
		else:
			array_tile[x][z] = 1

		x += 1
		if x >= 16:
			x = 0
			z += 1

	array_iso[1:-1, 2, 1:-1] = array_tile

	world_tile[corner_pos.x // 16][corner_pos.y][corner_pos.z // 16] = array_tile

	block.object.SetGeometry(geometry_iso.create_iso(array_iso, 16, 3, 16, 0.1, "iso.mat"))
	block.transform.SetPosition(corner_pos)


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

	scn = scene.new_scene()
	scn.Load('scene/world_scene.scn', gs.SceneLoadContext(render.get_render_system()))
	scene.add_light(scn, gs.Matrix4.TranslationMatrix(gs.Vector3(6, 140, -6)))
	cam = scene.add_camera(scn, gs.Matrix4.TranslationMatrix(gs.Vector3(112, 110, 112)))
	cam.camera.SetZoomFactor(gs.FovToZoomFactor(1.57))
	fps = camera.fps_controller(112, 110, 112)

	# create blocks node
	blocks = []
	list_pos_to_update = []
	for block_x in range(3):
		for block_y in range(8):
			for block_z in range(3):
				blocks.append(scene.add_cube(scn))
				list_pos_to_update.append(gs.Vector3(16 * block_x, block_y, 16 * block_z))

	count = 0
	while not input.key_press(gs.InputDevice.KeyEscape):
		if scn.IsReady():
			for i in range(1):
				# check if there blocks outside the pos
				cam_pos = cam.transform.GetPosition() + gs.Vector3(-1.5 * 16, -10, -1.5*16)

				# Get blocks from df
				df_block = GetBlock(from_world_to_dfworld(cam_pos + list_pos_to_update[count]))

				if df_block is not None:
					corner_pos = gs.Vector3(df_block.map_x, df_block.map_z, df_block.map_y)
					update_block(df_block, blocks[count], corner_pos)

				count += 1
				if count >= len(blocks):
					count = 0

		dt_sec = clock.update()
		fps.update_and_apply_to_node(cam, dt_sec)
		scene.update_scene(scn, dt_sec)
		render.flip()

finally:
	close_socket()

