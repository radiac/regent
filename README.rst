======
Regent
======

A python framework for performing privileged tasks for untrusted users in the
absence of an admin.


==============
Regent backend
==============

Use this to build Regent backends to service requests from frontend apps.


Testing your backend manually
=============================

Regent uses human-readable JSON, terminated in a newline. Using ``socat``::

    socat - UNIX-CONNECT:/tmp/my-regent.sock

send the following, ending in a UNIX-style newline (``\n``):

    {"secret": "123456", "op": "my-op"}

and you'll receive your response::

    {"error": "something failed"}


Internal socket API
-------------------

This is the raw API between the frontend and backend. Knowledge of this will
not be required in normal Regent use if you're using a frontend.

A connection to the backend API should send a JSON object with the following
key/values:

    secret          Socket secret
    op              Operation name
    data            Optional: Data for the operation

The backend will return either:

    error           Error message

or

    success         True
    uid             Unique ID for this operation request, or null if complete
    data            Data from the operation or pending async auth

JSON objects should be terminated with a newline.

If the original operation requires an asynchronous authentication step, the
frontend should send the following JSON object:

    secret          Socket secret
    uid             UID for a stored operation request (passed from async auth)
    data            Data for authenticating the auth request
