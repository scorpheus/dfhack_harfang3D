__author__ = 'scorpheus'

from dfhack_connect import *
import gs
import blocks_builder
import update_dwarf
import os

# for the protobuf to be fast with c backend
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "cpp"

plus = gs.GetPlus()

gs.LoadPlugins(gs.get_default_plugins_path())

plus.CreateWorkers()


width, height = 1920, 1080
plus.RenderInit(width, height)
gs.MountFileDriver(gs.StdFileDriver(""))

blocks_builder.setup()

scn = plus.NewScene()

sky_script = gs.LogicScript("@core/lua/sky_lighting.lua")
sky_script.Set("time_of_day", 15.0)
sky_script.Set("attenuation", 0.55)
sky_script.Set("shadow_range", 10.0) # 1km shadow range
sky_script.Set("shadow_split", gs.Vector4(0.1, 0.2, 0.3, 0.4))
scn.AddComponent(sky_script)

plus.UpdateScene(scn, gs.time(0.1))
plus.UpdateScene(scn, gs.time(0.1))
scn.GetNode("Sky Main Light").GetLight().SetShadow(gs.Light.Shadow_None)
scn.GetNode("Sky Back Light").GetLight().SetShadow(gs.Light.Shadow_None)

light_cam = plus.AddLight(scn, gs.Matrix4.TranslationMatrix(gs.Vector3(6, 200, -6)))
light_cam.GetLight().SetShadow(gs.Light.Shadow_None)

cam = plus.AddCamera(scn, gs.Matrix4.TranslationMatrix(gs.Vector3(112, 62, 112)))
cam.GetCamera().SetZoomFactor(gs.FovToZoomFactor(1.57))

scene_simple_graphic = gs.SimpleGraphicSceneOverlay(False)
scene_simple_graphic.SetBlendMode(gs.BlendAlpha)
scene_simple_graphic.SetDepthWrite(False)
scn.AddComponent(scene_simple_graphic)

# get first dwarf position
unit_list = get_all_unit_list()
dwarf_pos = gs.Vector3(95, 95*blocks_builder.scale_unit_y, 150)
# get position on the first dwarf encounter
for unit in unit_list.creature_list:
	if unit:
		dwarf_pos = gs.Vector3(blocks_builder.map_info.block_size_x * 16 - unit.pos_x, unit.pos_z*blocks_builder.scale_unit_y + 1, unit.pos_y)
		break

fps = gs.FPSController(dwarf_pos.x, dwarf_pos.y, dwarf_pos.z)
fps.SetRot(gs.Vector3(0.5, 0, 0))

block_drawn = 0
props_drawn = 0

# main loop
while not plus.IsAppEnded(plus.EndOnDefaultWindowClosed): #plus.EndOnEscapePressed |
	plus.Clear()
	dt_sec = plus.UpdateClock()

	scn.Update(dt_sec)

	fps.UpdateAndApplyToNode(cam, dt_sec)
	light_cam.GetTransform().SetPosition(fps.GetPos())

	# get the block info from df
	blocks_builder.update_block(cam)

	# draw the block
	big_block_visible = blocks_builder.draw_block(scn.GetRenderableSystem(), cam, scene_simple_graphic)

	# update unit draw
	update_dwarf.draw_dwarf(scn)

	plus.Text2D(0, 65, "FPS:{0}".format(int(1/dt_sec.to_sec())))
	plus.Text2D(0, 45, "BIG BLOCK: %d, BLOCK VISIBLE: %d" % (len(blocks_builder.array_world_big_block), big_block_visible), 16, gs.Color.Red)
	plus.Text2D(0, 25, "FPS.X = %f, FPS.Y = %f, FPS.Z = %f" % (fps.GetPos().x, fps.GetPos().y, fps.GetPos().z), 16, gs.Color.Red)

	scn.WaitUpdate(True)
	scn.Commit()
	scn.WaitCommit(True)
	plus.Flip()

close_socket()