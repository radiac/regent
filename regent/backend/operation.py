"""
Regent operation
"""
import random
import time


class Operation(object):
    def __init__(self):
        timestamp = str(time.time()).replace('.', '')
        self.uid = '{:0>12}{:0>9}'.format(
            timestamp,
            random.randint(0, 999999999),
        )

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
