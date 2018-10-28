"""
Send a request to a backend
"""
from ..constants import SOCKET_TIMEOUT
from ..socket import Socket


class Client(object):
    def __init__(
        self,
        socket_path,
        socket_secret,
        socket_timeout=SOCKET_TIMEOUT,
    ):
        self.socket = Socket(socket_path, socket_secret, socket_timeout)

    def request(self, op_name, data=None):
        """
        Request an operation
        """
        return self.call_backend({
            'op': op_name,
            'data': data,
        })

    def auth(self, uid, data=None):
        """
        Authorise a suspended operation
        """
        return self.call_backend({
            'uid': uid,
            'data': data,
        })

    def call_backend(self, data):
        """
        Write to and read from the backend
        """
        self.socket.connect()
        self.socket.write(data)
        response = self.socket.read()
        self.socket.close()
        return response

    def close(self):
        """
        Call this once you're done with the client
        """
        self.socket.close()

    def reset(self):
        """
        Call this to reopen after closing
        """
        self.socket.init()
