from __future__ import print_function

import os


DEBUG = os.getenv("DEBUG", False)


def debug(*msg):
    if DEBUG:
        print(*msg)
