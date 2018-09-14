import zmq
import sys
import hashlib

partSize = 1024 * 1024 * 10

def uploadFile2(filename, socket):
	with open(filename, "rb") as f:
		finished = False
		part = 0
		while not finished:
			print("Uploading part {}".format(part))
			f.seek(part*partSize)
			bt = f.read(partSize)
			socket.send_multipart([filename, bt])
			response = socket.recv()
			print("Received reply  [%s ]" % (response))
			part = part + 1
			if len(bt) < partSize:
				finished = True

def computeHashFile(filename):
	BUF_SIZE = 65536  # lets read stuff in 64kb chunks!
	sha1 = hashlib.sha1()

	with open(filename, 'rb') as f:
		while True:
			data = f.read(BUF_SIZE)
			if not data:
				break
			sha1.update(data)
	return sha1.hexdigest()

def computeHash(bytes):
	sha1 = hashlib.sha1()
	sha1.update(bytes)
	return sha1.hexdigest()

def uploadFile(context, username, filename, servers, proxy):
	sockets = []
	for ad in servers:
		s = context.socket(zmq.REQ)
		s.connect("tcp://"+ ad.decode("ascii"))
		sockets.append(s)

	with open(filename, "rb") as f:
		completeSha1= bytes(computeHashFile(filename), "ascii")
		finished = False
		shacu = []
		part = 0
		while not finished:
			print("Uploading part {}".format(part))
			f.seek(part*partSize)
			bt = f.read(partSize)
			sha1bt = bytes(computeHash(bt), "ascii")
			shacu.append(sha1bt)
			s = sockets[part % len(sockets)]
			s.send_multipart([b"upload", filename, bt, sha1bt, completeSha1])

			response = s.recv()
			print("Received reply for part {} ".format(part))
			part = part + 1
			if len(bt) < partSize:
				finished = True

		dicc = index(username, filename, shacu, completeSha1)
		print (type(dicc), dicc)
		# proxy.send_multipart(b"table", dicc)
		# r = proxy.recv()
		# print (r)

def index(username, filename, shacu, shacomplete):
	# nombre archivo, sha complete, sha1 c/u
	# index = {'filename':filename, 'sha_cada_parte':shacu, 'shacomplete': shacomplete}
	index = {}
	index[username] = filename
	return index


def download(context , filename, username):
	sockets = []


def main():
	if len(sys.argv) != 4:
		print("Must be called with a filename")
		print("Sample call: python ftclient <username> <operation> <filename>")
		exit()


	username = sys.argv[1]
	operation = sys.argv[2]
	filename = sys.argv[3].encode('ascii')

	context = zmq.Context()
	proxy = context.socket(zmq.REQ)
	proxy.connect("tcp://localhost:6666")

	print("Operation: {}".format(operation))
	if operation == "upload":
		proxy.send_multipart([b"availableServers"])
		servers = proxy.recv_multipart()
		print("There are {} available servers".format(len(servers)))
		uploadFile(context, username, filename, servers, proxy)
		print("File {} was uploaded.".format(filename))
	elif operation == "download":
		print("Not implemented yet")
	elif operation == "share":
		print("Not implemented yet")
	else:
		print("Operation not found!!!")

if __name__ == '__main__':
	main()
