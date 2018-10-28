"""
Open a port on the firewall

Assumes firewall is ufw
"""
import ipaddress

from regent.backend import Server, Operation


class FirewallOpen(Operation):
    PORTS = [22]
    COMMAND = 'ufw allow proto tcp from {ip} to any port {port}'

    def prepare(self, data):
        """
        Validate the input and prepare the safe context
        """
        ip = data.get('ip')
        if not ip:
            raise ValueError('Missing IP')

        try:
            addr = ipaddress.ip_address(ip)
        except ValueError:
            raise ValueError('Invalid IP')

        if not addr.version == 4:
            raise ValueError('IPv4 only')

        if (
            addr.is_private or
            addr.is_multicast or
            not addr.is_global
        ):
            raise ValueError('IP not allowed')

        self.ip = ip

    def perform(self):
        """
        Open the firewall
        """
        from subprocess import call
        for port in self.PORTS:
            call(self.COMMAND.format(ip=self.ip, port=port).split(' '))


class FirewallClose(FirewallOpen):
    COMMAND = 'ufw delete proto tcp from {ip} to any port {port}'


server = Server(
    socket_path='/tmp/regent-firewall.sock',
    socket_secret='123456',
)
server.register('open', FirewallOpen)
server.register('close', FirewallClose)
server.listen()
