__author__ = 'scorpheus'

import gs
import template_scene


class SubScene(template_scene.SceneTemplate):
	def on_frame_complete(self):
		self.render_system.GetRenderer().SetWorldMatrix(gs.Matrix4.Identity)
		gs.DrawBox(self.render_system, gs.MinMax(gs.Vector3(-10, -10, -10), gs.Vector3(10, 10, 10)), gs.Color.Red)

	def update(self):
		pass

scene = SubScene("pkg.core")
scene.open_window_and_initialize_scene(1024, 768)
scene.load_scene('scene/world_scene.scn')
scene.main_loop()