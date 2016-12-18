__author__ = 'scorpheus'

from dfhack_connect import *
import gs
import threading
import numpy as np
from helpers import *
import update_dwarf
import geometry_iso
import math
from iso_mesh_from_big_block import make_big_block_iso
import os
import noise
import xmltodict


plus = gs.GetPlus()

map_info = None
df_tile_type_list = None
material_list = None
material_list_color = None

building_geos = None
tile_geos = None
ramp_geos = {}
render_geos = []  # contains all the geos to draw

scale_unit_y = 1.0
visible_area_length = 15

mutex_array_world_big_block = threading.Lock()
array_world_big_block = {}


class building_type():
	NONE = -1
	Chair, Bed, Table, Coffin, FarmPlot, Furnace, TradeDepot, Shop, Door, Floodgate, Box, Weaponrack, \
	Armorstand, Workshop, Cabinet, Statue, WindowGlass, WindowGem, Well, Bridge, RoadDirt, RoadPaved, SiegeEngine, \
	Trap, AnimalTrap, Support, ArcheryTarget, Chain, Cage, Stockpile, Civzone, Weapon, Wagon, ScrewPump, \
	Construction, Hatch, GrateWall, GrateFloor, BarsVertical, BarsFloor, GearAssembly, AxleHorizontal, AxleVertical, \
	WaterWheel, Windmill, TractionBench, Slab, Nest, NestBox, Hive, Rollers = range(51)


class tile_type():  # begin by the struct of remote_fortress.TiletypeShape
	NONE = -1
	EMPTY, FLOOR, BOULDER, PEBBLES, WALL, FORTIFICATION, STAIR_UP, STAIR_DOWN, STAIR_UPDOWN, RAMP, RAMP_TOP, BROOK_BED, \
	BROOK_TOP, TREE_SHAPE, SAPLING, SHRUB, ENDLESS_PIT, BRANCH, TRUNK_BRANCH, TWIG, WATER, MAGMA = range(22)


def create_colors_from_xml():
	colors_from_xml = {}

	with open("assets/colors/index.txt", "r") as index:
		xmls = index.read().splitlines()

	for color_path in xmls:
		if not color_path.startswith("#"):
			with open(os.path.join("assets/colors", color_path)) as fd:
				doc = xmltodict.parse(fd.read())
				for color in doc["colors"]["color"]:
					c = (int(color["@red"])/255, int(color["@green"])/255, int(color["@blue"])/255)
					if type(color["material"]) is list:
						for token in color["material"]:
							colors_from_xml[token["@token"]] = c
					elif "@token" in color["material"]:
						colors_from_xml[color["material"]["@token"]] = c
					else:
						value_material = color["material"]["@value"]
						def get_token(value):
							if value_material == "Inorganic":
								return "INORGANIC:"+value.upper()
							else:
								return "PLANT:"+value.upper()+":"+value_material.upper()

						if "subtype" not in color["material"]:
							colors_from_xml[color["material"]["@value"]] = c
						elif type(color["material"]["subtype"]) is list:
							for subtype in color["material"]["subtype"]:
								colors_from_xml[get_token(subtype["@value"])] = c
						elif "@value" in color["material"]["subtype"]:
							colors_from_xml[get_token(color["material"]["subtype"]["@value"])] = c

	return colors_from_xml


