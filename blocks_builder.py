__author__ = 'scorpheus'

from dfhack_connect import *
import gs
import numpy as np


plus = gs.GetPlus()
geos = None

map_info = None
tile_type_list = None
material_list = None
building_geos = None
dwarf_geo = None
cube_geo = None
mats_path = ["empty.mat", "floor.mat", "magma.mat", "rock.mat", "water.mat", "tree.mat", "floor.mat", "floor.mat"]

scale_unit_y = 1.0


def from_world_to_dfworld(new_pos):
	return gs.Vector3(new_pos.x, new_pos.z, new_pos.y)


def from_dfworld_to_world(new_pos):
	return gs.Vector3(new_pos.x, new_pos.z, new_pos.y)


size_big_block = gs.Vector3(16 * 3, 3, 16 * 3)
array_world_big_block = {}


cache_block = {}

# cache_block_props = {}
# cache_block_building = {}
# cache_block_mat = {}
# cache_geo_block = {}
# update_cache_block = {}
# update_cache_geo_block = {}
# counter_block_to_remove = {}


class building_type():
	NONE = -1
	Chair, Bed, Table, Coffin, FarmPlot, Furnace, TradeDepot, Shop, Door, Floodgate, Box, Weaponrack, \
	Armorstand, Workshop, Cabinet, Statue, WindowGlass, WindowGem, Well, Bridge, RoadDirt, RoadPaved, SiegeEngine, \
	Trap, AnimalTrap, Support, ArcheryTarget, Chain, Cage, Stockpile, Civzone, Weapon, Wagon, ScrewPump, \
	Construction, Hatch, GrateWall, GrateFloor, BarsVertical, BarsFloor, GearAssembly, AxleHorizontal, AxleVertical, \
	WaterWheel, Windmill, TractionBench, Slab, Nest, NestBox, Hive, Rollers = range(51)


def hash_from_pos(x, y, z):
	return x + y * 2048 + z * 2048 * 2048


def setup():
	global map_info, tile_type_list, material_list, geos, building_geos, dwarf_geo, cube_geo

	connect_socket()
	handshake()
	# dfversion = get_df_version()
	map_info = get_map_info()

	# get once to use after (material list is huge)
	tile_type_list = get_tiletype_list()
	# material_list = get_material_list()

	# dwarf_geo = plus.CreateGeometry(plus.CreateCube(0.1, 0.6, 0.1, "iso.mat"))
	dwarf_geo = plus.LoadGeometry("minecraft_assets/default_dwarf/default_dwarf.geo")
	cube_geo = plus.CreateGeometry(plus.CreateCube(0.5, 0.5*scale_unit_y, 0.5, "iso.mat"))


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



	old_pos = gs.Vector3()

	# precompile material
	# for mat in mats_path:
	# 	plus.CreateGeometry(plus.create_cube(0.1, 0.6, 0.1, mat))


def parse_block(fresh_block, big_block):
	world_block_pos = from_dfworld_to_world(gs.Vector3(fresh_block.map_x, fresh_block.map_y, fresh_block.map_z))
	# world_block_pos.x *= 16
	# world_block_pos.z *= 16

	x, z = 15, 0
	for tile, magma, water, material in zip(fresh_block.tiles, fresh_block.magma, fresh_block.water, fresh_block.materials):
		if tile != 0:
			type = tile_type_list.tiletype_list[tile]

			# choose a material
			block_mat = 0
			if magma > 0:
				block_mat = 2
			elif water > 0:
				block_mat = 4
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
			# if type.material == remote_fortress.PLANT:
			# 	block_mat = 2
			elif type.shape == remote_fortress.SHRUB or type.shape == remote_fortress.SAPLING:
				block_mat = 1

			if type.material == remote_fortress.TREE_MATERIAL or type.shape == remote_fortress.TRUNK_BRANCH or\
				type.shape == remote_fortress.TWIG:
				block_mat = 5

			# if it's not air, add it to draw it
			tile_pos = gs.Vector3(world_block_pos.x + x, world_block_pos.y, world_block_pos.z + z)
			id_tile = hash_from_pos(tile_pos.x, tile_pos.y, tile_pos.z)
			if block_mat != 0:
				big_block["blocks"][id_tile] = {"m": gs.Matrix4.TranslationMatrix(tile_pos), "mat": block_mat}
			else:
				if id_tile in big_block["blocks"]:
					del big_block["blocks"][id_tile]

			# add props
			# if building != -1:
			# 	array_building.append((gs.Vector3(block_pos.x*16 + x, block_pos.y, block_pos.z*16 + z), building))

		x -= 1
		if x < 0:
			x = 15
			z += 1

block_drawn = 0
props_drawn = 0


def draw_geo_block(renderable_system, geo_block, x, y, z):
	x *= 16
	z *= 16

	renderable_system.DrawGeometry(geo_block[0], gs.Matrix4.TranslationMatrix(gs.Vector3(x+1, y*scale_unit_y, z)) * gs.Matrix4.ScaleMatrix(gs.Vector3(1, scale_unit_y, 1)))

	global block_drawn
	block_drawn += 1


def draw_cube_block(renderable_system, name_block, pos_block):
	block = cache_block[name_block]
	for x in range(16):
		for z in range(16):
			if block[x, z] == 1:
				renderable_system.DrawGeometry(cube_geo, gs.Matrix4.TransformationMatrix(gs.Vector3(pos_block.x*16+x+1, pos_block.y*scale_unit_y, pos_block.z*16+z), gs.Vector3(0, 0, 0)))


