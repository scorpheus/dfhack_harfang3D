__author__ = 'scorpheus'

import gs
import time
import math

scene = 0
gpu = 0
scene_ready = False
render_system_async = 0
mixer_async = 0
lua_system = 0
engine_env = 0


def on_log(msg, prefix, details):
	print('%s: %s' % ('log' if prefix == '' else prefix, msg))
	if details != '':
		print('	%s' % details)

def on_script_error(event):
	print("Error in script '%s'\n\n%s" % (event.component.GetPath(), event.error))



def InitialiseKraken():
	global scene
	global gpu
	global scene_ready
	global render_system_async
	global mixer_async
	global lua_system
	global engine_env

	# hook the engine log
	# gs.GetOnLogSignal().Connect(on_log)

	gs.GetTaskSystem().CreateWorkers()

	egl = gs.EglRenderer()
	gpu = gs.GpuRendererAsync(egl)

	gs.GetFilesystem().Mount(gs.StdFileDriver("runtime"), "@core")
	gs.GetFilesystem().Mount(gs.StdFileDriver())

	render_system = gs.RenderSystem(egl)
	render_system_async = gs.RenderSystemAsync(render_system)

	mixer = gs.ALMixer()
	mixer_async = gs.MixerAsync(mixer)


	gpu.Open(1280, 720)
	render_system_async.Initialize().wait()

	gs.GetInputSystem().SetHandle(gpu.GetDefaultOutputWindow().GetHandle())

	scene = gs.Scene()
	scene.SetupCoreSystemsAndComponents(render_system)
	scene_ready = scene.Load('scene/world_scene.xml', gs.SceneLoadContext(render_system))

	engine_env = gs.ScriptEngineEnv(render_system_async, gpu, mixer_async)

	lua_system = gs.LuaSystem(engine_env)
	lua_system.SetExecutionContext(gs.ScriptContextEditor)
	lua_system.Open()
	lua_system.GetScriptErrorSignal().Connect(on_script_error)
	scene.AddNodeSystem(lua_system)


def UpdateCamera():

	camera_item = scene.GetNode("render_camera")
	if camera_item is not None:
		vec_dir = camera_item.transform.GetRotation()
		speed = 1.0

		gs.GetInputSystem().Update()
		keyboard_device = gs.GetInputSystem().GetDevice("keyboard")

		if keyboard_device.IsDown(gs.InputDevice.KeyUp) or keyboard_device.IsDown(gs.InputDevice.KeyZ) or keyboard_device.IsDown(gs.InputDevice.KeyW):
			camera_item.transform.SetPosition(camera_item.transform.GetPosition() + gs.Vector3(math.sin(vec_dir.y), -math.sin(vec_dir.x), math.cos(-vec_dir.y))*speed)

		elif keyboard_device.IsDown(gs.InputDevice.KeyDown) or keyboard_device.IsDown(gs.InputDevice.KeyS):
			camera_item.transform.SetPosition(camera_item.transform.GetPosition() - gs.Vector3(math.sin(vec_dir.y), -math.sin(vec_dir.x), math.cos(-vec_dir.y))*speed)

		elif keyboard_device.IsDown(gs.InputDevice.KeyLeft) or keyboard_device.IsDown(gs.InputDevice.KeyQ) or keyboard_device.IsDown(gs.InputDevice.KeyA):
			camera_item.transform.SetPosition(camera_item.transform.GetPosition() - gs.Vector3(math.cos(vec_dir.y), 0.0, math.sin(-vec_dir.y))*speed)

		elif keyboard_device.IsDown(gs.InputDevice.KeyRight) or keyboard_device.IsDown(gs.InputDevice.KeyD):
			camera_item.transform.SetPosition(camera_item.transform.GetPosition() + gs.Vector3(math.cos(vec_dir.y), 0.0, math.sin(-vec_dir.y))*speed)

		mouse_device = gs.GetInputSystem().GetDevice("mouse")
		if mouse_device.IsDown(gs.InputDevice.KeyButton0):
			old_mx = mouse_device.GetLastValue(gs.InputDevice.InputAxisX)
			old_my = mouse_device.GetLastValue(gs.InputDevice.InputAxisY)
			mx = mouse_device.GetValue(gs.InputDevice.InputAxisX)
			my = mouse_device.GetValue(gs.InputDevice.InputAxisY)
			euler = camera_item.transform.GetRotation() + gs.Vector3(my - old_my, mx - old_mx, 0) * math.radians(360)
			if euler.x < -math.pi:
				euler.x = -math.pi
			if euler.x > math.pi:
				euler.x = math.pi
			camera_item.transform.SetRotation(euler)


def UpdateKraken():
	if scene_ready:
		scene.SetCurrentCamera(scene.GetNode("render_camera"))
		# scene.SetCurrentCamera(scene.GetNode("center_camera"))

		UpdateCamera()

		# Read-only
		scene.Update(gs.time(0.016))
		scene.WaitUpdate()

		# Read/write
		scene.Commit()
		scene.WaitCommit()

		gpu.ShowFrame()
		gpu.UpdateOutputWindow()


def GetGeo(name):
	return render_system_async.LoadGeometry(name)


def CreateCube(pos):

	# add camera
	node = gs.Node()
	node.SetName("cube")

	transform = gs.Transform()
	transform.SetPosition(pos)
	node.AddComponent(transform)

	render_geo = render_system_async.LoadGeometry('scene/assets/geo-cube.xml', True)
	object = gs.Object()
	object.SetGeometry(render_geo)
	node.AddComponent(object)

	#
	# script = gs.Script()
	# script.SetPath("@core/lua/cube.lua")
	# node.AddComponent(script)

	scene.AddNode(node)

	return node
