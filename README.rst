======
Regent
======

A Python framework to allow untrusted users to perform privileged system tasks.


Overview
========

Regent comes in two parts:

* a service which runs as the privileged system user, defines a set of operations it
  will perform, and listens for requests on a linux socket file
* a client library to ask the service to perform the operations

A service is intended for use with clients on a single host. Alternatively its socket
can be mounted within a docker container to control its host or other containers.

The authentication system is designed on the assumption that the unprivileged user is
untrusted and can be compromised. For non-harmful operations a basic shared key will
deter casual attackers, and for more high-risk commands it supports out-of-channel
activation, to allow two-factor authentication or administrator approval.


Example
=======

A service which defines a system command (`whoami`) and returns its output::

    import subprocess

    from regent.service import Operation, Service


    class WhoAmI(Operation):
        def perform(self):
            value = subprocess.check_output("whoami")
            value = value.strip()
            return value


    service = Service(
        socket_path="/tmp/regent-whoami.sock",
        socket_secret="123456",
    )
    service.register("whoami", WhoAmI)
    service.listen()


A client which calls the service::

    from regent.client import Client

    client = Client(
        socket_path="/tmp/regent-whoami.sock",
        socket_secret="123456",
    )

    response = client.request("whoami")
    print(response["data"])


More complicated examples can be found in the `examples` dir, including:

* make changes to the firewall
* restart the server


Implementation
==============

Testing your service manually
-----------------------------

Regent uses human-readable JSON, terminated in a newline. Using ``socat``::

    socat - UNIX-CONNECT:/tmp/my-regent.sock

send the following, ending in a UNIX-style newline (``\n``):

    {"secret": "123456", "op": "my-op"}

and you'll receive your response::

    {"error": "something failed"}


Internal messaging API
----------------------

This is the raw API between the client and service. Knowledge of this will not be
required in normal Regent use if you're using a client.

A connection to the service API should send a JSON object with the following
key/values:

    secret          Socket secret
    op              Operation name
    data            Optional: Data for the operation

The service will return either:

    error           Error message

or

    success         True
    uid             Unique ID for this operation request, or null if complete
    data            Data from the operation or pending async auth

JSON objects should be terminated with a newline.

If the original operation requires an asynchronous authentication step, the
client should send the following JSON object:

    secret          Socket secret
    uid             UID for a stored operation request (passed from async auth)
    data            Data for authenticating the auth request