# def draw_props_in_block(renderable_system, name_block):
# 	for prop in cache_block_props[name_block]:
# 		renderable_system.DrawGeometry(geos[prop[1]], gs.Matrix4.TransformationMatrix(gs.Vector3(prop[0].x+1, prop[0].y*scale_unit_y, prop[0].z), gs.Vector3(0, (name_block%628)*0.01, 0), gs.Vector3(0.25, 0.25, 0.25)))
# 		global props_drawn
# 		props_drawn += 1
#
#
# def draw_building_in_block(renderable_system, name_block):
# 	for building in cache_block_building[name_block]:
# 		if building_geos[building[1]] is not None:
# 			renderable_system.DrawGeometry(building_geos[building[1]]["g"], gs.Matrix4.TransformationMatrix(gs.Vector3(building[0].x+1, building[0].y*scale_unit_y, building[0].z), gs.Vector3(0, 0, 0), gs.Vector3(0.25, 0.25, 0.25)) * building_geos[building[1]]["o"])
# 			global props_drawn
# 			props_drawn += 1


def get_viewing_min_max(cam):
	pos_min = gs.Vector3(99999, 99999, 99999)
	pos_max = gs.Vector3(-99999, -99999, -99999)
	cam_pos_up_left = cam.GetTransform().GetPosition() + cam.GetTransform().GetWorld().GetY() * 50 + cam.GetTransform().GetWorld().GetX() * -50
	cam_pos_down_right_max = cam.GetTransform().GetPosition() + cam.GetTransform().GetWorld().GetY() * -50 + cam.GetTransform().GetWorld().GetX() * 50 + cam.GetTransform().GetWorld().GetZ() * 50

	if cam_pos_up_left.x < cam_pos_down_right_max.x:
		pos_min.x = cam_pos_up_left.x
		pos_max.x = cam_pos_down_right_max.x
	else:
		pos_min.x = cam_pos_down_right_max.x
		pos_max.x = cam_pos_up_left.x

	if cam_pos_up_left.y < cam_pos_down_right_max.y:
		pos_min.y = cam_pos_up_left.y
		pos_max.y = cam_pos_down_right_max.y
	else:
		pos_min.y = cam_pos_down_right_max.y
		pos_max.y = cam_pos_up_left.y

	if cam_pos_up_left.z < cam_pos_down_right_max.z:
		pos_min.z = cam_pos_up_left.z
		pos_max.z = cam_pos_down_right_max.z
	else:
		pos_min.z = cam_pos_down_right_max.z
		pos_max.z = cam_pos_up_left.z

	return pos_min, pos_max


def update_block(cam):
	p_min, p_max = get_viewing_min_max(cam)

	# grow the array_big_block
	for x in range(int(p_min.x // size_big_block.x), int(p_max.x // size_big_block.x)):
		for y in range(int(p_min.y // size_big_block.y), int(p_max.y // size_big_block.y)):
			for z in range(int(p_min.z // size_big_block.z), int(p_max.z // size_big_block.z)):
				id = hash_from_pos(x, y, z)
				if id not in array_world_big_block:
					array_world_big_block[id] = {"min": gs.Vector3(x, y, z) * size_big_block, "blocks": {}, "to_update": True, "time": 1000}

	# find a block to update
	for id, big_block in array_world_big_block.items():
		if big_block["to_update"]:
			fresh_blocks = get_block_list(from_world_to_dfworld(big_block["min"]), from_world_to_dfworld(big_block["min"] + size_big_block))
			for fresh_block in fresh_blocks.map_blocks:
				parse_block(fresh_block, big_block)
			big_block["to_update"] = False
			break


def draw_block(renderable_system):
	for id, big_block in array_world_big_block.items():
		if not big_block["to_update"]:
			for id, block in big_block["blocks"].items():
				renderable_system.DrawGeometry(cube_geo, block["m"])

# def update_geo_block():
# 	global update_cache_geo_block
# 	global cache_geo_block
#
# 	if len(update_cache_geo_block) <= 0:
# 		return
#
# 	pos_in_front = fps_pos_in_front_2d(2)
# 	ordered_update_cache_geo = OrderedDict(sorted(update_cache_geo_block.items(), key=lambda t: (t[1].x-pos_in_front.x/16)**2 + ((t[1].y -pos_in_front.y/scale_unit_y)/1.5)**2 + (t[1].z - pos_in_front.z/16)**2))
#
# 	# get a not already updating Node
# 	for name_block, block_pos in iter(ordered_update_cache_geo.items()):
# 		current_layer_block_name = hash_from_pos(block_pos.x, block_pos.y, block_pos.z)
# 		upper_layer_block_name = hash_from_pos(block_pos.x, block_pos.y + 1, block_pos.z)
#
# 		if current_layer_block_name in cache_block and upper_layer_block_name in cache_block:
# 			def check_block_can_generate_geo(x, y, z):
# 				# can update the geo block because it has all the neighbour
# 				return hash_from_pos(x, y, z+1) in cache_block and hash_from_pos(x + 1, y, z) in cache_block
#
# 			if check_block_can_generate_geo(block_pos.x, block_pos.y, block_pos.z) and check_block_can_generate_geo(block_pos.x, block_pos.y + 1, block_pos.z):
# 				cache_geo_block[current_layer_block_name] = create_iso_geo_from_block(current_layer_block_name, upper_layer_block_name, cache_block[current_layer_block_name], cache_block[upper_layer_block_name], block_pos)
# 				update_cache_geo_block.pop(current_layer_block_name)
# 				break
#
