__author__ = 'scorpheus'

from dfhack_connect import *


try:
	connect_socket()
	Handshake()
	dfversion = GetDFVersion()

	blocklist = GetBlockList()




finally:
	close_socket()

