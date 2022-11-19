"""
Regent service

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
import time
import traceback

from ..constants import SOCKET_TIMEOUT
from ..debug import debug
from ..exceptions import DoesNotExist, ProcessError, SocketError
from ..socket import Socket
from . import storage
from .auth import Auth
from .serialiser import deserialise


class Service(object):
    def __init__(
        self,
        socket_path,
        socket_secret,
        db_path=None,
        socket_timeout=SOCKET_TIMEOUT,
    ):
        """
        Create the socket path
        """
        self.operations = {}

        if db_path:
            self.db = storage.Database(db_path)
        else:
            self.db = storage.Memory()

        self.socket = Socket(socket_path, socket_secret, socket_timeout)

    def listen(self):
        """
        Main server loop
        """
        self.socket.listen()

        while 1:
            client = self.socket.accept()
            debug("Connected")

            try:
                request = client.read()
                debug("Received: {}".format(request))
                uid, data = self.process(request)
                client.write(
                    {
                        "success": True,
                        "uid": uid,
                        "data": data,
                    }
                )

            except Exception as e:
                # Try to report the error
                debug("Error processing request:", e, traceback.format_exc())
                try:
                    client.write(
                        {
                            "error": "{}".format(e),
                        }
                    )
                except SocketError:
                    # Fail silently if we can't talk to the client
                    # That may have been the original error
                    debug("Error writing to client")

            try:
                client.close()
            except SocketError:
                debug("Error closing client")
                continue

    def process(self, request):
        """
        Process a request

        Returns uid and response, raises ProcessError if anything goes wrong
        """
        # Check the secret
        if "secret" not in request or request["secret"] != self.socket.secret:
            # Auth failed.
            # Sleep for 1 sec - very basic protection against brute-forcing.
            # Given someone would already have shell access to the server
            # though to be able to write to the service, by the time this
            # becomes an issue you probably have more serious problems.
            time.sleep(1)
            raise ProcessError("Permission denied")

        # Prepare the operation
        if "op" in request:
            # New operation - check it's valid then create it
            if request["op"] not in self.operations:
                raise ProcessError("Unknown operation")

            op, auth = self.op_new(request["op"], request.get("data"))

        elif "uid" in request:
            # Existing operation - process it
            uid = request["uid"]
            op, auth = self.op_existing(uid, request.get("data"))

        else:
            raise ProcessError("Invalid message: operation not found")

        # Handle authentication response from op
        if auth is True:
            # Allow it to continue
            pass

        elif auth is False:
            raise ProcessError("Authorisation failed")

        elif isinstance(auth, Auth):
            # Send the auth request
            response = auth.request(op)

            # Out-of-stream authorisation required - put operation on hold
            frozen_op = op.serialise()
            frozen_auth = auth.serialise()
            self.db.save(op.uid, frozen_op, frozen_auth)

            return op.uid, response

        # Auth ok
        response = op.perform()
        return None, response

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
            op.prepare(data)
        except ValueError as e:
            raise ProcessError("Invalid data: {}".format(e))

        # Ask op if it wants to auth
        auth = op.auth()

        return op, auth

    def op_existing(self, uid, data):
        """
        Defrost and process auth for an existing operation on hold

        Returns:
            op      Operation instance
            auth    Result of processing the auth response
        """
        # Load existing op obj and its auth obj from the store
        try:
            frozen_op, frozen_auth = self.db.load(uid)
        except DoesNotExist:
            raise ProcessError

        # Deserialise
        try:
            op = deserialise(*frozen_op)
            auth_obj = deserialise(*frozen_auth)
        except ValueError as e:
            raise ProcessError(
                "Could not deserialise operation: {}".format(e),
            )

        # Process auth
        auth_obj.process(op, data)
        auth = op.auth_response(auth_obj)

        return op, auth

    def register(self, name, operation):
        self.operations[name] = operation