def setup():
	global map_info, df_tile_type_list, material_list, material_list_color, tile_geos, building_geos

	connect_socket()
	handshake()
	# dfversion = get_df_version()
	map_info = get_map_info()
	reset_map_hashes()

	# get once to use after (material list is huge)
	df_tile_type_list = get_tiletype_list()
	# plant_list = get_plant_raw_list()
	material_list = get_material_list()
	material_list_color = {}
	colors_from_xml = create_colors_from_xml()
	for mat in material_list.material_list:
		if mat.mat_pair.mat_type not in material_list_color:
			material_list_color[mat.mat_pair.mat_type] = {}

		color = mat.state_color
		color = (color.red/255, color.green/255, color.blue/255)

		if mat.id in colors_from_xml:
			color = colors_from_xml[mat.id]
		elif mat.id.startswith("PLANT:"):
			id = mat.id.split(":")
			if len(id) == 3:
				id = id[0]+":*:"+id[2]
				if id in colors_from_xml:
					color = colors_from_xml[id]
				else:
					id = mat.id.split(":")
					id = id[0]+":"+id[1]+":WOOD"
					if id in colors_from_xml:
						color = colors_from_xml[id]

		material_list_color[mat.mat_pair.mat_type][mat.mat_pair.mat_index] = color

	building_def_list = get_building_def_list()

	building_geos = {building_type.Chair: None, building_type.Bed: None,
					 building_type.Table: {'g': plus.LoadGeometry("environment_kit/geo-table.geo"), 'o': gs.Matrix4.Identity},
					 building_type.Coffin: None, building_type.FarmPlot: None, building_type.Furnace: None,
					 building_type.TradeDepot: None, building_type.Shop: None,
					 building_type.Door: {'g': plus.LoadGeometry("environment_kit/geo-door.geo"), 'o': gs.Matrix4.Identity},
					 building_type.Floodgate: None,
					 building_type.Box: {'g': plus.LoadGeometry("environment_kit_inca/chest_top.geo"), 'o': gs.Matrix4.Identity},
					 building_type.Weaponrack: None,
					 building_type.Armorstand: None,
					 building_type.Workshop: {'g': plus.LoadGeometry("environment_kit/geo-bookshelf.geo"), 'o': gs.Matrix4.Identity},
					 building_type.Cabinet: {'g': plus.LoadGeometry("environment_kit/geo-bookshelf.geo"), 'o': gs.Matrix4.Identity},
					 building_type.Statue: {'g': plus.LoadGeometry("environment_kit/geo-greece_column.geo"), 'o': gs.Matrix4.RotationMatrix(gs.Vector3(-1.57, 0, 0))},
					 building_type.WindowGlass: None, building_type.WindowGem: None,
					 building_type.Well: None, building_type.Bridge: None, building_type.RoadDirt: None,
					 building_type.RoadPaved: None, building_type.SiegeEngine: None, building_type.Trap: None,
					 building_type.AnimalTrap: None, building_type.Support: None, building_type.ArcheryTarget: None,
					 building_type.Chain: None, building_type.Cage: None, building_type.Stockpile: None,
					 building_type.Civzone: None,
					 building_type.Weapon: None, building_type.Wagon: None, building_type.ScrewPump: None,
					 building_type.Construction: {'g': plus.LoadGeometry("environment_kit/geo-egypt_wall.geo"), 'o': gs.Matrix4.Identity},
					 building_type.Hatch: None, building_type.GrateWall: None, building_type.GrateFloor: None,
					 building_type.BarsVertical: None,
					 building_type.BarsFloor: None, building_type.GearAssembly: None,
					 building_type.AxleHorizontal: None, building_type.AxleVertical: None,
					 building_type.WaterWheel: None, building_type.Windmill: None, building_type.TractionBench: None,
					 building_type.Slab: None, building_type.Nest: None, building_type.NestBox: None,
					 building_type.Hive: None, building_type.Rollers: None}

	# precompile material
	tile_geos = {
		tile_type.NONE:           {"core_g": None, "render_g": None, "o": gs.Matrix4.Identity},
		tile_type.EMPTY:          {"core_g": None, "render_g": None, "o": gs.Matrix4.Identity},
		tile_type.FLOOR:          {"core_g": plus.CreateCube(1.0, 0.1 * scale_unit_y, 1.0, "assets/floor.mat"), "render_g": None, "o": gs.Matrix4.TranslationMatrix((0, -0.45 * scale_unit_y, 0))},
		tile_type.BOULDER:        {"core_g": None, "render_g": plus.LoadGeometry("environment_kit_inca/stone_high_03.geo"), "o": gs.Matrix4.TransformationMatrix((0, -0.5, 0), (0, 0, 0), (0.1, 0.1, 0.1))},
		tile_type.PEBBLES:        {"core_g": None, "render_g": plus.LoadGeometry("environment_kit_inca/stone_high_01.geo"), "o": gs.Matrix4.TransformationMatrix((0, -0.5, 0), (0, 0, 0), (0.1, 0.1, 0.1))},
		tile_type.WALL:           {"core_g": plus.CreateCube(1.0, 1.0 * scale_unit_y, 1.0, "assets/rock.mat"), "render_g": None, "o": gs.Matrix4.Identity},
		tile_type.FORTIFICATION:  {"core_g": plus.CreateCube(1.0, 1.0 * scale_unit_y, 1.0, "assets/rock.mat"), "render_g": None, "o": gs.Matrix4.Identity},
		tile_type.STAIR_UP:       {"core_g": None, "render_g": None, "o": gs.Matrix4.Identity},
		tile_type.STAIR_DOWN:     {"core_g": None, "render_g": None, "o": gs.Matrix4.Identity},
		tile_type.STAIR_UPDOWN:   {"core_g": None, "render_g": None, "o": gs.Matrix4.Identity},
		tile_type.RAMP:           {"core_g": None, "render_g": None, "o": gs.Matrix4.Identity},       # ramp will build after
		tile_type.RAMP_TOP:       {"core_g": None, "render_g": None, "o": gs.Matrix4.Identity},
		tile_type.BROOK_BED:      {"core_g": None, "render_g": None, "o": gs.Matrix4.Identity},
		tile_type.BROOK_TOP:      {"core_g": None, "render_g": None, "o": gs.Matrix4.Identity},
		tile_type.TREE_SHAPE:     {"core_g": None, "render_g": None, "o": gs.Matrix4.Identity},
		tile_type.SAPLING:        {"core_g": plus.CreateCube(1.0, 1.0 * scale_unit_y, 1.0, "assets/floor.mat"), "render_g": None, "o": gs.Matrix4.Identity},
		tile_type.SHRUB:          {"core_g": plus.CreateCube(1.0, 1.0 * scale_unit_y, 1.0, "assets/floor.mat"), "render_g": None, "o": gs.Matrix4.Identity},
		tile_type.ENDLESS_PIT:    {"core_g": None, "render_g": None, "o": gs.Matrix4.Identity},
		tile_type.BRANCH:         {"core_g": plus.CreateCube(1.0, 1.0 * scale_unit_y, 1.0, "assets/tree.mat"), "render_g": None, "o": gs.Matrix4.Identity},
		tile_type.TRUNK_BRANCH:   {"core_g": plus.CreateCube(1.0, 1.0 * scale_unit_y, 1.0, "assets/tree.mat"), "render_g": None, "o": gs.Matrix4.Identity},
		tile_type.TWIG:           {"core_g": plus.CreateCube(1.0, 1.0 * scale_unit_y, 1.0, "assets/tree.mat"), "render_g": None, "o": gs.Matrix4.Identity},
		tile_type.WATER:          {"core_g": plus.CreateCube(1.0, 1.0 * scale_unit_y, 1.0, "assets/water.mat"), "render_g": None, "o": gs.Matrix4.Identity},
		tile_type.MAGMA:          {"core_g": plus.CreateCube(1.0, 1.0 * scale_unit_y, 1.0, "assets/magma.mat"), "render_g": None, "o": gs.Matrix4.Identity},
	}

	# core_geo to render_geo
	for id, geo in tile_geos.items():
		if geo["core_g"] is not None:
			geo["render_g"] = plus.CreateGeometry(geo["core_g"])
			geo["geos_color"] = {}

	# give id_geo to building
	for id, building in building_geos.items():
		if building is not None:
			render_geos.append({"g": building["g"], "o": building["o"]})
			building["id_geo"] = len(render_geos)-1

	for id, geo in tile_geos.items():
		if geo["render_g"] is not None:
			render_geos.append({"g": geo["render_g"], "o": geo["o"]})
			geo["id_geo"] = len(render_geos)-1


