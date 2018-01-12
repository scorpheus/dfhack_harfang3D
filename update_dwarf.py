__author__ = 'scorpheus'

from dfhack_connect import *
import harfang as hg
from harfang_shortcut import *
import threading
import blocks_builder

dwarfs_pos = {}
mutex_dwarfs_pos = threading.Lock()

dwarf_geo = None


def update_dwarf_pos():
	global dwarfs_pos

	with mutex_dwarfs_pos:
		unit_list = get_all_unit_list()
		for unit in unit_list.creature_list:
			if unit.race.mat_type == 572:
				if unit.id in dwarfs_pos:
					dwarfs_pos[unit.id]["new_pos"] = vec3(unit.pos_x, unit.pos_y, unit.pos_z)
				else:
					pos = vec3(unit.pos_x, unit.pos_y, unit.pos_z)
					dwarfs_pos[unit.id] = {"pos": pos, "new_pos": pos, "rot": mat3.Identity}


def draw_dwarf(scn):
	global dwarf_geo
	if dwarf_geo is None:
		plus = hg.GetPlus()
		# dwarf_geo = plus.CreateGeometry(plus.CreateCube(0.1, 0.6, 0.1, "iso.mat"))
		dwarf_geo = plus.LoadGeometry("minecraft_assets/default_dwarf/default_dwarf.geo")

	with mutex_dwarfs_pos:
		dwarf_scale = vec3(0.01, 0.01, 0.01)
		for dwarf in dwarfs_pos.values():

			d = dwarf["new_pos"] - dwarf["pos"]
			if d.Len2() != 0:
				dwarf["rot"] = mat3.LookAt(vec3(-d.x, d.z, d.y).Normalized())
				dwarf["pos"] += d * 0.5

			scn.GetRenderableSystem().DrawGeometry(dwarf_geo, hg.Matrix4.TransformationMatrix(vec3(blocks_builder.map_info.block_size_x * 16 - dwarf["pos"].x, dwarf["pos"].z * blocks_builder.scale_unit_y - 0.5, dwarf["pos"].y), dwarf["rot"], dwarf_scale))
