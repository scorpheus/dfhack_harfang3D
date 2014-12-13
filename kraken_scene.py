__author__ = 'scorpheus'

import gs
import time

scene = 0
gpu = 0
scene_ready = False
render_system = 0


def InitialiseKraken():
	global scene
	global gpu
	global scene_ready
	global render_system

	gpu = gs.EglRenderer()
	gpu.Open(1280, 720)

	gs.GetFilesystem().Mount(gs.CFile("runtime"), "@core")
	gs.GetFilesystem().Mount(gs.CFile())

	render_system = gs.RenderSystem(gpu)
	render_system.Initialize()

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
	return render_system.LoadGeometry(name)


def CreateCube(pos):

	# add camera
	node = gs.Node()
	node.SetName("cube")

	transform = gs.Transform()
	transform.SetPosition(pos)
	node.AddComponent(transform)

	render_geo = render_system.LoadGeometry('scene/assets/geo-cube.xml')
	object = gs.Object()
	object.SetGeometry(render_geo)
	node.AddComponent(object)

	#
	# script = gs.Script()
	# script.SetPath("@core/lua/cube.lua")
	# node.AddComponent(script)


	scene.AddNode(node)

	return node
