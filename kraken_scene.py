__author__ = 'scorpheus'

import gs
import time

scene = 0
gpu = 0
scene_ready = False
render_system_async = 0


def InitialiseKraken():
	global scene
	global gpu
	global scene_ready
	global render_system_async

	gs.GetTaskSystem().CreateWorkers()

	egl = gs.EglRenderer()
	gpu = gs.GpuRendererAsync(egl)

	gs.GetFilesystem().Mount(gs.CFile("runtime"), "@core")
	gs.GetFilesystem().Mount(gs.CFile())

	render_system = gs.RenderSystem(egl)
	render_system_async = gs.RenderSystemAsync(render_system)

	gpu.Open(1280, 720)
	render_system_async.Initialize().wait()

	scene = gs.Scene()
	scene.SetupCoreSystemsAndComponents(render_system)
	scene_ready = scene.Load('scene/world_scene.xml', gs.SceneLoadContext(render_system))


def UpdateKraken():
	if scene_ready:
		scene.SetCurrentCamera(scene.GetNode("render_camera"))
		# scene.SetCurrentCamera(scene.GetNode("center_camera"))

		# Read-only
		scene.Update()
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
