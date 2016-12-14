__author__ = 'scorpheus'

from dfhack_connect import *
import gs
from math import *
import uuid
import threading
from collections import OrderedDict
import random
import numpy as np
from helpers import *
from iso_mesh_from_big_block import make_big_block_iso


plus = gs.GetPlus()
geos = None


map_info = None
tile_type_list = None
material_list = None
building_geos = None
tile_core_geos = None
tile_geos = None
dwarf_geo = None
cube_geo_big_block = None

scale_unit_y = 1.0
visible_area_length = 15

mutex_big_block = threading.Lock()
array_world_big_block = {}


class building_type():
	NONE = -1
	Chair, Bed, Table, Coffin, FarmPlot, Furnace, TradeDepot, Shop, Door, Floodgate, Box, Weaponrack, \
	Armorstand, Workshop, Cabinet, Statue, WindowGlass, WindowGem, Well, Bridge, RoadDirt, RoadPaved, SiegeEngine, \
	Trap, AnimalTrap, Support, ArcheryTarget, Chain, Cage, Stockpile, Civzone, Weapon, Wagon, ScrewPump, \
	Construction, Hatch, GrateWall, GrateFloor, BarsVertical, BarsFloor, GearAssembly, AxleHorizontal, AxleVertical, \
	WaterWheel, Windmill, TractionBench, Slab, Nest, NestBox, Hive, Rollers = range(51)


