"""
Regent operation
"""
import time


class Operation(object):
    def __init__(self):
        # Generate unique ID in case it needs auth/serialisation
        self._id = '{}-{:0>9}'.format(time.time(), random.randint(0,999999999))

    @property
    def id(self):
        """
        Getter for ID

        The ID is stored on _id so it isn't serialised as part of the object,
        so that when the op is deserialised a new ID will be generated. This
        will make it significantly harder to guess the ID when attacking a
        multi-stage authentication
        """
        return self._id

    def prepare(self, data):
        """
        Validate and clean the input and store any data on ``self`` as
        attributes.

        Raise ValueError if there is a problem with the data.
        """
        return

    def auth(self):
        """
        Check for or request authorisation to proceed

        Return:
            True        if authorisation succeeded
            False       if it failed
            Auth        ``Auth`` subclass instance if operation is on hold
        """
        return True

    def auth_response(self, auth):
        """
        Perform an action after an auth response.

        This will only be called if ``auth()`` returns an ``Auth`` instance.

        It is called regardless of whether the auth succeeded or failed.

        Provides the opportunity to perform tasks after auth is received, or
        to return another ``Auth`` instance for multi-stage authentication.

        Return:
            True        if authorisation succeeded
            False       if it failed
            Auth        ``Auth`` subclass instance if operation is on hold
        """
        return auth.state

    def perform(self):
        """
        Perform the operation
        """
        pass
