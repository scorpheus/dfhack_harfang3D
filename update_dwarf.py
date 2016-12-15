__author__ = 'scorpheus'

from dfhack_connect import *
import gs
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
					dwarfs_pos[unit.id]["new_pos"] = gs.Vector3(unit.pos_x, unit.pos_y, unit.pos_z)
				else:
					pos = gs.Vector3(unit.pos_x, unit.pos_y, unit.pos_z)
					dwarfs_pos[unit.id] = {"pos": pos, "new_pos": pos, "rot": gs.Matrix3.Identity}


def draw_dwarf(scn):
	global dwarf_geo
	if dwarf_geo is None:
		plus = gs.GetPlus()
		# dwarf_geo = plus.CreateGeometry(plus.CreateCube(0.1, 0.6, 0.1, "iso.mat"))
		dwarf_geo = plus.LoadGeometry("minecraft_assets/default_dwarf/default_dwarf.geo")

	with mutex_dwarfs_pos:
		dwarf_scale = gs.Vector3(0.01, 0.01, 0.01)
		for dwarf in dwarfs_pos.values():

			d = dwarf["new_pos"] - dwarf["pos"]
			if d.Len2() != 0:
				dwarf["rot"] = gs.Matrix3.LookAt(gs.Vector3(-d.x, d.z, d.y).Normalized())
				dwarf["pos"] += d * 0.5

			scn.GetRenderableSystem().DrawGeometry(dwarf_geo, gs.Matrix4.TransformationMatrix( gs.Vector3(blocks_builder.map_info.block_size_x * 16 - dwarf["pos"].x, dwarf["pos"].z * blocks_builder.scale_unit_y - 0.5, dwarf["pos"].y), dwarf["rot"], dwarf_scale))
