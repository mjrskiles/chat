"""
CSC376 Assignment 3 - Chat
Server
Michael Skiles
"""

import threading
import sys
import os
import socket

def usage( script_name ):
    print( 'Usage: python3 ' + script_name + ' <port number>' )

argv = sys.argv
argc = len( sys.argv )
if argc != 2:
    usage( sys.argv[0] )
    os.exit(1)

def parse_opts( argv ):
    port = ''
    host = 'localhost'

    try:
        port = argv[1]

        # make sure the port argument is an int, throws ValueError
        int(port)
    except (IndexError, ValueError):
        print("The port number was either not specified, or not an integer")
        sys.exit()

    return (port, host)

class Server:

    #The client_socks dict is a dictionary with an client id int
    #as the key, followed by a list in form [socket, thread instance, client username]
    SOCKET_POS = 0
    INSTANCE_POS = 1
    CLIENT_NAME_POS = 2
    client_socks = {}
    listen_sock = None

    def __init__( self, port ):
        self.port = port
        self.open_listener( self.port )

    def open_listener( self, port ):
        self.listen_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listen_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.listen_sock.bind( ('localhost', int(port)) )
        self.listen_sock.listen(5)

    def get_new_client( self ):
        next_client = 0
        try:
            while True:
                sock, addr = self.listen_sock.accept()
                print("Connection accepted, addr: " + str(addr) + " client no. " + str(next_client))
                instance = threading.Thread( target=self.get_messages, args=(sock, next_client) )
#                print("instance created.")
                instance.start()
                self.client_socks[next_client] = [sock, instance, '']
                next_client += 1
        finally:
            self.listen_sock.close()

    def get_messages( self, sock, id ):
        print("Thread opened @client " + str(id))
        message = sock.recv( 4096 )
        client_name = message.decode().strip()
        self.client_socks[id][self.CLIENT_NAME_POS] = client_name
        print( 'Client@client ' + str(id) + ' entered their name as ' + client_name )
        while True:
            message = sock.recv( 4096 )
            print( client_name + ': ' + message.decode(), end='' )
            self.broadcast_msg( id, message.decode() )
            if not message:
                break
        sock.close()
        self.client_socks.pop(id)
        print( client_name + ' disconnected and the socket was successfully closed.' )

    def broadcast_msg( self, client_id, message ):
        line_to_send = self.client_socks[client_id][self.CLIENT_NAME_POS] + ': ' + message
        for c in self.client_socks:
            if c != client_id:
                sock = self.client_socks[c][self.SOCKET_POS]
                send_instance = threading.Thread( target=self.send_msg, args=(sock, c, client_id, line_to_send) )
                send_instance.start()

    def send_msg( self, sock, id_to, id_from, message ):
        try:
            sock.send( message.encode() )
        except:
            to_name = self.client_socks[id_to][CLIENT_NAME_POS]
            from_name = self.client_socks[id_from][CLIENT_NAME_POS]
            print('Sending message to ' + to_name + ' from ' + from_name + ' failed.')


def main():
    port, host = parse_opts(argv)
    s = Server(port)
    s.get_new_client()

main()
