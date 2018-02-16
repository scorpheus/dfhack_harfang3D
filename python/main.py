__author__ = 'scorpheus'

import os, sys

# for the protobuf to be fast with c backend
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "cpp"


from dfhack_connect import *
import harfang as hg
from harfang_shortcut import *
import blocks_builder
import update_dwarf
import helper_2d

if getattr(sys, 'frozen', False):
    # frozen
	exe_path = os.path.dirname(sys.executable)
	dir_ = sys._MEIPASS
	hg.LoadPlugins(dir_)
else:
    # unfrozen
	exe_path = dir_ = os.path.dirname(os.path.realpath(__file__))
	hg.LoadPlugins()

sys.path.append(exe_path)

plus = hg.GetPlus()

plus.CreateWorkers()


width, height = 1024, 768
plus.RenderInit(width, height)
hg.MountFileDriver(hg.StdFileDriver())
hg.MountFileDriver(hg.StdFileDriver(dir_))
hg.MountFileDriver(hg.StdFileDriver(os.path.join(exe_path, "assets")), "@assets")
hg.MountFileDriver(hg.StdFileDriver(os.path.join(exe_path, "environment_kit")), "@environment_kit")
hg.MountFileDriver(hg.StdFileDriver(os.path.join(exe_path, "minecraft_assets")), "@minecraft_assets")

blocks_builder.setup()

helper_2d.font = hg.RasterFont("@assets/default.ttf", 16)
scn = plus.NewScene()

environment = hg.Environment()
scn.AddComponent(environment)

#sky_script = hg.LogicScript("@core/lua/sky_lighting.lua")
#sky_script.Set("time_of_day", 15.0)
#sky_script.Set("attenuation", 0.55)
#sky_script.Set("shadow_range", 10.0) # 1km shadow range
#sky_script.Set("shadow_split", hg.Vector4(0.1, 0.2, 0.3, 0.4))
#scn.AddComponent(sky_script)

plus.UpdateScene(scn, hg.time_from_sec_f(0.1))
plus.UpdateScene(scn, hg.time_from_sec_f(0.1))
#scn.GetNode("Sky Main Light").GetLight().SetShadow(hg.LightShadowNone)
#scn.GetNode("Sky Back Light").GetLight().SetShadow(hg.LightShadowNone)

light_cam = plus.AddLight(scn, mat4.TranslationMatrix(vec3(6, 200, -6)))
light_cam.GetLight().SetShadow(hg.LightShadowNone)

cam = plus.AddCamera(scn, mat4.TranslationMatrix(vec3(112, 62, 112)))
cam.GetCamera().SetZoomFactor(hg.FovToZoomFactor(1.57))

scene_simple_graphic = hg.SimpleGraphicSceneOverlay(False)
scene_simple_graphic.SetBlendMode(hg.BlendAlpha)
scene_simple_graphic.SetDepthWrite(False)
scn.AddComponent(scene_simple_graphic)

# get first dwarf position
unit_list = get_all_unit_list()
dwarf_pos = vec3(95, 95*blocks_builder.scale_unit_y, 150)
# get position on the first dwarf encounter
for unit in unit_list.creature_list:
	if unit:
		dwarf_pos = vec3(blocks_builder.map_info.block_size_x * 16 - unit.pos_x, unit.pos_z*blocks_builder.scale_unit_y + 1, unit.pos_y)
		break

fps = hg.FPSController(dwarf_pos.x, dwarf_pos.y, dwarf_pos.z)
fps.SetRot(vec3(0.5, 0, 0))

block_drawn = 0
props_drawn = 0

# main loop
while not plus.IsAppEnded():
	plus.Clear()
	dt_sec = plus.UpdateClock()

	scn.Update(dt_sec)

	fps.UpdateAndApplyToNode(cam, dt_sec)
	light_cam.GetTransform().SetPosition(fps.GetPos())

	# get the block info from df
	blocks_builder.update_block(cam)

	# draw the block
	count_big_block_visible = blocks_builder.draw_block(scn.GetRenderableSystem(), cam, scene_simple_graphic)

	# update unit draw
	update_dwarf.draw_dwarf(scn)

	plus.Text2D(0, 65, "FPS:{0}".format(int(1/hg.time_to_sec_f(dt_sec))))
	plus.Text2D(0, 45, "BIG BLOCK: %d, BLOCK VISIBLE: %d" % (len(blocks_builder.array_world_big_block), count_big_block_visible), 16, col.Red)
	plus.Text2D(0, 25, "FPS.X = %f, FPS.Y = %f, FPS.Z = %f" % (fps.GetPos().x, fps.GetPos().y, fps.GetPos().z), 16, col.Red)

	scn.WaitUpdate(True)
	scn.Commit()
	scn.WaitCommit(True)

	plus.Flip()
	plus.EndFrame()

close_socket()