def parse_block_building(fresh_block, array_geos_worlds, tiles):
	# clean building
	for id, building in building_geos.items():
		if building is not None and "id_geo" in building:
			array_geos_worlds[building["id_geo"]] = []

	# parse building
	for building in fresh_block.buildings:
		if building_geos[building.building_type.building_type] is not None and "id_geo" in building_geos[building.building_type.building_type]:
			tile_pos = from_dfworld_to_world(gs.Vector3(map_info.block_size_x * 16 - building.pos_x_min, building.pos_y_min * scale_unit_y, building.pos_z_min))
			m = gs.Matrix4.TranslationMatrix(tile_pos) * gs.Matrix4.TransformationMatrix((-1, -0.45, 0), (0, 0, 0), (0.25, 0.25, 0.25))
			array_geos_worlds[building_geos[building.building_type.building_type]["id_geo"]].append(m * building_geos[building.building_type.building_type]["o"])

	return array_geos_worlds, tiles


def parse_block_only_water_magma(fresh_block, array_geos_worlds, tiles, iso_array, iso_array_mat):
	world_block_pos = from_dfworld_to_world(gs.Vector3(map_info.block_size_x*16-16 - fresh_block.map_x, fresh_block.map_y, fresh_block.map_z))

	# temporary array_geos
	magma_array_geos = []
	water_array_geos = []

	x, z = 15, 0
	max_count = max(len(fresh_block.water), len(fresh_block.magma))
	for i in range(max_count):
		magma = fresh_block.magma[i] if i < len(fresh_block.magma) else 0
		water = fresh_block.water[i] if i < len(fresh_block.water) else 0

		if magma > 0 or water > 0:
			if magma > 0:
				tile_pos = gs.Vector3(world_block_pos.x + x, world_block_pos.y - (1.0 - magma / 7)*0.5, world_block_pos.z + z)
				tile_scale = gs.Vector3(1, magma/7., 1)
				iso_array[x, z] = magma/7.
				current_array_geos = magma_array_geos
			elif water > 0:
				tile_pos = gs.Vector3(world_block_pos.x + x, world_block_pos.y - (1.0 - water / 7)*0.5, world_block_pos.z + z)
				tile_scale = gs.Vector3(1, water/7., 1)
				iso_array[x, z] = water/7.
				current_array_geos = water_array_geos

			iso_array_mat[x, z] = 4

			id_tile = hash_from_pos(tile_pos.x, tile_pos.y, tile_pos.z)

			# block["blocks"][id_tile] = {"m": gs.Matrix4.TranslationMatrix(tile_pos), "mat": block_mat} # perfect grid
			n1 = noise.snoise3(tile_pos.x, tile_pos.y, tile_pos.z)
			n2 = noise.snoise3(tile_pos.x+0.5, tile_pos.y, tile_pos.z)
			n3 = noise.snoise3(tile_pos.x, tile_pos.y+0.5, tile_pos.z)
			m = gs.Matrix4.TransformationMatrix(tile_pos, (n1 * 0.1, n2 * 0.1, n3 * 0.1), tile_scale)
			tiles[id_tile] = {"m": m, "mat": 4} # with rumble

			current_array_geos.append(m)

		x -= 1
		if x < 0:
			x = 15
			z += 1

	# reset water and magma
	if len(magma_array_geos) > 0:
		array_geos_worlds[tile_geos[tile_type.MAGMA]["id_geo"]] = magma_array_geos

	if len(water_array_geos) > 0:
		array_geos_worlds[tile_geos[tile_type.WATER]["id_geo"]] = water_array_geos

	iso_array[:, -1] = iso_array[:, -2]
	iso_array[-1, :] = iso_array[-2, :]

	iso_array_mat[:, -1] = iso_array_mat[:, -2]
	iso_array_mat[-1, :] = iso_array_mat[-2, :]

	return array_geos_worlds, tiles, iso_array, iso_array_mat


