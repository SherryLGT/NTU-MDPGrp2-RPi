#!/usr/bin/python

import socket
from threading import Thread, Event
from select import select
from enum import Enum
import time


class SocketServerChild(Thread):
    """
    SocketServerChild: class for use with SocketServer. Uses the Thread subclass.

    @socket: client tuple in the form of (socket, client_addr)
    @run: this function should be overwritten with client-handling code
    """

    def __init__(self, socket):
        Thread.__init__(self)

        self.socket, self.address = socket

    def recv(self, bytes=1024, timeout=None):
        """
        recv: read n bytes from socket. optional timeout
        @bytes: max bytes to read from the socket
        @timeout: timeout for the read procedure in seconds
        """

        if timeout:
            readable, writable, errored = select(
                [self.socket, ], [], [], timeout)
            if self.socket in readable:
                return self.socket.recv(bytes)
            else:
                return None
        else:
            return self.socket.recv(bytes)

    def send(self, data, timeout=None):
        """
        send: write data to the socket. optional timeout
        @data: data (str) to send to the socket
        @timeout: timeout for the send procedure in seconds
        """

        if timeout:
            readable, writable, errored = select(
                [self.socket, ], [], [], timeout)
            if self.socket in writable:
                return self.socket.send(data)
            else:
                return None
        else:
            return self.socket.send(data)

    def run(self):
        """ overwrite with initial server function """

        self.socket.close()


class BluetoothForwardServer(SocketServerChild):
    """ Threaded server example """

    def run(self):
        global bluetooth_server
        global tcp_server
        bluetooth_server = self
        global running
        while running:
            data = self.recv()
            tcp_server.send(data)
        self.socket.close()


class TCPForwardServer(SocketServerChild):
    """ Threaded server example """

    def run(self):
        global tcp_server
        global bluetooth_server
        tcp_server = self
        global running
        while running:
            data = self.recv()
            bluetooth_server.send(data)
        self.socket.close()


class SocketServer(object):
    """
    SocketServer class: creates a listening socket and spawns threads for every connected client

    @bind_socket: socket tuple in the form (ipaddr, socket) to bind to
    @callback: class with subclass of SocketServerChild to handle each client connection
    @max_connections: maximum number of concurrend client connections
    """

    thread_pool = []

    def __init__(self, bind_socket, socket_type, callback, max_connections=1):
        self.bind_socket = bind_socket
        self.max_connections = max_connections
        self.callback = callback
        self.socket_type = socket_type

    def serve_forever(self):
        if self.socket_type == SocketType.BLUETOOTH:
            self.sock = socket.socket(
                socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
        elif self.socket_type == SocketType.TCP:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(self.bind_socket)
        self.sock.listen(self.max_connections)

        global running
        while running:
            readable, writable, errored = select([self.sock, ], [], [], 1)
            if self.sock in readable:
                self.thread_pool.append(self.callback(self.sock.accept()))
                self.thread_pool[-1].start()

            # clean up
            for thread in self.thread_pool[:]:
                if not thread.is_alive():
                    self.thread_pool.remove(thread)

            # print len(self.thread_pool)


class SocketClient(object):
    """
    SocketClient class: connects to a socket server and communicates via socket protocol
    @host: host / ip address to connect to
    @prot: remote socket port to connect to
    """

    def __init__(self, host, port):
        self.host = host
        self.port = port

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))

    def recv(self, bytes=1024, timeout=None):
        """
        recv: read n bytes from socket. optional timeout
        @bytes: max bytes to read from the socket
        @timeout: timeout for the read procedure in seconds
        """

        if timeout:
            readable, writable, errored = select(
                [self.socket, ], [], [], timeout)
            if self.socket in readable:
                return self.socket.recv(bytes)
            else:
                return None
        else:
            return self.socket.recv(bytes)

    def send(self, data, timeout=None):
        """
        send: write data to the socket. optional timeout
        @data: data (str) to send to the socket
        @timeout: timeout for the send procedure in seconds
        """

        if timeout:
            readable, writable, errored = select(
                [self.socket, ], [], [], timeout)
            if self.socket in writable:
                return self.socket.send(data)
            else:
                return None
        else:
            return self.socket.send(data)

    def close(self):
        self.socket.close()


class SocketType(Enum):
    BLUETOOTH = 1
    TCP = 2
    USB = 3


def start_bt_server():
    server = SocketServer(('B8:27:EB:CD:16:89', 10),
                          SocketType.BLUETOOTH, BluetoothForwardServer)
    server.serve_forever()


def start_tcp_server():
    server = SocketServer(('10.42.0.102', 8888),
                          SocketType.TCP, TCPForwardServer)
    server.serve_forever()


if __name__ == '__main__':
    global running
    running = True
    t1 = Thread(target=start_bt_server)
    t1.start()
    t2 = Thread(target=start_tcp_server)
    t2.start()
    raw_input('Press enter to quit.')
    print("attempting to close threads.")
    running = False
    t1.join()
    t2.join()
    print("threads successfully closed")