def setup():
	global map_info, tile_type_list, material_list, tile_core_geos, tile_geos, geos, building_geos, dwarf_geo, cube_geo_big_block

	connect_socket()
	handshake()
	# dfversion = get_df_version()
	map_info = get_map_info()
	reset_map_hashes()

	# get once to use after (material list is huge)
	tile_type_list = get_tiletype_list()
	# material_list = get_material_list()

	# dwarf_geo = plus.CreateGeometry(plus.CreateCube(0.1, 0.6, 0.1, "iso.mat"))
	dwarf_geo = plus.LoadGeometry("minecraft_assets/default_dwarf/default_dwarf.geo")
	cube_geo_big_block = plus.CreateGeometry(plus.CreateCube(size_big_block.x, size_big_block.y*0.5*scale_unit_y, size_big_block.z, "iso.mat"))

	geos = [plus.LoadGeometry("environment_kit_inca/stone_high_03.geo"), plus.LoadGeometry("environment_kit_inca/stone_high_01.geo")]
	building_geos = {building_type.Chair: None, building_type.Bed: None,
					 building_type.Table: {'g': plus.LoadGeometry("environment_kit/geo-table.geo"), 'o': gs.Matrix4.Identity},
					 building_type.Coffin: None, building_type.FarmPlot: None, building_type.Furnace: None,
					 building_type.TradeDepot: None, building_type.Shop: None,
					 building_type.Door: {'g': plus.LoadGeometry("environment_kit/geo-door.geo"), 'o': gs.Matrix4.Identity},
					 building_type.Floodgate: None,
					 building_type.Box: {'g': plus.LoadGeometry("environment_kit_inca/chest_top.geo"), 'o': gs.Matrix4.Identity},
					 building_type.Weaponrack: None,
					 building_type.Armorstand: None, building_type.Workshop: None,
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
	tile_core_geos = []
	tile_geos = []
	for mat in mats_path:
		core_geo = plus.CreateCube(1.0, 1.0 * scale_unit_y, 1.0, mat)
		tile_core_geos.append(core_geo)
		tile_geos.append(plus.CreateGeometry(core_geo))


def parse_block(fresh_block, block):
	world_block_pos = from_dfworld_to_world(gs.Vector3(fresh_block.map_x, fresh_block.map_y, fresh_block.map_z))

	iso_array = np.zeros((17, 17), np.int8)
	iso_array_mat = np.zeros((17, 17), np.int8)
	x, z = 0, 0
	for tile, magma, water, material in zip(fresh_block.tiles, fresh_block.magma, fresh_block.water, fresh_block.materials):
		if tile != 0:
			type = tile_type_list.tiletype_list[tile]

			# choose a material
			block_mat = 0
			if magma > 0:
				block_mat = 2
				iso_array[x, z] = 1
			elif water > 0:
				block_mat = 4
				iso_array[x, z] = 1
			elif type.shape == remote_fortress.FLOOR:
				block_mat = 1
			elif type.shape == remote_fortress.RAMP:
				block_mat = 6
			elif type.shape == remote_fortress.RAMP_TOP:
				block_mat = 7
			elif type.shape == remote_fortress.BOULDER:
				block_mat = 3
				# array_props.append((gs.Vector3(block_pos.x*16 + x, block_pos.y, block_pos.z*16 + z), 0))
			elif type.shape == remote_fortress.PEBBLES:
				block_mat = 3
				# array_props.append((gs.Vector3(block_pos.x*16 + x, block_pos.y, block_pos.z*16 + z), 1))
			elif type.shape == remote_fortress.WALL or type.shape == remote_fortress.FORTIFICATION:
				block_mat = 3
				iso_array[x, z] = 1
			# if type.material == remote_fortress.PLANT:
			# 	block_mat = 2
			elif type.shape == remote_fortress.SHRUB or type.shape == remote_fortress.SAPLING:
				block_mat = 1

			if type.material == remote_fortress.TREE_MATERIAL or type.shape == remote_fortress.TRUNK_BRANCH or\
				type.shape == remote_fortress.TWIG:
				block_mat = 5
				iso_array[x, z] = 1

			iso_array_mat[x, z] = block_mat

			# if it's not air, add it to draw it
			tile_pos = gs.Vector3(world_block_pos.x + x, world_block_pos.y, world_block_pos.z + z)
			id_tile = hash_from_pos(tile_pos.x, tile_pos.y, tile_pos.z)
			if block_mat != 0:
				# block["blocks"][id_tile] = {"m": gs.Matrix4.TranslationMatrix(tile_pos), "mat": block_mat} # perfect grid
				block["tiles"][id_tile] = {"m": gs.Matrix4.TransformationMatrix(tile_pos, gs.Vector3(random.random() * 0.2 - 0.1, random.random() * 0.2 - 0.1, random.random() * 0.2 - 0.1)), "mat": block_mat} # with rumble
			else:
				if id_tile in block["tiles"]:
					del block["tiles"][id_tile]

			# add props
			# if building != -1:
			# 	array_building.append((gs.Vector3(block_pos.x*16 + x, block_pos.y, block_pos.z*16 + z), building))

		x += 1
		if x > 15:
			x = 0
			z += 1

	iso_array[:, -1] = iso_array[:, -2]
	iso_array[-1, :] = iso_array[-2, :]
	block["iso_array"] = iso_array

	iso_array_mat[:, -1] = iso_array_mat[:, -2]
	iso_array_mat[-1, :] = iso_array_mat[-2, :]
	block["iso_array_mat"] = iso_array_mat


def get_viewing_min_max(cam):
	vecs = [cam.GetTransform().GetPosition() + cam.GetTransform().GetWorld().GetX() * visible_area_length + cam.GetTransform().GetWorld().GetY() * visible_area_length - cam.GetTransform().GetWorld().GetZ() * 1,
	        cam.GetTransform().GetPosition() + cam.GetTransform().GetWorld().GetX() * visible_area_length - cam.GetTransform().GetWorld().GetY() * visible_area_length - cam.GetTransform().GetWorld().GetZ() * 1,
	        cam.GetTransform().GetPosition() - cam.GetTransform().GetWorld().GetX() * visible_area_length + cam.GetTransform().GetWorld().GetY() * visible_area_length - cam.GetTransform().GetWorld().GetZ() * 1,
	        cam.GetTransform().GetPosition() - cam.GetTransform().GetWorld().GetX() * visible_area_length - cam.GetTransform().GetWorld().GetY() * visible_area_length - cam.GetTransform().GetWorld().GetZ() * 1,

	        cam.GetTransform().GetPosition() + cam.GetTransform().GetWorld().GetX() * visible_area_length + cam.GetTransform().GetWorld().GetY() * visible_area_length + cam.GetTransform().GetWorld().GetZ() * visible_area_length,
	        cam.GetTransform().GetPosition() + cam.GetTransform().GetWorld().GetX() * visible_area_length - cam.GetTransform().GetWorld().GetY() * visible_area_length + cam.GetTransform().GetWorld().GetZ() * visible_area_length,
	        cam.GetTransform().GetPosition() - cam.GetTransform().GetWorld().GetX() * visible_area_length + cam.GetTransform().GetWorld().GetY() * visible_area_length + cam.GetTransform().GetWorld().GetZ() * visible_area_length,
	        cam.GetTransform().GetPosition() - cam.GetTransform().GetWorld().GetX() * visible_area_length - cam.GetTransform().GetWorld().GetY() * visible_area_length + cam.GetTransform().GetWorld().GetZ() * visible_area_length
	        ]

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


def make_big_block_merge(big_block):
	geos = []
	ms = []
	for id_block, block in big_block["blocks"].items():
		for id, tile in block["tiles"].items():
			geos.append(tile_core_geos[tile["mat"]])
			ms.append(tile["m"])

	if len(geos) > 0:
		big_block["iso_mesh"] = gs.GeometryMerge(str(uuid.uuid4()), geos, ms)


def parse_big_block(fresh_blocks):
	id_big_block_to_merge = {}

	for id, fresh_block in enumerate(fresh_blocks.map_blocks):
		world_block_pos = from_dfworld_to_world(gs.Vector3(fresh_block.map_x, fresh_block.map_y, fresh_block.map_z))
		world_big_block_pos = world_block_pos / size_big_block
		world_big_block_pos.x = floor(world_big_block_pos.x)
		world_big_block_pos.y = floor(world_big_block_pos.y)
		world_big_block_pos.z = floor(world_big_block_pos.z)

		id_block = (world_block_pos / size_big_block) - world_big_block_pos
		id_block *= size_big_block

		id_block = hash_from_pos_v(id_block)
		id_world = hash_from_pos_v(world_big_block_pos)

		if id_world not in array_world_big_block:
			array_world_big_block[id_world] = {"min_pos": world_big_block_pos * size_big_block, "blocks": {}, "status": status_ready, "time": 1000, "iso_mesh": None}

		big_block = array_world_big_block[id_world]
		id_big_block_to_merge[id_world] = True

		if id_block not in big_block["blocks"]:
			with mutex_big_block:
				big_block["blocks"][id_block] = {"tiles": {}, "iso_array": np.zeros((17, 17), np.int8), "iso_array_mat": np.zeros((17, 17), np.int8)}
		parse_block(fresh_block, big_block["blocks"][id_block])
	#
	# big_block["status"] = status_ready
	# for id_big_block in id_big_block_to_merge.keys():
		# make_big_block_iso(array_world_big_block, big_block)
		# make_big_block_merge(array_world_big_block[id_big_block])

parse_big_block_thread = None


def load_big_block(min, max):
	global parse_big_block_thread

	fresh_blocks = get_block_list(from_world_to_dfworld(min), from_world_to_dfworld(max))

	if parse_big_block_thread is not None and parse_big_block_thread.is_alive():
		parse_big_block_thread.join()
	parse_big_block_thread = threading.Thread(target=parse_big_block, args=(fresh_blocks,))
	parse_big_block_thread.start()

big_block_thread = None


def update_block(cam):
	global big_block_thread

	if big_block_thread is None or not big_block_thread.is_alive():
		p_min, p_max = get_viewing_min_max(cam)

		# grow the array_big_block
		# for x in range(int(p_min.x // size_big_block.x) - 1, int(p_max.x // size_big_block.x) + 1):
		# 	for y in range(int(p_min.y // size_big_block.y) - 1, int(p_max.y // size_big_block.y) + 1):
		# 		for z in range(int(p_min.z // size_big_block.z) - 1, int(p_max.z // size_big_block.z) + 1):
		# 			id = hash_from_pos(x, y, z)
		# 			if id not in array_world_big_block:
		# 				array_world_big_block[id] = {"min_pos": gs.Vector3(x, y, z) * size_big_block, "blocks": {}, "status": status_to_parse, "time": 1000, "iso_mesh": None}

		# p_min.x -= size_big_block.x
		# p_min.z -= size_big_block.z
		#
		# p_max.x += size_big_block.x
		# p_max.z += size_big_block.z

		big_block_thread = threading.Thread(target=load_big_block, args=(p_min, p_max))
		big_block_thread.start()

		# dir = cam.GetTransform().GetWorld().GetZ()
		# # dir.y = 0
		# pos_in_front = cam.GetTransform().GetPosition() + dir.Normalized() * 2
		# ordered_array_world_big_block = OrderedDict(sorted(array_world_big_block.items(), key=lambda t: ((t[1]["min_pos"].x + size_big_block.x/2 - pos_in_front.x) // size_big_block.x) ** 2 +
		#                                                                                                 ((((t[1]["min_pos"].y + size_big_block.y/2 - pos_in_front.y) // size_big_block.y)) / scale_unit_y) ** 2 +
		#                                                                                                 ((t[1]["min_pos"].z + size_big_block.z/2 - pos_in_front.z) // size_big_block.x) ** 2))
		#
		# # find a block to update
		# for id, big_block in ordered_array_world_big_block.items():
		# 	if big_block["status"] == status_to_parse:
		# 		big_block["status"] = status_parsing
		#
		# 		big_block_thread = threading.Thread(target=load_big_block, args=(big_block,))
		# 		big_block_thread.start()
		# 		break


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
						with mutex_big_block:
							for id_block, block in big_block["blocks"].items():
								for id, tile in block["tiles"].items():
									renderable_system.DrawGeometry(tile_geos[tile["mat"]], tile["m"])
									count_draw += 1
						#
						# if big_block["iso_mesh"] is not None and big_block["iso_mesh"][0].IsReady():
						# 	renderable_system.DrawGeometry(big_block["iso_mesh"][0], gs.Matrix4.TranslationMatrix(big_block["min_pos"]))
						# 	count_draw += 1
	return count_draw
