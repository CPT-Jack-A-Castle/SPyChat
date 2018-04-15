#!/usr/bin/python
import socket, select, os, sys

if len(sys.argv) < 4:
    print('Usage: python server.py <host> <port> <key>')
    sys.exit(1)

SOCKET_LIST = [] # List with connected sockets

def server(host, port):
    running = True

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, int(port)))
    server_socket.listen(10)

    SOCKET_LIST.append(server_socket)

    #print("Chat server started on port %i" % int(port))

    while running:
        # get the list sockets which are ready to be read through select
        # 4th arg, time_out  = 0 : poll and never block
        ready_to_read,ready_to_write,in_error = select.select(SOCKET_LIST,[],[],0)

        for sock in ready_to_read:
            # a new connection request recieved
            if sock == server_socket:
                sockfd, addr = server_socket.accept()
                SOCKET_LIST.append(sockfd)
                #print "Client from %s connected" % addr[0]

                broadcast(server_socket, sockfd, "\rA client from [%s] entered our server\n" % addr[0])

            else:
                try:
                    data = sock.recv(1024)
                    if data:
                        data = data.strip()
                        # Send data to all clients
                        broadcast(server_socket, sock, '\r' + data)
                        #print(data.strip())
                        print('[%s] %s' % (addr[1], data.strip()))
                    else:
                        # remove the socket that's broken
                        if sock in SOCKET_LIST:
                            SOCKET_LIST.remove(sock)

                        # at this stage, no data means probably the connection has been broken
                        broadcast(server_socket, sock, "Client from (%s) left\n" % addr[0])

                # exception
                except:
                    broadcast(server_socket, sock, "Client from (%s) left\n" % addr[0])
                    continue

    server_socket.close()

# broadcast chat messages to all connected clients
def broadcast(server_socket, sock, message):
    for socket in SOCKET_LIST:
        # send the message only to peer
        if socket != server_socket and socket != sock :
            try :
                socket.send(message)
            except :
                # broken socket connection
                socket.close()
                # broken socket, remove it
                if socket in SOCKET_LIST:
                    SOCKET_LIST.remove(socket)

host = sys.argv[1]
port = sys.argv[2]
key = sys.argv[3]

# Start server
server(host, int(port))