def make_ramps(world_block_pos, ramp_to_evaluate, iso_array, array_geos_worlds):
	for ramp in ramp_to_evaluate:
		if 0 < ramp[0] < 16 and 0 < ramp[1] < 16:
			cube_val = np.zeros((3, 3, 2))
			cube_val[:, :, 0] = 1
			cube_val[0, 0, 1:] = 1 if iso_array[ramp[0] - 1, ramp[1]] or iso_array[ramp[0], ramp[1] - 1] or iso_array[ramp[0] - 1, ramp[1] - 1] else 0
			cube_val[-1, 0, 1:] = 1 if iso_array[ramp[0] + 1, ramp[1]] or iso_array[ramp[0], ramp[1] - 1] or iso_array[ramp[0] + 1, ramp[1] - 1] else 0
			cube_val[-1, -1, 1:] = 1 if iso_array[ramp[0] + 1, ramp[1]] or iso_array[ramp[0], ramp[1] + 1] or iso_array[ramp[0] + 1, ramp[1] + 1] else 0
			cube_val[0, -1, 1:] = 1 if iso_array[ramp[0] - 1, ramp[1]] or iso_array[ramp[0], ramp[1] + 1] or iso_array[ramp[0] - 1, ramp[1] + 1] else 0

			if iso_array[ramp[0] - 1, ramp[1]]:
				cube_val[0, :, :] = 1
			if iso_array[ramp[0] + 1, ramp[1]]:
				cube_val[-1, :, :] = 1
			if iso_array[ramp[0], ramp[1] + 1]:
				cube_val[:, -1, :] = 1
			if iso_array[ramp[0], ramp[1] - 1]:
				cube_val[:, 0, :] = 1

			id_ramp = hash(str(cube_val))
			if id_ramp not in ramp_geos:
				w, h, d = cube_val.shape[0], cube_val.shape[1], cube_val.shape[2]
				big_array = np.zeros((w+4, h+4, d+6))
				big_array[2:-2, 2:-2, 3:-3] = cube_val

				field = gs.BinaryBlob()
				field.Grow((w+4)*(d+5)*(h+4))
				field.WriteFloats(big_array.flatten('F').tolist())

				iso = gs.IsoSurface()
				gs.PolygoniseIsoSurface(w+2, h+2, d+3, field, 1.0, iso, (1/2, 1, 1/2))

				core_geo = gs.CoreGeometry()
				gs.IsoSurfaceToCoreGeometry(iso, core_geo)
				core_geo.SetMaterial(0, "assets/floor.mat")

				core_geo.ComputeVertexNormal(math.radians(0.0), True)
				core_geo.ComputeVertexTangent()

				ramp_geo = plus.CreateGeometry(core_geo, False)

				render_geos.append({"g": ramp_geo, "o": gs.Matrix4.Identity})
				ramp_geos[id_ramp] = {"id_geo": len(render_geos) - 1}

			id_geo = ramp_geos[id_ramp]["id_geo"]
			tile_pos = gs.Vector3(world_block_pos.x + ramp[0] - 1.5, world_block_pos.y-3.4, world_block_pos.z + ramp[1] - 1.5)
			n1 = noise.snoise3(tile_pos.x, tile_pos.y, tile_pos.z)
			n2 = noise.snoise3(tile_pos.x + 0.5, tile_pos.y, tile_pos.z)
			n3 = noise.snoise3(tile_pos.x, tile_pos.y + 0.5, tile_pos.z)

			m = gs.Matrix4.TransformationMatrix(tile_pos, (n1 * 0.01, n2 * 0.01, n3 * 0.01))

			if id_geo not in array_geos_worlds:
				array_geos_worlds[id_geo] = []
			array_geos_worlds[id_geo].append(m)


