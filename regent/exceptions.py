"""
Regent exceptions
"""


class SocketError(Exception):
    """
    A low-level socket error
    """
    pass


class ProcessError(Exception):
    """
    An error processing the request
    """
    pass


class DoesNotExist(Exception):
    """
    Object in database does not exist
    """
    pass
