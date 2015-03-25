__author__ = 'scorpheus'

import gs
import template_scene

scene = None
red_list = []
blue_list = []


class SubScene(template_scene.SceneTemplate):
	def on_frame_complete(self):
		pass
		# self.render_system.GetRenderer().SetWorldMatrix(gs.Matrix4.Identity)

		# for red in red_list:
		# 	gs.DrawBox(self.render_system, red, gs.Color.Red)
		# for blue in blue_list:
		# 	gs.DrawBox(self.render_system, blue, gs.Color.Blue)


def InitialiseKraken():
	global scene
	scene = SubScene("pkg.core")
	scene.open_window_and_initialize_scene(1024, 768)
	scene.load_scene('scene/world_scene.scn')


def UpdateKraken():
	global scene
	scene.update()
	return scene.scene.IsReady()