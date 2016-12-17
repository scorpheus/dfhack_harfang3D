__author__ = 'scorpheus'

import socket
import struct

import RemoteFortressReader_pb2 as remote_fortress
import BasicApi_pb2 as BasicApi
import Block_pb2 as Block
import Tile_pb2 as Tile
import CoreProtocol_pb2 as CoreProtocol

# import RemoteFortressReader_proto as remote_fortress
# import BasicApi_proto as BasicApi
# import Block_proto as Block
# import Tile_proto as Tile
# import CoreProtocol_proto as CoreProtocol

HOST, PORT = "localhost", 5000

sock = 0


def connect_socket():
	global sock
	# Create a socket (SOCK_STREAM means a TCP socket)
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	# Connect to server and send data
	return sock.connect((HOST, PORT)) == 0


def close_socket():
	sock.close()


def handshake():
	# handshake
	values = ('DFHack?\n'.encode("ascii"), 1)
	packer = struct.Struct('8s I')
	packed_data = packer.pack(*values)

	sock.sendall(packed_data)

	# Receive data from the server
	unpacker = struct.Struct('8s I')
	received = sock.recv(unpacker.size)
	unpacked_data = unpacker.unpack(received)

	return True


def send_message(id, message):
	#create header with id of the binding function and the length of the message
	values = (id, len(message))
	packer = struct.Struct('hi')
	packed_data = packer.pack(*values)

	sock.sendall(packed_data+message)


def get_answer_header():
	received = sock.recv(8)
	state = struct.unpack('hi', received)
	return state[1] # size of the waiting message


def get_answer():
	size = get_answer_header()
	received = sock.recv(size)

	while len(received) < size:
		received += sock.recv(size - len(received))

	return received


def get_id_bind_function(message_request):
	# protobuf to string
	serialize_block = message_request.SerializeToString()

	# send the query with the header,
	# 0 is the id to call the method bind request
	send_message(0, serialize_block)

	# Receive data from the server
	received = get_answer()

	# receive the answer protobuf containing the id
	out_id = CoreProtocol.CoreBindReply()
	out_id.ParseFromString(received)

	return out_id.assigned_id

cache_id_function = {}


def get_info_from_dfhack(message_request, message_input):

	# id_function = get_id_bind_function(message_request)
	if message_request.method in cache_id_function:
		id_function = cache_id_function[message_request.method]
	else:
		id_function = get_id_bind_function(message_request)
		cache_id_function[message_request.method] = id_function

	# with the id, call the function and get the result
	serialize_block = message_input.SerializeToString()

	send_message(id_function, serialize_block)

	# Receive data from the server
	return get_answer()


def get_df_version():     # example of how it works, just get the df version

	# create function request
	message_request = CoreProtocol.CoreBindRequest()
	message_request.method = "GetDFVersion"
	message_request.input_msg = "dfproto.EmptyMessage"
	message_request.output_msg = "dfproto.StringMessage"

	# the function get_df_version just need an empty protobuf in input message, but need a protobuf
	data_received = get_info_from_dfhack(message_request, CoreProtocol.EmptyMessage())

	out = CoreProtocol.StringMessage()
	out.ParseFromString(data_received)

	return out.value


def get_map_info():

	# create function request
	message_request = CoreProtocol.CoreBindRequest()
	message_request.method = "GetMapInfo"
	message_request.input_msg = "dfproto.EmptyMessage"
	message_request.output_msg = "RemoteFortressReader.MapInfo"
	message_request.plugin = "RemoteFortressReader"

	# the function get_map_info just need an empty protobuf in input message, but need a protobuf
	data_received = get_info_from_dfhack(message_request, CoreProtocol.EmptyMessage())

	out = remote_fortress.MapInfo()
	out.ParseFromString(data_received)

	return out


def reset_map_hashes():

	# create function request
	message_request = CoreProtocol.CoreBindRequest()
	message_request.method = "ResetMapHashes"
	message_request.input_msg = "dfproto.EmptyMessage"
	message_request.output_msg = "dfproto.EmptyMessage"
	message_request.plugin = "RemoteFortressReader"

	# the function get_df_version just need an empty protobuf in input message, but need a protobuf
	get_info_from_dfhack(message_request, CoreProtocol.EmptyMessage())


def get_all_unit_list():

	# create function request
	message_request = CoreProtocol.CoreBindRequest()
	message_request.method = "GetUnitList"
	message_request.input_msg = "dfproto.EmptyMessage"
	message_request.output_msg = "RemoteFortressReader.UnitList"
	message_request.plugin = "RemoteFortressReader"

	# the function get_map_info just need an empty protobuf in input message, but need a protobuf
	data_received = get_info_from_dfhack(message_request, CoreProtocol.EmptyMessage())

	out = remote_fortress.UnitList()
	out.ParseFromString(data_received)

	return out


