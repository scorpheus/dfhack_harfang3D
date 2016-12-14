__author__ = 'scorpheus'

from dfhack_connect import *
import gs
# import geometry_iso
import blocks_builder
import update_dwarf

plus = gs.GetPlus()

gs.LoadPlugins(gs.get_default_plugins_path())

plus.CreateWorkers()


width, height = 1920, 1080
plus.RenderInit(width, height)
gs.MountFileDriver(gs.StdFileDriver(""))

blocks_builder.setup()

scn = plus.NewScene()

# sky_script = gs.LogicScript("@core/lua/sky_lighting.lua")
# sky_script.Set("time_of_day", 15.0)
# sky_script.Set("attenuation", 0.75)
# sky_script.Set("shadow_range", 1000.0) # 1km shadow range
# sky_script.Set("shadow_split", gs.Vector4(0.1, 0.2, 0.3, 0.4))
# scn.AddComponent(sky_script)

light_cam = plus.AddLight(scn, gs.Matrix4.TranslationMatrix(gs.Vector3(6, 200, -6)))
light_cam.GetLight().SetShadow(gs.Light.Shadow_None)

cam = plus.AddCamera(scn, gs.Matrix4.TranslationMatrix(gs.Vector3(112, 62, 112)))
cam.GetCamera().SetZoomFactor(gs.FovToZoomFactor(1.57))

# dwarf_geo = plus.CreateGeometry(plus.CreateCube(0.1, 0.6, 0.1, "iso.mat"))
dwarf_geo = plus.LoadGeometry("minecraft_assets/default_dwarf/default_dwarf.geo")

# get first dwarf position
unit_list = get_all_unit_list()
dwarf_pos = gs.Vector3(95, 95*blocks_builder.scale_unit_y, 150)
# get position on the first dwarf encounter
for unit in unit_list.creature_list:
	if unit:
		dwarf_pos = gs.Vector3(blocks_builder.map_info.block_size_x*16 - 16 - unit.pos_x, unit.pos_z*blocks_builder.scale_unit_y + 1, unit.pos_y)
		break

fps = gs.FPSController(dwarf_pos.x, dwarf_pos.y, dwarf_pos.z)
fps.SetRot(gs.Vector3(0.5, 0, 0))

block_drawn = 0
props_drawn = 0

# main loop
while not plus.IsAppEnded(plus.EndOnDefaultWindowClosed): #plus.EndOnEscapePressed |
	plus.Clear()

	dt_sec = plus.UpdateClock()
	fps.UpdateAndApplyToNode(cam, dt_sec)
	light_cam.GetTransform().SetPosition(fps.GetPos())

	# get the block info from df
	blocks_builder.update_block(cam)

	# draw the block
	big_block_visible = blocks_builder.draw_block(scn.GetRenderableSystem(), cam)

	# update unit draw
	with update_dwarf.mutex_dwarfs_pos:
		dwarf_scale = gs.Vector3(0.01, 0.01, 0.01)
		for dwarf in update_dwarf.dwarfs_pos.values():
			d_pos = dwarf[0]
			scn.GetRenderableSystem().DrawGeometry(dwarf_geo, gs.Matrix4.TransformationMatrix(gs.Vector3(blocks_builder.map_info.block_size_x * 16 - d_pos.x, d_pos.z * blocks_builder.scale_unit_y, d_pos.y), dwarf[1], dwarf_scale))

	big_block_available = 0
	with blocks_builder.mutex_array_world_big_block:
		for id, big_block in blocks_builder.array_world_big_block.items():
			if big_block["status"] == blocks_builder.status_ready:
				big_block_available += 1

	plus.Text2D(0, 45, "BIG BLOCK: %d, CACHE BLOCK: %d, BLOCK VISIBLE: %d" % (len(blocks_builder.array_world_big_block), big_block_available, big_block_visible), 16, gs.Color.Red)
	plus.Text2D(0, 25, "FPS.X = %f, FPS.Y = %f, FPS.Z = %f" % (fps.GetPos().x, fps.GetPos().y, fps.GetPos().z), 16, gs.Color.Red)

	plus.UpdateScene(scn, dt_sec)
	plus.Flip()

close_socket()