__author__ = 'scorpheus'

import socket
import struct
import proto.build.RemoteFortressReader_pb2 as remote_fortress
import proto.build.BasicApi_pb2 as BasicApi
import proto.build.Block_pb2 as Block
import proto.build.Tile_pb2 as Tile
import proto.build.CoreProtocol_pb2 as CoreProtocol

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


def Handshake():
	# Handshake
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


def GetAnswerHeader():
	received = sock.recv(8)
	state = struct.unpack('hi', received)
	return state[1] # size of the waiting message


def GetAnswer():
	size = GetAnswerHeader()
	received = sock.recv(size)

	while len(received) < size:
		received += sock.recv(size - len(received))

	return received


def GetIDBindFunction(message_request):
	# protobuf to string
	serialize_block = message_request.SerializeToString()

	# send the query with the header,
	# 0 is the id to call the method bind request
	send_message(0, serialize_block)

	# Receive data from the server
	received = GetAnswer()

	# receive the answer protobuf containing the id
	out_id = CoreProtocol.CoreBindReply()
	out_id.ParseFromString(received)

	return out_id.assigned_id

cache_id_function = {}

def GetInfoFromDFHack(message_request, message_input):

	# id_function = GetIDBindFunction(message_request)
	if message_request.method in cache_id_function:
		id_function = cache_id_function[message_request.method]
	else:
		id_function = GetIDBindFunction(message_request)
		cache_id_function[message_request.method] = id_function

	# with the id, call the function and get the result
	serialize_block = message_input.SerializeToString()

	send_message(id_function, serialize_block)

	# Receive data from the server
	return GetAnswer()


def GetDFVersion():     # example of how it works, just get the df version

	# create function request
	message_request = CoreProtocol.CoreBindRequest()
	message_request.method = "GetDFVersion"
	message_request.input_msg = "dfproto.EmptyMessage"
	message_request.output_msg = "dfproto.StringMessage"

	# the function GetDFVersion just need an empty protobuf in input message, but need a protobuf
	data_received = GetInfoFromDFHack(message_request, CoreProtocol.EmptyMessage())

	out = CoreProtocol.StringMessage()
	out.ParseFromString(data_received)

	return out.value

def GetMapInfo():

	# create function request
	message_request = CoreProtocol.CoreBindRequest()
	message_request.method = "GetMapInfo"
	message_request.input_msg = "dfproto.EmptyMessage"
	message_request.output_msg = "RemoteFortressReader.MapInfo"
	message_request.plugin = "RemoteFortressReader"

	# the function GetMapInfo just need an empty protobuf in input message, but need a protobuf
	data_received = GetInfoFromDFHack(message_request, CoreProtocol.EmptyMessage())

	out = remote_fortress.MapInfo()
	out.ParseFromString(data_received)

	return out


def ResetMapHashes():

	# create function request
	message_request = CoreProtocol.CoreBindRequest()
	message_request.method = "ResetMapHashes"
	message_request.input_msg = "dfproto.EmptyMessage"
	message_request.output_msg = "dfproto.EmptyMessage"
	message_request.plugin = "RemoteFortressReader"

	# the function GetDFVersion just need an empty protobuf in input message, but need a protobuf
	GetInfoFromDFHack(message_request, CoreProtocol.EmptyMessage())


def GetAllUnitList():

	# create function request
	message_request = CoreProtocol.CoreBindRequest()
	message_request.method = "GetUnitList"
	message_request.input_msg = "dfproto.EmptyMessage"
	message_request.output_msg = "RemoteFortressReader.UnitList"
	message_request.plugin = "RemoteFortressReader"

	# the function GetMapInfo just need an empty protobuf in input message, but need a protobuf
	data_received = GetInfoFromDFHack(message_request, CoreProtocol.EmptyMessage())

	out = remote_fortress.UnitList()
	out.ParseFromString(data_received)

	return out


def GetListUnits():

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

	received = GetInfoFromDFHack(message_request, list_unit_in_message)

	out = BasicApi.ListUnitsOut()
	out.ParseFromString(received)

	return out

import numpy as np
import mmap
from struct import *

shm_block = mmap.mmap(0, 1+3*4 + 16*16*2 + 16*16 + 16*16 + 16*16, "Local\\df_block") # You should "open" the memory map file instead of attempting to create it..
shm_pos = mmap.mmap(0, 1+3*4, "Local\\df_pos")

# initialize the shared memory
shm_block[0] = 0
shm_pos[0] = 0