def parse_block(fresh_block, array_geos_worlds):
	# clear type tile in array_geos_worlds
	# clean all except water and magma
	for id_geo, array_geo in array_geos_worlds.items():
		if id_geo != tile_geos[tile_type.MAGMA]["id_geo"] and id_geo != tile_geos[tile_type.WATER]["id_geo"]:
			array_geos_worlds[id_geo] = []

	tiles = {}
	ramp_to_evaluate = []
	world_block_pos = from_dfworld_to_world(gs.Vector3(map_info.block_size_x*16-16 - fresh_block.map_x, fresh_block.map_y, fresh_block.map_z))

	iso_array = np.zeros((17, 17))
	iso_array_mat = np.zeros((17, 17))
	x, z = 15, 0
	for tile, material in zip(fresh_block.tiles, fresh_block.materials):
		tile_pos = gs.Vector3(world_block_pos.x + x, world_block_pos.y, world_block_pos.z + z)
		tile_scale = gs.Vector3(1, 1, 1)
		if tile != 0:
			type = df_tile_type_list.tiletype_list[tile]

			if type.shape == remote_fortress.RAMP:
				ramp_to_evaluate.append((x, z))
			# elif type.shape == remote_fortress.RAMP_TOP:
			# 	block_mat = 7

			# choose a material
			block_mat = 0
			color = None
			tile_shape = None
			if type.shape == remote_fortress.FLOOR:
				tile_shape = type.shape
				block_mat = 1
				color = material_list_color[material.mat_type][material.mat_index]

				# for mat in material_list.material_list:
				# 	if mat.mat_pair.mat_type == material.mat_type and mat.mat_pair.mat_index == material.mat_index:
				# 		break
			elif type.shape == remote_fortress.BOULDER:
				tile_shape = type.shape
				block_mat = 3
			elif type.shape == remote_fortress.PEBBLES:
				tile_shape = type.shape
				block_mat = 3
			elif type.shape == remote_fortress.WALL or type.shape == remote_fortress.FORTIFICATION:
				tile_shape = type.shape
				block_mat = 3
				iso_array[x, z] = 1
				color = material_list_color[material.mat_type][material.mat_index]
			# if type.material == remote_fortress.PLANT:
			# 	block_mat = 2
			elif type.shape == remote_fortress.SHRUB or type.shape == remote_fortress.SAPLING:
				tile_shape = type.shape
				block_mat = 1

			if type.shape != remote_fortress.RAMP and (type.material == remote_fortress.TREE_MATERIAL or type.shape == remote_fortress.TRUNK_BRANCH or type.shape == remote_fortress.TWIG):
				tile_shape = type.shape
				block_mat = 5
				iso_array[x, z] = 1

			iso_array_mat[x, z] = block_mat

			# if it's not air, add it to draw it
			id_tile = hash_from_pos(tile_pos.x, tile_pos.y, tile_pos.z)
			if block_mat != 0:
				# block["blocks"][id_tile] = {"m": gs.Matrix4.TranslationMatrix(tile_pos), "mat": block_mat} # perfect grid
				n1 = noise.snoise3(tile_pos.x, tile_pos.y, tile_pos.z)
				n2 = noise.snoise3(tile_pos.x+0.5, tile_pos.y, tile_pos.z)
				n3 = noise.snoise3(tile_pos.x, tile_pos.y+0.5, tile_pos.z)
				m = gs.Matrix4.TransformationMatrix(tile_pos, (n1 * 0.1, n2 * 0.1, n3 * 0.1), tile_scale)
				tiles[id_tile] = {"m": m, "geo": tile_shape} # with rumble

				if tile_shape is not None and "id_geo" in tile_geos[tile_shape]:
					id_geo = tile_geos[tile_shape]["id_geo"]

					# check if there is geo with a color
					if color is not None:
						hash_color = hash(color)
						if hash_color not in tile_geos[tile_shape]["geos_color"]:
							# create the color geo
							new_render_geo = plus.CreateGeometry(tile_geos[tile_shape]["core_g"], False)
							while not new_render_geo.IsReady(): # don't know why it's not immediate ...
								pass
							new_mat = new_render_geo.GetMaterial(0).Clone()
							new_mat.SetFloat4("diffuse_color", color[0], color[1], color[2], 1.0)
							new_render_geo.SetMaterial(0, new_mat)

							render_geos.append({"g": new_render_geo, "o": tile_geos[tile_shape]["o"]})
							tile_geos[tile_shape]["geos_color"][hash_color] = len(render_geos)-1

						id_geo = tile_geos[tile_shape]["geos_color"][hash_color]

					if id_geo not in array_geos_worlds:
						array_geos_worlds[id_geo] = []
					array_geos_worlds[id_geo].append(m * render_geos[id_geo]["o"])

		x -= 1
		if x < 0:
			x = 15
			z += 1

	iso_array[:, -1] = iso_array[:, -2]
	iso_array[-1, :] = iso_array[-2, :]

	iso_array_mat[:, -1] = iso_array_mat[:, -2]
	iso_array_mat[-1, :] = iso_array_mat[-2, :]

	# check the ramps
	make_ramps(world_block_pos, ramp_to_evaluate, iso_array, array_geos_worlds)

	# parse the water, magma
	array_geos_worlds, tiles, iso_array, iso_array_mat = parse_block_only_water_magma(fresh_block, array_geos_worlds, tiles, iso_array, iso_array_mat)

	# parse buildings
	parse_block_building(fresh_block, array_geos_worlds, tiles)

	return array_geos_worlds, tiles, iso_array, iso_array_mat


