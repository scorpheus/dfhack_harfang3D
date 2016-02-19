__author__ = 'scorpheus'

from dfhack_connect import *
import gs
import gs.plus.render as render
import gs.plus.input as input
import gs.plus.scene as scene
import gs.plus.camera as camera
import gs.plus.clock as clock
import gs.plus.geometry as geometry
import geometry_iso
from update_dwarf import *

from collections import OrderedDict
import threading
import numpy as np


class building_type():
	NONE = -1
	Chair, Bed, Table, Coffin, FarmPlot, Furnace, TradeDepot, Shop, Door, Floodgate, Box, Weaponrack, \
	Armorstand, Workshop, Cabinet, Statue, WindowGlass, WindowGem, Well, Bridge, RoadDirt, RoadPaved, SiegeEngine, \
	Trap, AnimalTrap, Support, ArcheryTarget, Chain, Cage, Stockpile, Civzone, Weapon, Wagon, ScrewPump, \
	Construction, Hatch, GrateWall, GrateFloor, BarsVertical, BarsFloor, GearAssembly, AxleHorizontal, AxleVertical, \
	WaterWheel, Windmill, TractionBench, Slab, Nest, NestBox, Hive, Rollers = range(51)

scale_unit_y = 1.0

gs.LoadPlugins(gs.get_default_plugins_path())

gs.plus.create_workers()

def from_world_to_dfworld(new_pos):
	return gs.Vector3(new_pos.x, new_pos.z, new_pos.y)


def fps_pos_in_front_2d(dist):
	world = gs.Matrix3.FromEuler(0, fps.rot.y, 0)
	return fps.pos + world.GetZ() * dist

