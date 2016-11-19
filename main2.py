__author__ = 'scorpheus'

from dfhack_connect import *
import gs
import geometry_iso
import blocks_builder
from update_dwarf import *

plus = gs.GetPlus()

gs.LoadPlugins(gs.get_default_plugins_path())

plus.CreateWorkers()

plus.RenderInit(1024, 768)
gs.MountFileDriver(gs.StdFileDriver(""))

blocks_builder.setup()

scn = plus.NewScene()

sky_script = gs.LogicScript("@core/lua/sky_lighting.lua")
sky_script.Set("time_of_day", 15.0)
sky_script.Set("attenuation", 0.75)
sky_script.Set("shadow_range", 1000.0) # 1km shadow range
sky_script.Set("shadow_split", gs.Vector4(0.1, 0.2, 0.3, 0.4))
scn.AddComponent(sky_script)

cam = plus.AddCamera(scn, gs.Matrix4.TranslationMatrix(gs.Vector3(112, 62, 112)))
cam.GetCamera().SetZoomFactor(gs.FovToZoomFactor(1.57))


def fps_pos_in_front_2d(dist):
	world = gs.Matrix3.FromEuler(0, fps.GetRot().y, 0)
	return fps.GetPos() + world.GetZ() * dist


fps = gs.FPSController(90, 140*blocks_builder.scale_unit_y, 90)
fps.SetRot(gs.Vector3(0.5, 0, 0))

block_drawn = 0
props_drawn = 0

# get first dwarf position
# unit_list = get_all_unit_list()


# main loop
while not plus.KeyPress(gs.InputDevice.KeyEscape):
	plus.Clear()

	dt_sec = plus.UpdateClock()
	fps.UpdateAndApplyToNode(cam, dt_sec)
	# light_cam.GetTransform().SetPosition(fps.GetPos())

	# get the block info from df
	blocks_builder.update_block(cam)

	# draw the block
	blocks_builder.draw_block(scn.GetRenderableSystem())

	# blocks_builder.update_geo_block()

	# update unit draw
	# update_dwarf_pos()
	# dwarf_scale = gs.Vector3(0.01, 0.01, 0.01)
	# for dwarf in dwarfs_pos.values():
	# 	d_pos = dwarf[0]
	# 	scn.GetRenderableSystem().DrawGeometry(dwarf_geo, gs.Matrix4.TransformationMatrix(gs.Vector3(map_info.block_size_x*16 - d_pos.x+16, (d_pos.z)*scale_unit_y, d_pos.y), dwarf[1], dwarf_scale))

	# check if needed to remove block not used
	# blocks_builder.check_to_delete_far_block()

	big_block_available = 0
	block_available = 0
	for id, big_block in blocks_builder.array_world_big_block.items():
		if not big_block["to_update"]:
			big_block_available += 1
			block_available += len(big_block["blocks"])

	plus.Text2D(0, 45, "BIG BLOCK: %d, CACHE BLOCK: %d, BLOCK VISIBLE: %d" % (len(blocks_builder.array_world_big_block), big_block_available, block_available), 16, gs.Color.Red)
	plus.Text2D(0, 25, "FPS.X = %f, FPS.Y = %f, FPS.Z = %f" % (fps.GetPos().x, fps.GetPos().y, fps.GetPos().z), 16, gs.Color.Red)
	plus.Text2D(0, 65, "timeget = %f, time_parse = %f" % (time_get, time_parse), 16, gs.Color.Red)

	plus.UpdateScene(scn, dt_sec)
	plus.Flip()


close_socket()