def parse_big_block(fresh_blocks):
	id_big_block_to_merge = {}

	for id, fresh_block in enumerate(fresh_blocks.map_blocks):
		world_block_pos = from_dfworld_to_world(gs.Vector3(map_info.block_size_x*16 - size_big_block.x - fresh_block.map_x, fresh_block.map_y, fresh_block.map_z))
		world_big_block_pos = world_block_pos / size_big_block
		world_big_block_pos.x = int(world_big_block_pos.x)
		world_big_block_pos.y = int(world_big_block_pos.y)
		world_big_block_pos.z = int(world_big_block_pos.z)

		id_block = (world_block_pos / size_big_block) - world_big_block_pos
		id_block *= size_big_block

		id_block = hash_from_pos_v(id_block)
		id_big_block = hash_from_pos_v(world_big_block_pos)

		if id_big_block not in array_world_big_block:
			with mutex_array_world_big_block:
				array_world_big_block[id_big_block] = {"min_pos": world_big_block_pos * size_big_block, "blocks": {}, "status": status_ready, "time": 1000, "iso_mesh": None, "new_iso_mesh": None, "mutex": threading.Lock()}

		big_block = array_world_big_block[id_big_block]

		# create or initialize the block, if the block actually contains something
		if len(fresh_block.tiles) > 0 or id_block not in big_block["blocks"]:
			id_big_block_to_merge[id_big_block] = True
			array_geos_worlds = {}
			if id_block in big_block["blocks"]:
				array_geos_worlds = big_block["blocks"][id_block]["array_geos_worlds"]

			array_geos_worlds, tiles, iso_array, iso_array_mat = parse_block(fresh_block, array_geos_worlds)
			if id_block not in big_block["blocks"] or len(tiles) > 0:
				with big_block["mutex"]:
					big_block["blocks"][id_block] = {"array_geos_worlds": array_geos_worlds, "tiles": tiles, "iso_array": iso_array, "iso_array_mat": iso_array_mat}

		elif len(fresh_block.water) > 0:
			id_big_block_to_merge[id_big_block] = True
			with big_block["mutex"]:
				array_geos_worlds, tiles, iso_array, iso_array_mat = parse_block_only_water_magma(fresh_block, big_block["blocks"][id_block]["array_geos_worlds"], big_block["blocks"][id_block]["tiles"], big_block["blocks"][id_block]["iso_array"], big_block["blocks"][id_block]["iso_array_mat"])
				big_block["blocks"][id_block] = {"array_geos_worlds": array_geos_worlds, "tiles": tiles, "iso_array": iso_array, "iso_array_mat": iso_array_mat}

	# for id_big_block in id_big_block_to_merge.keys():
	# 	make_big_block_iso(array_world_big_block, array_world_big_block[id_big_block])


