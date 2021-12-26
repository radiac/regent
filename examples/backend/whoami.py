"""
Who Am I

See which user the backend is running as

Test with:
    {"secret": "123456", "op": "whoami"}
"""
import subprocess

from regent.backend import Operation, Server


class WhoAmI(Operation):
    def perform(self):
        value = subprocess.check_output("whoami")
        value = value.strip()
        return value


server = Server(
    socket_path="/tmp/regent-whoami.sock",
    socket_secret="123456",
)
server.register("whoami", WhoAmI)
server.listen()
