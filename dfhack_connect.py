__author__ = 'scorpheus'

import socket
import struct
import proto.build.RemoteFortressReader_pb2 as remote_fortress
import proto.build.BasicApi_pb2 as BasciApi
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


def send_message(id, message):
	values = (id, len(message))
	packer = struct.Struct('hi')
	packed_data = packer.pack(*values)

	sock.sendall(packed_data+message)


def GetAnswerHeader():
	received = sock.recv(8)
	state = struct.unpack('hi', received)
	return state[1] # size of the waiting message


def GetAnswer():
	received = sock.recv(GetAnswerHeader())
	return received


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


def GetDFVersion():     # example of how it works

	# get the id of the fonction in dfhack
	block = CoreProtocol.CoreBindRequest()
	block.method = "GetDFVersion"
	block.input_msg = "dfproto.EmptyMessage"
	block.output_msg = "dfproto.StringMessage"

	serialize_block = block.SerializeToString()

	# send the query with the header,
	# 0 is the id to call the method bind request
	send_message(0, serialize_block)

	# Receive data from the server
	received = GetAnswer()

	# receive the answer protobuf containing the id
	out_id = CoreProtocol.CoreBindReply()
	out_id.ParseFromString(received)

	# with the id, call the function and get the result
	# the function GetDFVersion just need an empty protobuf, but need a protobuf
	block = CoreProtocol.EmptyMessage()
	serialize_block = block.SerializeToString()

	send_message(out_id.assigned_id, serialize_block)

	# Receive data from the server
	received = GetAnswer()
	out = CoreProtocol.StringMessage()
	out.ParseFromString(received)


def GetBlockList():

	# get the id of the fonction in dfhack
	block = CoreProtocol.CoreBindRequest()
	# block.method = "ListEnums"
	# block.input_msg = "dfproto.EmptyMessage"
	# block.output_msg = "dfproto.ListEnumsOut"

	block.method = "GetBlockList"
	block.input_msg = "RemoteFortressReader.BlockRequest"
	block.output_msg = "RemoteFortressReader.BlockList"
	block.plugin = "RemoteFortressReader"

	# block.method = "GetGrowthList"
	# block.input_msg = "dfproto.EmptyMessage"
	# block.output_msg = "RemoteFortressReader.MaterialList"
	# block.plugin = "RemoteFortressReader"

	serialize_block = block.SerializeToString()

	send_message(0, serialize_block)

	# Receive data from the server
	received = GetAnswer()

	out_id = CoreProtocol.CoreBindReply()
	out_id.ParseFromString(received)

	# with the id call the function and get the result
	block = remote_fortress.BlockRequest()
	block.min_x = 0
	block.max_x = 2
	block.min_y = 0
	block.max_y = 2
	block.min_z = 3
	block.max_z = 5

	serialize_block = block.SerializeToString()

	send_message(out_id.assigned_id, serialize_block)

	# Receive data from the server
	received = GetAnswer()

	out = remote_fortress.BlockList()
	out.ParseFromString(received)