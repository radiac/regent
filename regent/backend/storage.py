"""
Storage for backend serialisation
"""
import os


def Database(object):
    def __init__(self, db_path):
        self.db_path = db_path

        # ++
        return

        # Ensure private path exists and has correct ownership and permissions
        os.chown(self.db_path, os.getuid(), -1)
        os.chmod(self.db_path, 0700)

    def load(self, op_id):
        raise NotImplementedError()

    def save(self, op_id, frozen_op, frozen_auth):
        raise NotImplementedError()