parse_big_block_thread = None


def load_big_block(min, max):
	global parse_big_block_thread, unit_list

	# inverse on x because dwarf fortress is inverted on this axis
	temp = min.x
	min.x = map_info.block_size_x * 16 - max.x
	max.x = map_info.block_size_x * 16 - temp

	fresh_blocks = get_block_list(from_world_to_dfworld(min), from_world_to_dfworld(max))

	if parse_big_block_thread is not None and parse_big_block_thread.is_alive():
		parse_big_block_thread.join()
	parse_big_block_thread = threading.Thread(target=parse_big_block, args=(fresh_blocks,))
	parse_big_block_thread.start()

	# update dwarf position in this thread, no race with the get blocks
	update_dwarf.update_dwarf_pos()

big_block_thread = None


def get_viewing_min_max(cam):
	vecs = [
		cam.GetTransform().GetPosition() + cam.GetTransform().GetWorld().GetX() * visible_area_length + cam.GetTransform().GetWorld().GetY() * visible_area_length - cam.GetTransform().GetWorld().GetZ() * 1,
		cam.GetTransform().GetPosition() + cam.GetTransform().GetWorld().GetX() * visible_area_length - cam.GetTransform().GetWorld().GetY() * visible_area_length - cam.GetTransform().GetWorld().GetZ() * 1,
		cam.GetTransform().GetPosition() - cam.GetTransform().GetWorld().GetX() * visible_area_length + cam.GetTransform().GetWorld().GetY() * visible_area_length - cam.GetTransform().GetWorld().GetZ() * 1,
		cam.GetTransform().GetPosition() - cam.GetTransform().GetWorld().GetX() * visible_area_length - cam.GetTransform().GetWorld().GetY() * visible_area_length - cam.GetTransform().GetWorld().GetZ() * 1,

		cam.GetTransform().GetPosition() + cam.GetTransform().GetWorld().GetX() * visible_area_length + cam.GetTransform().GetWorld().GetY() * visible_area_length + cam.GetTransform().GetWorld().GetZ() * visible_area_length,
		cam.GetTransform().GetPosition() + cam.GetTransform().GetWorld().GetX() * visible_area_length - cam.GetTransform().GetWorld().GetY() * visible_area_length + cam.GetTransform().GetWorld().GetZ() * visible_area_length,
		cam.GetTransform().GetPosition() - cam.GetTransform().GetWorld().GetX() * visible_area_length + cam.GetTransform().GetWorld().GetY() * visible_area_length + cam.GetTransform().GetWorld().GetZ() * visible_area_length,
		cam.GetTransform().GetPosition() - cam.GetTransform().GetWorld().GetX() * visible_area_length - cam.GetTransform().GetWorld().GetY() * visible_area_length + cam.GetTransform().GetWorld().GetZ() * visible_area_length]

	def get_min_max(a, b):
		if a < b:
			return a, b
		else:
			return b, a

	pos_min = gs.Vector3(vecs[0])
	pos_max = gs.Vector3(vecs[0])
	for vec in vecs:
		pos_min.x, temp = get_min_max(pos_min.x, vec.x)
		temp, pos_max.x = get_min_max(pos_max.x, vec.x)

		pos_min.y, temp = get_min_max(pos_min.y, vec.y)
		temp, pos_max.y = get_min_max(pos_max.y, vec.y)

		pos_min.z, temp = get_min_max(pos_min.z, vec.z)
		temp, pos_max.z = get_min_max(pos_max.z, vec.z)

	return pos_min, pos_max


