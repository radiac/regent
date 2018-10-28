"""
Storage for backend serialisation
"""
import os

from ..exceptions import DoesNotExist


class Memory(object):
    """
    In-memory storage of frozen ops and auth
    """
    def __init__(self):
        self.data = {}

    def load(self, uid):
        if uid not in self.data:
            raise DoesNotExist()

        frozen_op, frozen_auth = self.data.pop(uid)
        return frozen_op, frozen_auth

    def save(self, uid, frozen_op, frozen_auth):
        self.data[uid] = (frozen_op, frozen_auth)


class Database(object):
    """
    Database storage
    """
    def __init__(self, db_path):
        self.db_path = db_path

        # ++ connect
        raise NotImplementedError()

        # Ensure private path exists and has correct ownership and permissions
        os.chown(self.db_path, os.getuid(), -1)
        os.chmod(self.db_path, 0o700)

    def load(self, op_id):
        raise NotImplementedError()

    def save(self, op_id, frozen_op, frozen_auth):
        raise NotImplementedError()
