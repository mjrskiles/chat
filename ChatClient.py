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

class Client:
    sock = None

    def __init__( self, port, host ):
        self.host = host
        self.port = port
        self.start_connection( self.port )

    def start_connection( self, port ):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect( (self.host, int(self.port)) )
        if self.sock is None:
            print("Could not open socket.")
            os.exit(1)

    def run_client( self ):
        msg_receiver = threading.Thread( target=self.get_messages )
        msg_receiver.start()
        self.get_input()

    def get_messages( self ):
        message = self.sock.recv( 4096 )
        while message:
            print( message.decode(), end='' )
            message = self.sock.recv( 4096 )
        self.clean_up()

    def get_input( self ):
        for line in sys.stdin:
            self.sock.send( line.encode() )
        self.clean_up()

    def clean_up( self ):
        self.sock.close()
        os._exit(0)

def main():
    port, host = parse_opts(argv)
    client = Client( port, host )
    client.run_client()

main()