try:
	connect_socket()
	Handshake()
	# dfversion = GetDFVersion()
	map_info = GetMapInfo()

	# get once to use after (material list is huge)
	tile_type_list = GetTiletypeList()
	# material_list = GetMaterialList()

	render.init(1920, 1080, "pkg.core")
	gs.MountFileDriver(gs.StdFileDriver("."))

	scn = scene.new_scene()
	# add lua system
	engine_env = gs.ScriptEngineEnv(render.get_render_system_async(), render.get_renderer_async(), None)

	lua_system = gs.LuaSystem(engine_env)
	lua_system.SetExecutionContext(gs.ScriptContextAll )
	lua_system.Open()
	scn.AddSystem(lua_system)

	scn.Load('@core/scene_templates/scene.scn', gs.SceneLoadContext(render.get_render_system()))
	light_cam = scene.add_light(scn, gs.Matrix4.TranslationMatrix(gs.Vector3(6, 200, -6)))
	light_cam.GetLight().SetShadow(gs.Light.Shadow_None)
	# light_cam.GetLight().SetDiffuseIntensity(100)
	# light_cam.GetLight().SetDiffuseColor(gs.Color.Red)
	# light_cam.GetLight().SetRange(130)
	# light_cam.GetLight().SetVolumeRange(1000)

	cam = scene.add_camera(scn, gs.Matrix4.TranslationMatrix(gs.Vector3(112, 62, 112)))
	cam.GetCamera().SetZoomFactor(gs.FovToZoomFactor(1.57))

	fps = camera.fps_controller(128, 74*scale_unit_y, 64)
	fps.rot = gs.Vector3(0.5, 0, 0)

	# dwarf_geo = render.create_geometry(geometry.create_cube(0.1, 0.6, 0.1, "iso.mat"))
	dwarf_geo = render.load_geometry("minecraft_assets/default_dwarf/default_dwarf.geo")
	cube_geo = render.create_geometry(geometry.create_cube(1, 1*scale_unit_y, 1, "iso.mat"))

	pos = gs.Vector3(112//16, 62, 112//16)


	def hash_from_pos(x, y, z):
		return x + y * 2048 + z * 2048 * 2048


	def hash_from_layer(layer_pos, x, z):
		return hash_from_pos(layer_pos.x + x - (layer_size - 1) / 2, layer_pos.y, layer_pos.z + z - (layer_size - 1) / 2)


	geos = [render.load_geometry("environment_kit_inca/stone_high_03.geo"), render.load_geometry("environment_kit_inca/stone_high_01.geo")]
	building_geos = {building_type.Chair: None, building_type.Bed: None,
					 building_type.Table: {'g':render.load_geometry("environment_kit/geo-table.geo"), 'o':gs.Matrix4.Identity},
					 building_type.Coffin: None, building_type.FarmPlot: None, building_type.Furnace: None,
					 building_type.TradeDepot: None, building_type.Shop: None,
					 building_type.Door: {'g':render.load_geometry("environment_kit/geo-door.geo"), 'o':gs.Matrix4.Identity},
					 building_type.Floodgate: None,
					 building_type.Box: {'g':render.load_geometry("environment_kit_inca/chest_top.geo"), 'o':gs.Matrix4.Identity},
					 building_type.Weaponrack: None,
					 building_type.Armorstand: None, building_type.Workshop: None,
					 building_type.Cabinet: {'g':render.load_geometry("environment_kit/geo-bookshelf.geo"), 'o':gs.Matrix4.Identity},
					 building_type.Statue: {'g':render.load_geometry("environment_kit/geo-greece_column.geo"), 'o':gs.Matrix4.RotationMatrix(gs.Vector3(-1.57, 0, 0))},
					 building_type.WindowGlass: None, building_type.WindowGem: None,
					 building_type.Well: None, building_type.Bridge: None, building_type.RoadDirt: None,
					 building_type.RoadPaved: None, building_type.SiegeEngine: None, building_type.Trap: None,
					 building_type.AnimalTrap: None, building_type.Support: None, building_type.ArcheryTarget: None,
					 building_type.Chain: None, building_type.Cage: None, building_type.Stockpile: None,
					 building_type.Civzone: None,
					 building_type.Weapon: None, building_type.Wagon: None, building_type.ScrewPump: None,
					 building_type.Construction: {'g':render.load_geometry("environment_kit/geo-egypt_wall.geo"), 'o':gs.Matrix4.Identity},
					 building_type.Hatch: None, building_type.GrateWall: None, building_type.GrateFloor: None,
					 building_type.BarsVertical: None,
					 building_type.BarsFloor: None, building_type.GearAssembly: None,
					 building_type.AxleHorizontal: None, building_type.AxleVertical: None,
					 building_type.WaterWheel: None, building_type.Windmill: None, building_type.TractionBench: None,
					 building_type.Slab: None, building_type.Nest: None, building_type.NestBox: None,
					 building_type.Hive: None, building_type.Rollers: None}



	block_fetched = 0
	layer_size = 5
	cache_block = {}
	cache_block_props = {}
	cache_block_building = {}
	cache_block_mat = {}
	cache_geo_block = {}
	update_cache_block = {}
	update_cache_geo_block = {}
	counter_block_to_remove = {}

	old_pos = gs.Vector3()

	mats_path = ["empty.mat", "floor.mat", "magma.mat", "rock.mat", "water.mat", "tree.mat", "floor.mat", "floor.mat"]
	# precompile material
	# for mat in mats_path:
	# 	render.create_geometry(geometry.create_cube(0.1, 0.6, 0.1, mat))

	def parse_block(block, block_flow_size, block_liquid_type, block_building, block_pos):

		array_has_geo = np.full((17, 17), 0, np.int8)
		array_tile_mat_id = np.full((17, 17), 0, np.int8)
		array_props = []
		array_building = []

		x, z = 15, 0
		for tile, flow_size, liquid_type, building in zip(block, block_flow_size, block_liquid_type, block_building):
			if tile != 0:
				type = tile_type_list.tiletype_list[tile]

				# choose a material
				block_mat = 0
				if flow_size > 0:
					if liquid_type == Tile.Tile.MAGMA:
						block_mat = 2
					elif liquid_type == Tile.Tile.WATER:
						block_mat = 4
					array_has_geo[x, z] = 1
				elif type.shape == remote_fortress.FLOOR:
					block_mat = 1
					array_has_geo[x, z] = 0
				elif type.shape == remote_fortress.RAMP:
					block_mat = 6
					array_has_geo[x, z] = 0
				elif type.shape == remote_fortress.RAMP_TOP:
					block_mat = 7
					array_has_geo[x, z] = 0
				elif type.shape == remote_fortress.BOULDER:
					block_mat = 3
					array_has_geo[x, z] = 0
					array_props.append((gs.Vector3(block_pos.x*16 + x, block_pos.y, block_pos.z*16 + z), 0))
				elif type.shape == remote_fortress.PEBBLES:
					block_mat = 3
					array_has_geo[x, z] = 0
					array_props.append((gs.Vector3(block_pos.x*16 + x, block_pos.y, block_pos.z*16 + z), 1))
				elif type.shape == remote_fortress.WALL or type.shape == remote_fortress.FORTIFICATION:
					block_mat = 3
					array_has_geo[x, z] = 1
				# if type.material == remote_fortress.PLANT:
				# 	block_mat = 2
				elif type.shape == remote_fortress.SHRUB or type.shape == remote_fortress.SAPLING:
					block_mat = 1
					array_has_geo[x, z] = 0

				if type.material == remote_fortress.TREE_MATERIAL or type.shape == remote_fortress.TRUNK_BRANCH or\
					type.shape == remote_fortress.TWIG:
					block_mat = 5
					array_has_geo[x, z] = 1

				array_tile_mat_id[x, z] = block_mat

				# add props
				if building != -1:
					array_building.append((gs.Vector3(block_pos.x*16 + x, block_pos.y, block_pos.z*16 + z), building))

			x -= 1
			if x < 0:
				x = 15
				z += 1

		array_has_geo[:, -1] = array_has_geo[:, -2]
		array_has_geo[-1, :] = array_has_geo[-2, :]

		array_tile_mat_id[:, -1] = array_tile_mat_id[:, -2]
		array_tile_mat_id[-1, :] = array_tile_mat_id[-2, :]

		return array_has_geo, array_tile_mat_id, array_props, array_building

	def check_block_to_update():
		global block_fetched
		global update_cache_block

		# get the previous block asked (with different pos)
		array_pos, block, block_flow_size, block_liquid_type, block_building = GetBlockMemory()

		if block is not None:
			new_pos = gs.Vector3(float(map_info.block_size_x - array_pos[0]), float(array_pos[2]), float(array_pos[1]))

			# parse the return array
			current_block, current_block_mat, current_block_props, current_block_building = parse_block(block, block_flow_size, block_liquid_type, block_building, new_pos)

			# update neighbour array
			north_name = hash_from_pos(new_pos.x, new_pos.y, new_pos.z-1)
			if north_name in cache_block:
				cache_block[north_name][:, -1] = current_block[:, 0]
				cache_block_mat[north_name][:, -1] = current_block_mat[:, 0]
			south_name = hash_from_pos(new_pos.x, new_pos.y, new_pos.z+1)
			if south_name in cache_block:
				current_block[:, -1] = cache_block[south_name][:, 0]
				current_block_mat[:, -1] = cache_block_mat[south_name][:, 0]
			west_name = hash_from_pos(new_pos.x-1, new_pos.y, new_pos.z)
			if west_name in cache_block:
				cache_block[west_name][-1, :] = current_block[0, :]
				cache_block_mat[west_name][-1, :] = current_block_mat[0, :]
			east_name = hash_from_pos(new_pos.x+1, new_pos.y, new_pos.z)
			if east_name in cache_block:
				current_block[-1, :] = cache_block[east_name][0, :]
				current_block_mat[-1, :] = cache_block_mat[east_name][0, :]

			# register the block in the cache
			name_block = hash_from_pos(new_pos.x, new_pos.y, new_pos.z)
			cache_block[name_block] = current_block
			cache_block_mat[name_block] = current_block_mat
			cache_block_props[name_block] = current_block_props
			cache_block_building[name_block] = current_block_building

			# this block array is setup, ask the update the geo block
			update_cache_geo_block[name_block] = gs.Vector3(new_pos)
			if name_block in update_cache_block:
				update_cache_block.pop(name_block)
			block_fetched += 1

		#
		if len(update_cache_block) > 0:
			# send the pos to update
			pos_in_front = fps_pos_in_front_2d(2)
			name_pos_block = min(update_cache_block.items(), key=lambda t: (t[1].x-pos_in_front.x/16)**2 + ((t[1].y -pos_in_front.y/scale_unit_y)/1.5)**2 + (t[1].z - pos_in_front.z/16)**2)
			name_block, block_pos = name_pos_block[0], name_pos_block[1]
			_pos = gs.Vector3(block_pos)
			_pos.x = map_info.block_size_x - _pos.x
			SendPos(from_world_to_dfworld(_pos))

		# print(len(update_cache_block))

	def create_iso_geo_from_block(name_geo, upper_name_block, block, upper_block, block_pos):
		array_has_geo = np.empty((17, 2, 17), np.int8)
		array_has_geo[:, 0, :] = block
		array_has_geo[:, 1, :] = upper_block

		array_mats = np.empty((17, 2, 17), np.int8)
		array_mats[:, 0, :] = cache_block_mat[name_geo]
		array_mats[:, 1, :] = cache_block_mat[upper_name_block]

		return geometry_iso.create_iso_c(array_has_geo, 17, 2, 17, array_mats, 0.5, mats_path, block_pos)
		# return geometry_iso.create_iso(array_has_geo, 17, 2, 17, array_mats, 0.5, mats_path, name_geo)

	block_drawn = 0
	props_drawn = 0

	def draw_geo_block(geo_block, x, y, z):
		x *= 16
		z *= 16

		scn.GetRenderableSystem().DrawGeometry(geo_block, gs.Matrix4.TranslationMatrix(gs.Vector3(x+1, y*scale_unit_y, z)) * gs.Matrix4.ScaleMatrix(gs.Vector3(1, scale_unit_y, 1)))

		global block_drawn
		block_drawn += 1

	def draw_cube_block(name_block, pos_block):
		block = cache_block[name_block]
		for x in range(16):
			for z in range(16):
				if block[x, z] == 1:
					scn.GetRenderableSystem().DrawGeometry(cube_geo, gs.Matrix4.TransformationMatrix(gs.Vector3(pos_block.x*16+x+1, pos_block.y*scale_unit_y, pos_block.z*16+z), gs.Vector3(0, 0, 0)))

	def draw_props_in_block(name_block):
		for prop in cache_block_props[name_block]:
			scn.GetRenderableSystem().DrawGeometry(geos[prop[1]], gs.Matrix4.TransformationMatrix(gs.Vector3(prop[0].x+1, prop[0].y*scale_unit_y, prop[0].z), gs.Vector3(0, (name_block%628)*0.01, 0), gs.Vector3(0.25, 0.25, 0.25)))
			global props_drawn
			props_drawn += 1

	def draw_building_in_block(name_block):
		for building in cache_block_building[name_block]:
			if building_geos[building[1]] is not None:
				scn.GetRenderableSystem().DrawGeometry(building_geos[building[1]]["g"], gs.Matrix4.TransformationMatrix(gs.Vector3(building[0].x+1, building[0].y*scale_unit_y, building[0].z), gs.Vector3(0, 0, 0), gs.Vector3(0.25, 0.25, 0.25)) * building_geos[building[1]]["o"])
				global props_drawn
				props_drawn += 1


	class Layer:
		def __init__(self):
			self.pos = gs.Vector3()

		def update(self, new_pos):
			self.pos = gs.Vector3(new_pos)

		def fill(self):
			global update_cache_block

			block_pos = gs.Vector3()
			block_pos.x = self.pos.x - (layer_size - 1) / 2
			block_pos.y = self.pos.y
			block_pos.z = self.pos.z - (layer_size - 1) / 2

			for z in range(layer_size):
				for x in range(layer_size):
					name_block = hash_from_layer(self.pos, x, z)

					# if block not available or if it currently used a lot, then re update it
					if (name_block not in cache_block and name_block not in update_cache_block) or \
							(name_block in counter_block_to_remove and counter_block_to_remove[name_block][0] >= 700):
						update_cache_block[name_block] = gs.Vector3(block_pos)
						counter_block_to_remove[name_block] = [500, gs.Vector3(block_pos)]

					block_pos.x += 1
				block_pos.x -= layer_size
				block_pos.z += 1
			return False

		def draw(self):
			block_pos = gs.Vector3()
			block_pos.x = self.pos.x - (layer_size - 1) / 2
			block_pos.y = self.pos.y
			block_pos.z = self.pos.z - (layer_size - 1) / 2

			for z in range(layer_size):
				for x in range(layer_size):
					name_block = hash_from_layer(self.pos, x, z)
					if name_block in counter_block_to_remove:
						counter_block_to_remove[name_block][0] = counter_block_to_remove[name_block][0]+2 if counter_block_to_remove[name_block][0] < 1000 else 1000

					if name_block in cache_geo_block and cache_geo_block[name_block] is not None:
						draw_geo_block(cache_geo_block[name_block], block_pos.x, block_pos.y, block_pos.z)
						draw_props_in_block(name_block)
						draw_building_in_block(name_block)

					# if name_block in cache_block:
					# 	draw_cube_block(name_block, block_pos)

					block_pos.x += 1
				block_pos.x -= layer_size
				block_pos.z += 1


	layers = []
	for i in range(40):
		layers.append(Layer())

	def update_geo_block():
		global update_cache_geo_block
		global cache_geo_block

		if len(update_cache_geo_block) <= 0:
			return

		pos_in_front = fps_pos_in_front_2d(2)
		ordered_update_cache_geo = OrderedDict(sorted(update_cache_geo_block.items(), key=lambda t: (t[1].x-pos_in_front.x/16)**2 + ((t[1].y -pos_in_front.y/scale_unit_y)/1.5)**2 + (t[1].z - pos_in_front.z/16)**2))

		# get a not already updating Node
		for name_block, block_pos in iter(ordered_update_cache_geo.items()):
			current_layer_block_name = hash_from_pos(block_pos.x, block_pos.y, block_pos.z)
			upper_layer_block_name = hash_from_pos(block_pos.x, block_pos.y + 1, block_pos.z)

			if current_layer_block_name in cache_block and upper_layer_block_name in cache_block:
				def check_block_can_generate_geo(x, y, z):
					# can update the geo block because it has all the neighbour
					return hash_from_pos(x, y, z+1) in cache_block and hash_from_pos(x + 1, y, z) in cache_block

				if check_block_can_generate_geo(block_pos.x, block_pos.y, block_pos.z) and check_block_can_generate_geo(block_pos.x, block_pos.y + 1, block_pos.z):
					cache_geo_block[current_layer_block_name] = create_iso_geo_from_block(current_layer_block_name, upper_layer_block_name, cache_block[current_layer_block_name], cache_block[upper_layer_block_name], block_pos)
					update_cache_geo_block.pop(current_layer_block_name)
					break

	def check_to_delete_far_block():
		global cache_block, cache_block_props, cache_block_building, cache_block_mat, cache_geo_block, update_cache_block, update_cache_geo_block, counter_block_to_remove
		for name, counter_pos in list(counter_block_to_remove.items()):
			counter_block_to_remove[name][0] -= 1
			if counter_block_to_remove[name][0] < 0: # too far , remove this block fromeverywhere
				#check the 2 around are disactivated
				temp_pos = counter_block_to_remove[name][1]
				name_west = hash_from_pos(temp_pos.x - 1, temp_pos.y, temp_pos.z)
				name_north = hash_from_pos(temp_pos.x, temp_pos.y, temp_pos.z - 1)
				if (name_west not in counter_block_to_remove or counter_block_to_remove[name_west][0] < 0) and (name_north not in counter_block_to_remove or counter_block_to_remove[name_north][0] < 0):
					counter_block_to_remove.pop(name)
					if name in cache_block:
						cache_block.pop(name)
					if name in cache_block_props:
						cache_block_props.pop(name)
					if name in cache_block_building:
						cache_block_building.pop(name)
					if name in cache_block_mat:
						cache_block_mat.pop(name)
					if name in cache_geo_block:
						cache_geo_block.pop(name)
					if name in update_cache_block:
						update_cache_block.pop(name)
					if name in update_cache_geo_block:
						update_cache_geo_block.pop(name)

	# def on_frame_complete():
	# 	state = render.get_render_system().GetViewState()
	# 	gs.DrawStateCacheStats(render.get_render_system(), render.__cache_font(render.get_font(), 12), 0, 600)
	# 	render.get_render_system_async().DrawRenderSystemStats(render.__cache_font(render.get_font(), 12), 0, 300)
	# 	render.get_render_system().SetViewState(state)
	#
	# scn.GetRenderSignals().frame_complete_signal.Connect(on_frame_complete)

	# main loop
	while not input.key_press(gs.InputDevice.KeyEscape):
		render.clear()

		dt_sec = clock.update()
		fps.update_and_apply_to_node(cam, dt_sec)
		light_cam.GetTransform().SetPosition(fps.pos)

		# pos -> blocks dans lequel on peux se deplacer
		pos.x = fps.pos.x // 16
		pos.y = fps.pos.y // scale_unit_y
		pos.z = fps.pos.z // 16

		#
		if pos.y > old_pos.y:
			for i in range(len(layers) - 1):
				layers[i] = layers[i + 1]
			layers[-1] = Layer()
		elif pos.y < old_pos.y:
			for i in range(len(layers) - 1, 0, -1):
				layers[i] = layers[i - 1]
			layers[0] = Layer()

		old_pos = gs.Vector3(pos)

		#
		block_fetched, block_drawn, props_drawn = 0, 0, 0

		for i, layer in enumerate(layers):
			layer.update(pos + gs.Vector3(0, i - len(layers) // 2, 0))
			layer.fill()
			layer.draw()

		# get the block info from df
		check_block_to_update()
		#
		update_geo_block()

		# update unit draw
		# update_dwarf_pos()
		# for dwarf in dwarfs_pos.values():
		# 	d_pos = dwarf[0]
		# 	scn.GetRenderableSystem().DrawGeometry(dwarf_geo, gs.Matrix4.TransformationMatrix(gs.Vector3(map_info.block_size_x*16 - d_pos.x+16, (d_pos.z)*scale_unit_y, d_pos.y), dwarf[1], gs.Vector3(0.01, 0.01, 0.01)))

		# check if needed to remove block not used
		check_to_delete_far_block()

		render.text2d(0, 65, "CACHE GEO: %d - CACHE BLOCK: %d" % (len(cache_geo_block), len(cache_block)), color=gs.Color.Red)
		render.text2d(0, 45, "BLOCK FETCHED: %d - BLOCK DRAWN: %d - PROPS DRAWN: %d - FPS: %.2fHZ" % (block_fetched, block_drawn, props_drawn, 1 / dt_sec), color=gs.Color.Red)
		render.text2d(0, 25, "FPS.X = %f, FPS.Z = %f" % (fps.pos.x, fps.pos.z), color=gs.Color.Red)
		render.text2d(0, 5, "POS.X = %f, POS.Y = %f, POS.Z = %f" % (pos.x, pos.y, pos.z), color=gs.Color.Red)

		scene.update_scene(scn, dt_sec)
		render.flip()

finally:
	close_socket()

#