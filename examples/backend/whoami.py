"""
Who Am I

See which user the service is running as

Test with:
    {"secret": "123456", "op": "whoami"}
"""
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
