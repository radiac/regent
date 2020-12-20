"""
Example frontend to call examples/backend/firewall.py
"""
import time
import sys
from regent.frontend import Client


client = Client(
    socket_path='/tmp/regent-firewall.sock',
    socket_secret='123456',
)

response = client.request('open', {'ip': '8.8.8.8'})
if response.get('success'):
    print('Firewall open')
else:
    print('Error: {}'.format(response.get('error')))
    sys.exit(1)
client.close()

time.sleep(5)

client.reset()
response = client.request('close', {'ip': '8.8.8.8'})
if response.get('success'):
    print('Firewall closed')
else:
    print('Error: {}'.format(response.get('error')))
    sys.exit(1)