def GetBlockMemory():
	get_buffer = shm_block[0] != 0

	block = None
	block_pos = None
	block_flow_size = None
	block_liquid_type = None
	block_building = None
	# if block available
	if get_buffer:
		start_id, end_id = 1+3*4, 1+3*4+16*16*2
		block = np.frombuffer(shm_block[start_id:end_id], dtype=np.uint16)
		start_id = end_id
		end_id += 16*16
		block_flow_size = np.frombuffer(shm_block[start_id:end_id], dtype=np.uint8)
		start_id = end_id
		end_id += 16*16
		block_liquid_type = np.frombuffer(shm_block[start_id:end_id], dtype=np.uint8)
		start_id = end_id
		end_id += 16*16
		block_building = np.frombuffer(shm_block[start_id:end_id], dtype=np.int8)
		block_pos = np.frombuffer(shm_block[1:(1+3*4)], dtype=np.int32)
		shm_block[0] = 0
		shm_block.flush()

	return block_pos, block, block_flow_size, block_liquid_type, block_building

def SendPos(pos):
	send_pos = shm_pos[0] == 0

	# if no pos and no block
	# send another pos
	if pos is not None and send_pos:
		packed_data = pack('=Biii', 3, int(pos.x), int(pos.y), int(pos.z))
		shm_pos.write(packed_data)
		shm_pos.flush()
		shm_pos.seek(0)

def GetBlock(pos):

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

	received = GetInfoFromDFHack(message_request, input_block_message)

	out = Block.MiniBlock()
	out.ParseFromString(received)

	return out


def GetBlockComplex(pos):
	dfblock = GetBlockList(pos, pos+1)
	return None if len(dfblock.map_blocks) <= 0 else dfblock.map_blocks[0]


def GetBlockList(p_min, p_max):

	# create function request
	message_request = CoreProtocol.CoreBindRequest()
	message_request.method = "GetBlockList"
	message_request.input_msg = "RemoteFortressReader.BlockRequest"
	message_request.output_msg = "RemoteFortressReader.BlockList"
	message_request.plugin = "RemoteFortressReader"

	# input message: which part of datablock we want
	input_block_message = remote_fortress.BlockRequest()
	# input_block_message.min_x = int(p_min.x / 16)
	# input_block_message.max_x = int(p_max.x / 16)+1
	# input_block_message.min_y = int(p_min.y / 16)
	# input_block_message.max_y = int(p_max.y / 16)+1
	# input_block_message.min_z = int(p_min.z)
	# input_block_message.max_z = int(p_max.z)
	# input_block_message.blocks_needed = (input_block_message.max_x - input_block_message.min_x) * (input_block_message.max_y - input_block_message.min_y) * (input_block_message.max_z - input_block_message.min_z)

	input_block_message.blocks_needed = 1
	input_block_message.min_x = int(p_min.x / 16)
	input_block_message.max_x = input_block_message.min_x + 1
	input_block_message.min_y = int(p_min.y / 16)
	input_block_message.max_y = input_block_message.min_y + 1
	input_block_message.min_z = int(p_min.z)
	input_block_message.max_z = input_block_message.min_z + 1

	# print("x %d, %d"%(input_block_message.min_x, p_min.x))
	# print("y %d, %d"%(input_block_message.min_y, p_min.y))
	# print("z %d, %d"%(input_block_message.min_z, p_min.z))

	received = GetInfoFromDFHack(message_request, input_block_message)

	out = remote_fortress.BlockList()
	out.ParseFromString(received)

	return out


def GetTiletypeList():

	# create function request
	message_request = CoreProtocol.CoreBindRequest()
	message_request.method = "GetTiletypeList"
	message_request.input_msg = "dfproto.EmptyMessage"
	message_request.output_msg = "RemoteFortressReader.TiletypeList"
	message_request.plugin = "RemoteFortressReader"

	received = GetInfoFromDFHack(message_request, CoreProtocol.EmptyMessage())

	out = remote_fortress.TiletypeList()
	out.ParseFromString(received)

	return out


def GetMaterialList():

	# create function request
	message_request = CoreProtocol.CoreBindRequest()
	message_request.method = "GetMaterialList"
	message_request.input_msg = "dfproto.EmptyMessage"
	message_request.output_msg = "RemoteFortressReader.MaterialList"
	message_request.plugin = "RemoteFortressReader"

	received = GetInfoFromDFHack(message_request, CoreProtocol.EmptyMessage())

	out = remote_fortress.MaterialList()
	out.ParseFromString(received)

	return out

