"""
Open a port on the firewall

Assumes firewall is ufw

Test with:
    {"secret": "123456", "op": "open", "data": {"ip": "192.168.0.1"}}
    {"secret": "123456", "op": "close", "data": {"ip": "192.168.0.1"}}
"""
import ipaddress

from regent.service import Operation, Service


class FirewallOpen(Operation):
    PORTS = [22]
    COMMAND = "ufw allow proto tcp from {ip} to any port {port}"

    def prepare(self, data):
        """
        Validate the input and prepare the safe context
        """
        ip = data.get("ip")
        if not ip:
            raise ValueError("Missing IP")

        try:
            addr = ipaddress.ip_address(ip)
        except ValueError:
            raise ValueError("Invalid IP")

        if not addr.version == 4:
            raise ValueError("IPv4 only")

        if addr.is_private or addr.is_multicast:
            raise ValueError("IP not allowed")

        self.ip = ip

    def perform(self):
        """
        Open the firewall
        """
        from subprocess import call

        for port in self.PORTS:
            cmd = self.COMMAND.format(ip=self.ip, port=port)
            print(cmd)
            ok = call(cmd.split(" "))
            if ok != 0:
                raise ValueError("Failed to change firewall")


class FirewallClose(FirewallOpen):
    COMMAND = "ufw delete allow proto tcp from {ip} to any port {port}"


service = Service(
    socket_path="/tmp/regent-firewall.sock",
    socket_secret="123456",
)
service.register("open", FirewallOpen)
service.register("close", FirewallClose)
service.listen()
