from regent.frontend import Client


client = Client(
    socket_path='/tmp/regent-whoami.sock',
    socket_secret='123456',
)

response = client.request('whoami')
print('I am {}'.format(response['data']))
