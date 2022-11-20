"""
Example client to call examples/service/whoami.py
"""
from regent.client import Client

client = Client(
    socket_path="/tmp/regent-whoami.sock",
    socket_secret="123456",
)

response = client.request("whoami")
print(response["data"])
