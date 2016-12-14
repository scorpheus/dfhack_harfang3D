__author__ = 'scorpheus'

from dfhack_connect import *
import gs
import threading

dwarfs_pos = {}
mutex_dwarfs_pos = threading.Lock()


def update_dwarf_pos():
	global dwarfs_pos

	with mutex_dwarfs_pos:
		unit_list = get_all_unit_list()
		for unit in unit_list.creature_list:
			if unit.race.mat_type == 572:
				if unit.id in dwarfs_pos:
					d = gs.Vector3(unit.pos_x, unit.pos_y, unit.pos_z) - dwarfs_pos[unit.id][0]
					if d.Len2() != 0:
						dwarfs_pos[unit.id][1] = gs.Matrix3.LookAt(gs.Vector3(-d.x, d.z, d.y).Normalized())
					dwarfs_pos[unit.id][0] += d*0.5
				else:
					dwarfs_pos[unit.id] = [gs.Vector3(unit.pos_x, unit.pos_y, unit.pos_z), gs.Matrix3.Identity]

