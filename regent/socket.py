"""
Common socket tools
"""
from __future__ import absolute_import

import json
import os
import select
import socket

from .constants import SOCKET_PENDING
from .exceptions import SocketError, ProcessError


class BaseSocket(object):
    """
    Wrapper for socket which communicates using newline-terminated JSON objects

    Common functionality for server/client socket, and for new connections on
    a server
    """
    def __init__(self, socket, timeout):
        self.socket = socket
        self.timeout = timeout

    def write(self, data):
        raw = json.dumps(data)
        try:
            self.socket.send(raw + '\n')
        except socket.error:
            raise SocketError('Could not write to client')

    def read(self):
        raw = ''
        while not raw.endswith('\n'):
            # Use select so we can manage the timeout safely
            sockets = select.select(
                [self.socket], [], [], self.timeout,
            )[0]

            # If there's nothing to be read, connection failed
            if len(sockets) != 1:
                raise SocketError('Failed waiting for data')

            # Read and store
            try:
                chunk = self.socket.recv(4096)
            except socket.error:
                raise SocketError('Could not read from client')
            if len(chunk) == 0:
                raise SocketError('Unexpected end of data')
            raw += chunk

        try:
            data = json.loads(raw)
        except ValueError as e:
            raise ProcessError(
                'Invalid message, could not decode JSON: {}'.format(e),
            )

        return data

    def close(self):
        try:
            self.socket.close()
        except socket.error:
            raise SocketError('Client already disconnected')


class Socket(BaseSocket):
    def __init__(self, path, secret, timeout):
        self.path = path
        self.secret = secret
        self.timeout = timeout
        self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

    def listen(self):
        """
        Listen on a socket as a server
        """
        try:
            os.remove(self.path)
        except OSError:
            pass

        self.socket.bind(self.path)
        os.chmod(self.path, 0o777)

        # Queue up to SOCKET_PENDING connections
        self.socket.listen(SOCKET_PENDING)

    def accept(self):
        """
        Wait for a connection and accept it
        """
        client, address = self.socket.accept()
        return BaseSocket(client, self.timeout)

    def connect(self):
        """
        Connect to a socket as a client
        """
        self.socket.connect(self.path)

    def write(self, data):
        out = {
            'secret': self.secret,
        }
        out.update(data)
        super(Socket, self).write(out)
