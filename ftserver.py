
import zmq
import sys

def main():
	if len(sys.argv) != 4:
		print("Sample call: python ftserver <address> <port> <folder>")
		exit()

	clientsPort = sys.argv[2]
	clientsAddress = sys.argv[1]
	serversFolder = sys.argv[3]
	clientsAddress = clientsAddress + ":" + clientsPort

	context = zmq.Context()
	proxy = context.socket(zmq.REQ)
	proxy.connect("tcp://localhost:5555")

	clients = context.socket(zmq.REP)
	clients.bind("tcp://*:{}".format(clientsPort))

	proxy.send_multipart([b"newServer", bytes(clientsAddress, "ascii")])
	m = proxy.recv()
	print(m)

	while True:
		print("Waitting for users!")
		operation, *rest = clients.recv_multipart() # ERROR
		print ("Esta es la operacion: ", operation)
		if operation == b"upload":
			print("almenos entre")
			filename, byts, sha1byts, sha1complete = rest
			storeAs = serversFolder + sha1byts.decode("ascii")
			print("Storing {}".format(storeAs))
			with open(storeAs, "wb") as f:
				f.write(byts)
			print("Uploaded as {}".format(storeAs))

		else:
			print("Unsupported operation: {}".format(operation))


		clients.send(b"Done")

if __name__ == '__main__':
	main()
