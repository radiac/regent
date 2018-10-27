"""
Regent backend server

Socket Protocol
---------------

Message is a JSON string, with its length prepended in first 4 bytes.

Version: 1

Once decoded, the JSON string contains:
    {
        'version':  1,
        'data':     <json data object>
    }
"""
import json
import os
import socket
import select
import struct

from ..exceptions import ProcessError
from .storage import Database


class Server(object):
    def __init__(self, socket_path, socket_secret, db_path):
        """
        Create the socket path
        """
        self.socket_path = socket_path
        self.socket_secret = socket_secret

        # Operations registry
        self.operations = {}

        self.db = Database(db_path)

        self.open_socket()

    def open_socket(self):
        # Open the socket
        self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            os.remove(self.socket_path)
        except OSError:
            pass
        self.socket.bind(self.socket_path)
        os.chmod(self.socket_path, 0777)

        # Queue up to 5 connections
        self.socket.listen(5)

    def run(self):
        """
        Main server loop
        """
        while 1:
            client, address = self.socket.accept()
            try:
                msg = self.process_connection(client)
                client.send(json.dumps({'success': msg}))
            except Exception, e:
                # Try to report the error
                try:
                    client.send(json.dumps({'error': str(e)}))
                except:
                    # Fail silently if we can't talk to the client
                    # That may have been the original error
                    pass
            try:
                client.close()
            except Exception, e:
                pass

    def process_connection(self, client):
        """
        Deal with a new connection

        Returns response string, raises ProcessError if anything goes wrong
        """
        # Read message length and unpack it into an integer
        raw_msglen = self.read(client, 4)
        if not raw_msglen:
            raise ProcessError('Invalid message length')
        msglen = struct.unpack('>I', raw_msglen)[0]

        # Read message
        encoded = self.read(client, msglen)
        try:
            request = json.loads(encoded)
        except ValueError:
            raise ProcessError('Invalid message: could not decode JSON')

        # Check the secret
        if 'secret' not in request or request['socket'] != self.socket_secret:
            # Auth failed.
            # Sleep for 1 sec - very basic protection against brute-forcing.
            # Given someone would already have shell access to the server
            # though to be able to write to the backend, by the time this
            # becomes an issue you probably have more serious problems.
            time.sleep(1)
            raise ProcessError('Permission denied')

        # Get the operation name
        if 'op' not in request:
            raise ProcessError('Invalid message: operation not found')
        op_name = request['op']
        if op_name not in self.operations:
            raise ProcessError('Unknown operation')

        data = request.get('data')

        return self.process_request(client, op_name, data)

    def read(self, client, msglen):
        """
        Read a message of a given length
        """
        msg = ''
        while len(msg) < msglen:
            # Use select so we can manage the timeout safely
            sockets = select.select(
                [client], [], [], settings.SOCKET_TIMEOUT,
            )[0]

            # If there's nothing to be read, connection failed
            if len(sockets) != 1:
                raise ProcessError('Failed waiting for data')

            # Read and store
            packet = client.recv(msglen - len(msg))
            if packet == '':
                raise ProcessError('Unexpected end of data')
            msg += packet
        return msg

    def process_request(self, client, op_name, data):
        """
        Process a request

        Returns response string, raises ProcessError if anything goes wrong
        """
        # Either deserialise existing or create a new operation instance
        if 'id' in data:
            op, auth = self.op_existing(op_name, data)
        else:
            op, auth = self.op_new(op_name, data)

        # Handle authentication response from op
        if auth is True:
            # Allow it to continue
            pass

        elif auth is False:
            raise ProcessError('Authorisation failed')

        elif isinstance(auth, Auth):
            # Send the auth request
            msg = auth.request(op)

            # Out-of-stream authorisation required - put operation on hold
            frozen_op = op.serialise()
            frozen_auth = auth.serialise()
            self.db.save_frozen(op.id, frozen_op, frozen_auth)

            return msg

        # Auth ok
        op.perform()
        return op.complete_msg

    def op_existing(self, op_name, data):
        """
        Defrost and process auth for an existing operation on hold

        Returns:
            op      Operation instance
            auth    Result of processing the auth response
        """
        # Load existing op obj and its auth obj from the store
        try:
            frozen_op, frozen_auth = self.db.load(data['id'])
        except db.DoesNotExist:
            raise ProcessError

        # Deserialise
        try:
            op = deserialise(frozen_op)
            auth_obj = deserialise(frozen_auth)
        except ValueError as e:
            raise ProcessError(
                'Could not deserialise operation: {}'.format(e),
            )

        # Process auth
        auth_obj.process(op, data)
        auth = op.auth_response(auth_obj)

        return op, auth

    def op_new(self, op_name, data):
        """
        Create a new operation

        Returns:
            op      Operation instance
            auth    Whether the op wants auth (or is rejecting request)
        """
        # Create new op obj and prepare the data
        op = self.operations[op_name]()
        try:
            op.prepare(data['data'])
        except ValueError as e:
            raise ProcessError('Invalid data: {}'.format(e))

        # Ask op if it wants to auth
        auth = op.auth()

        return op, auth

    def register(self, name, operation):
        self.operations[name] = operation
