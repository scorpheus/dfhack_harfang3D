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
					dwarfs_pos[unit.unit_id] += (gs.Vector3(unit.pos_x, unit.pos_y, unit.pos_z) - dwarfs_pos[unit.unit_id])*0.5
				else:
					dwarfs_pos[unit.unit_id] = gs.Vector3(unit.pos_x, unit.pos_y, unit.pos_z)
		unit_list_thread = UpdateUnitListFromDF()
		unit_list_thread.start()