def get_list_units():

	# create function request
	message_request = CoreProtocol.CoreBindRequest()
	message_request.method = "ListUnits"
	message_request.input_msg = "dfproto.ListUnitsIn"
	message_request.output_msg = "dfproto.ListUnitsOut"

	# input message: which part of datablock we want
	list_unit_in_message = BasicApi.ListUnitsIn()
	list_unit_in_message.scan_all = True
	list_unit_in_message.alive = True
	list_unit_in_message.race = 465
	# list_unit_in_message.mask.labors = True
	# list_unit_in_message.mask.skills = True
	# list_unit_in_message.mask.profession = True
	# list_unit_in_message.mask.misc_traits = True

	received = get_info_from_dfhack(message_request, list_unit_in_message)

	out = BasicApi.ListUnitsOut()
	out.ParseFromString(received)

	return out


def get_block(pos):

	# create function request
	message_request = CoreProtocol.CoreBindRequest()
	message_request.method = "GetBlock"
	message_request.input_msg = "RemoteFortressReader.BlockRequest"
	message_request.output_msg = "dfproto.MiniBlock"
	message_request.plugin = "RemoteFortressReader"

	# input message: which part of datablock we want
	input_block_message = remote_fortress.BlockRequest()
	input_block_message.min_x = int(pos.x / 16)
	input_block_message.min_y = int(pos.y / 16)
	input_block_message.min_z = int(pos.z)

	received = get_info_from_dfhack(message_request, input_block_message)

	out = Block.MiniBlock()
	out.ParseFromString(received)

	return out


def get_block_complex(pos):
	dfblock = get_block_list(pos, pos+1)
	return None if len(dfblock.map_blocks) <= 0 else dfblock.map_blocks[0]


def get_block_list(p_min, p_max):

	# create function request
	message_request = CoreProtocol.CoreBindRequest()
	message_request.method = "GetBlockList"
	message_request.input_msg = "RemoteFortressReader.BlockRequest"
	message_request.output_msg = "RemoteFortressReader.BlockList"
	message_request.plugin = "RemoteFortressReader"

	# input message: which part of datablock we want
	input_block_message = remote_fortress.BlockRequest()
	input_block_message.min_x = max(0, int(p_min.x / 16))
	input_block_message.max_x = max(0, int(p_max.x / 16))
	input_block_message.min_y = max(0, int(p_min.y / 16))
	input_block_message.max_y = max(0, int(p_max.y / 16))
	input_block_message.min_z = max(0, int(p_min.z))
	input_block_message.max_z = max(0, int(p_max.z))
	input_block_message.blocks_needed = (input_block_message.max_x - input_block_message.min_x) * (input_block_message.max_y - input_block_message.min_y) * (input_block_message.max_z - input_block_message.min_z)

	# for one block in p_min
	# input_block_message.blocks_needed = 1
	# input_block_message.min_x = int(p_min.x / 16)
	# input_block_message.max_x = input_block_message.min_x + 1
	# input_block_message.min_y = int(p_min.y / 16)
	# input_block_message.max_y = input_block_message.min_y + 1
	# input_block_message.min_z = int(p_min.z)
	# input_block_message.max_z = input_block_message.min_z + 1

	# print("x %d, %d"%(input_block_message.min_x, p_min.x))
	# print("y %d, %d"%(input_block_message.min_y, p_min.y))
	# print("z %d, %d"%(input_block_message.min_z, p_min.z))

	received = get_info_from_dfhack(message_request, input_block_message)

	out = remote_fortress.BlockList()
	out.ParseFromString(received)
	return out


def get_tiletype_list():

	# create function request
	message_request = CoreProtocol.CoreBindRequest()
	message_request.method = "GetTiletypeList"
	message_request.input_msg = "dfproto.EmptyMessage"
	message_request.output_msg = "RemoteFortressReader.TiletypeList"
	message_request.plugin = "RemoteFortressReader"

	received = get_info_from_dfhack(message_request, CoreProtocol.EmptyMessage())

	out = remote_fortress.TiletypeList()
	out.ParseFromString(received)

	return out


def get_material_list():

	# create function request
	message_request = CoreProtocol.CoreBindRequest()
	message_request.method = "GetMaterialList"
	message_request.input_msg = "dfproto.EmptyMessage"
	message_request.output_msg = "RemoteFortressReader.MaterialList"
	message_request.plugin = "RemoteFortressReader"

	received = get_info_from_dfhack(message_request, CoreProtocol.EmptyMessage())

	out = remote_fortress.MaterialList()
	out.ParseFromString(received)

	return out


def get_building_def_list():

	# create function request
	message_request = CoreProtocol.CoreBindRequest()
	message_request.method = "GetBuildingDefList"
	message_request.input_msg = "dfproto.EmptyMessage"
	message_request.output_msg = "RemoteFortressReader.BuildingList"
	message_request.plugin = "RemoteFortressReader"

	received = get_info_from_dfhack(message_request, CoreProtocol.EmptyMessage())

	out = remote_fortress.BuildingList()
	out.ParseFromString(received)

	return out
