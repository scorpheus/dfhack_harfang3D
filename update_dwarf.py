__author__ = 'scorpheus'

from dfhack_connect import *
import gs
import geometry_iso

from collections import OrderedDict
import threading
import numpy as np


dwarfs_pos = {}

class UpdateUnitListFromDF(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		self.unit_list = None

	def run(self):
		self.unit_list = GetListUnits()

unit_list_thread = UpdateUnitListFromDF()

def update_dwarf_pos():
	global unit_list_thread, dwarfs_pos

	if not unit_list_thread.is_alive():
		if unit_list_thread.unit_list is not None:
			for unit in unit_list_thread.unit_list.value:
				if unit.unit_id in dwarfs_pos:
					d = gs.Vector3(unit.pos_x, unit.pos_y, unit.pos_z) - dwarfs_pos[unit.unit_id][0]
					if d.Len2() != 0:
						dwarfs_pos[unit.unit_id][1] = gs.Matrix3.LookAt(gs.Vector3(-d.x, d.z, d.y).Normalized())
					dwarfs_pos[unit.unit_id][0] += d*0.5
				else:
					dwarfs_pos[unit.unit_id] = [gs.Vector3(unit.pos_x, unit.pos_y, unit.pos_z), gs.Matrix3.Identity]
		unit_list_thread = UpdateUnitListFromDF()
		unit_list_thread.start()

