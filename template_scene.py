__author__ = 'scorpheus'

import gs
from math import *


def on_log(msgs):
	for i in range(msgs.GetSize()):
		print(msgs.GetMessage(i))


def on_script_error(event):
	print("Error in script '%s'\n\n%s" % (event.component.GetPath(), event.error))


class SceneTemplate:
	def __init__(self, path_pkg_core):

		# hook the engine log
		gs.GetOnLogSignal().Connect(on_log)

		# create workers for multithreading
		gs.GetTaskSystem().CreateWorkers()

		# mount the system file driver
		gs.GetFilesystem().Mount(gs.StdFileDriver(path_pkg_core), "@core")
		gs.GetFilesystem().Mount(gs.StdFileDriver())

		# create the renderer
		self.renderer = gs.EglRenderer()
		self.renderer_async = gs.GpuRendererAsync(self.renderer)

		# create the render system, which is used to draw through the renderer
		self.render_system = gs.RenderSystem(self.renderer)
		self.render_system_async = gs.RenderSystemAsync(self.render_system)

		self.mixer_async = gs.MixerAsync(gs.ALMixer())

		self.scene = None
		self.camera = None
		self.environment = None

		self.clock = gs.Clock()

	def __del__(self):
		self.scene.Dispose()
		self.render_system_async.Free().wait()
		self.renderer_async.Close().wait()

	def open_window_and_initialize_scene(self, width, height):
		# open a window and initialize the render_system
		self.renderer_async.Open(width, height)
		self.render_system_async.Initialize().wait()

		# setup input and get the keyboard device
		gs.GetInputSystem().SetHandle(self.renderer.GetCurrentOutputWindow().GetHandle())
		self.keyboard = gs.GetInputSystem().GetDevice("keyboard")

		self.setup_scene()

		self.add_camera_light()

		self.setup()

	def setup_scene(self):
		self.scene = gs.Scene()
		self.scene.SetupCoreSystemsAndComponents(self.render_system)
		self.physic_system = gs.BulletPhysicSystem()
		self.scene.AddNodeSystem(self.physic_system)

		# add a callback if the user want to draw with the rendersystem manually
		self.scene.GetRenderSignals().frame_complete_signal.Connect(self.on_frame_complete)

		# add an environment
		self.environment = gs.Environment()
		self.environment.SetBackgroundColor(gs.Color(0.560784, 0.768627, 0.976471, 0.0))
		self.environment.SetAmbientColor(gs.Color(0.323476, 0.229694, 0.488884, 0.0))
		self.environment.SetFogColor(gs.Color(0.561837, 0.767803, 0.977783, 0.0))
		self.scene.AddComponent(self.environment)

		# add lua system
		engine_env = gs.ScriptEngineEnv(self.render_system_async, self.renderer_async, self.mixer_async)

		lua_system = gs.LuaSystem(engine_env)
		lua_system.SetExecutionContext(gs.ScriptContextEditor)
		lua_system.Open()
		lua_system.GetScriptErrorSignal().Connect(on_script_error)
		self.scene.AddNodeSystem(lua_system)

	def load_scene(self, path_scene):
		self.scene.Load(path_scene, gs.SceneLoadContext(self.render_system))

	# add content in the scene (camera, light)
	def add_camera_light(self):
		# add a camera
		self.camera = gs.Node()
		self.camera.SetName("camera")
		transform = gs.Transform()
		self.camera.AddComponent(transform)

		camera = gs.Camera()
		camera.SetZNear(0.1)
		camera.SetZFar(50000)
		self.camera.AddComponent(camera)
		self.scene.AddNode(self.camera)

		# add this camera as the current one in scene
		self.scene.SetCurrentCamera(self.camera)

		# add light
		node = gs.Node()
		node.SetName("light")
		transform = gs.Transform()
		transform.SetPosition(gs.Vector3(0, 7, 0))
		transform.SetRotation(gs.Vector3(0.698, -1.3962, 0))
		node.AddComponent(transform)

		light = gs.Light()
		light.SetModel(gs.Light.Model_Linear)
		light.SetShadow(gs.Light.Shadow_Map)
		light.SetShadowRange(200)
		light.SetShadowDistribution(0.25)
		light.SetRange(500)
		light.SetVolumeRange(500)
		light.SetSpecularIntensity(1)
		light.SetConeAngle(0.261799)
		light.SetEdgeAngle(0.261799)
		light.SetSpecularColor(gs.Color(1, 1, 1))
		node.AddComponent(light)

		self.scene.AddNode(node)

	# setup anything before the main loop
	def setup(self):
		pass

	def update_camera(self):
		camera_item = self.scene.GetCurrentCamera()
		if camera_item is not None:
			right = camera_item.transform.GetCurrent().world.GetX()
			front = camera_item.transform.GetCurrent().world.GetZ()
			speed = 10.0 * self.clock.GetDelta().to_sec()

			keyboard_device = gs.GetInputSystem().GetDevice("keyboard")

			if keyboard_device.IsDown(gs.InputDevice.KeyUp) or keyboard_device.IsDown(gs.InputDevice.KeyZ) or keyboard_device.IsDown(gs.InputDevice.KeyW):
				camera_item.transform.SetPosition(camera_item.transform.GetPosition() + front * speed)

			elif keyboard_device.IsDown(gs.InputDevice.KeyDown) or keyboard_device.IsDown(gs.InputDevice.KeyS):
				camera_item.transform.SetPosition(camera_item.transform.GetPosition() - front * speed)

			elif keyboard_device.IsDown(gs.InputDevice.KeyLeft) or keyboard_device.IsDown(gs.InputDevice.KeyQ) or keyboard_device.IsDown(gs.InputDevice.KeyA):
				camera_item.transform.SetPosition(camera_item.transform.GetPosition() - right * speed)

			elif keyboard_device.IsDown(gs.InputDevice.KeyRight) or keyboard_device.IsDown(gs.InputDevice.KeyD):
				camera_item.transform.SetPosition(camera_item.transform.GetPosition() + right * speed)

			mouse_device = gs.GetInputSystem().GetDevice("mouse")
			if mouse_device.IsDown(gs.InputDevice.KeyButton0):
				old_mx = mouse_device.GetLastValue(gs.InputDevice.InputAxisX)
				old_my = mouse_device.GetLastValue(gs.InputDevice.InputAxisY)
				mx = mouse_device.GetValue(gs.InputDevice.InputAxisX)
				my = mouse_device.GetValue(gs.InputDevice.InputAxisY)
				euler = camera_item.transform.GetRotation() + gs.Vector3(my - old_my, mx - old_mx, 0) * radians(360)
				if euler.x < -pi:
					euler.x = -pi
				if euler.x > pi:
					euler.x = pi
				camera_item.transform.SetRotation(euler)

	# call by the engine, allow to draw using the render_system
	def on_frame_complete(self):
		pass

	# the user can update, modify object, gameplay by subclassing this function
	def update(self):
		pass

	# launch the main loop
	def main_loop(self):
		# update the scene
		while not self.keyboard.IsDown(gs.InputDevice.KeyEscape) and self.renderer.GetDefaultOutputWindow():
			self.clock.Update()

			self.update_camera()
			self.update()

			# Read-only
			self.scene.Update(gs.time(0.016))
			self.scene.WaitUpdate()

			# Read/write
			self.scene.Commit()
			self.scene.WaitCommit()

			if self.scene.IsReady():
				self.renderer_async.ShowFrame()

			self.renderer_async.UpdateOutputWindow()
			gs.GetInputSystem().Update()