def update_block(cam):
	global big_block_thread

	if big_block_thread is None or not big_block_thread.is_alive():
		p_min, p_max = get_viewing_min_max(cam)

		p_min.x -= size_big_block.x
		p_min.z -= size_big_block.z

		p_max.x += size_big_block.x
		p_max.z += size_big_block.z

		big_block_thread = threading.Thread(target=load_big_block, args=(p_min, p_max))
		big_block_thread.start()


def draw_block(renderable_system, cam):
	p_min, p_max = get_viewing_min_max(cam)
	count_draw = 0
	# grow the array_big_block
	for x in range(int(p_min.x // size_big_block.x) - 1, int(p_max.x // size_big_block.x) + 1):
		for y in range(int(p_min.y // size_big_block.y) - 1, int(p_max.y // size_big_block.y) + 1):
			for z in range(int(p_min.z // size_big_block.z) - 1, int(p_max.z // size_big_block.z) + 1):
				id = hash_from_pos(x, y, z)
				if id in array_world_big_block:
					big_block = array_world_big_block[id]
					if big_block["status"] == status_ready:
						with big_block["mutex"]:
							for id_block, block in big_block["blocks"].items():
								for geo, ms in block["array_geos_worlds"].items():
									renderable_system.DrawGeometry(render_geos[geo]["g"], ms)
									count_draw += 1

							# for id, tile in block["tiles"].items():
								# 	renderable_system.DrawGeometry(tile_geos[tile["mat"]], tile["m"])
								# 	count_draw += 1

						#
						# if big_block["new_iso_mesh"] is not None and big_block["new_iso_mesh"][0].IsReady():
						# 	big_block["iso_mesh"] = big_block["new_iso_mesh"]
						# 	big_block["new_iso_mesh"] = None
						#
						# if big_block["iso_mesh"] is not None:
						# 	renderable_system.DrawGeometry(big_block["iso_mesh"][0], gs.Matrix4.TranslationMatrix(big_block["min_pos"]))
						# 	count_draw += 1
	return count_draw
