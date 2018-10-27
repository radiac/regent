class Auth(object):
    """
    Asynchronous authorisation for operations
    """
    state = True

    def request(self, op):
        """
        Send the auth request

        Arguments:
            op      Operation

        Returns:
            msg     Message to send back to originating requester

        Note: the operation ID will not be the same when it comes to processing
        the response, so any data required to process the auth response will
        need to be stored as attributes on this class for serialisation.
        """
        raise NotImplementedError()

    def process(self, op, auth_data):
        """
        Process an auth response

        Arguments:
            op          Operation
            auth_data   Any data passed to the backend on the ``auth`` key of
                        the data from the originating requester.

        Note: the operation will have been given a new ID to reduce the
        opportunity for attacks on multi-stage authentication.
        """
        raise NotImplementedError()
