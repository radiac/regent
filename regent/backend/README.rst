========================
Regent backend framework
========================

Use this to build Regent backends to service requests from frontend apps.


Example::

    from regent.backend import Server, Operation, auth

    class Restart(Operation):
        def prepare(self, data):
            """
            Validate the input and prepare the safe context
            """
            service_name = data.get('service_name')
            if not service_name:
                raise ValueError('Missing service name')

            if service_name not in ['nginx', 'supervisor']:
                raise ValueError('Unexpected service name')

            self.service_name = service_name

        def auth(self):
            """
            Check for or request authorisation to proceed

            Return:
                True        if authorisation succeeded
                False       if it failed
                Auth        ``Auth`` subclass instance if operation is on hold
            """
            # Allow nginx restarts straight through
            if self.service_name == 'nginx':
                return True

            # Other operations need to be checked
            return auth.Email(
                to='me@example.com',
                subject='Server wants to restart',
                body=f'Really restart {self.service_name}? {{ link }}',
            )

        def auth_response(self, auth):
            """
            Process an auth response

            Opportunity to perform tasks after auth is received

            Same return values as auth()
            """
            from .myproject import send_admin_email
            send_admin_email(f'Restarting {self.service_name}')
            return auth.state

        def perform(self):
            """
            Perform the operation on the service name from the context
            """
            from subprocess import call
            call(['service', 'restart', self.service_name])


    server = Server(
        socket='/tmp/regent-restart.sock',
        secret='123456',
    )
    server.register('restart', Restart)
    server.listen()


Example 2:

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
        socket='/tmp/regent-restart.sock',
        secret='123456',
    )
    server.register('open', FirewallOpen)
    server.register('close', FirewallClose)
    server.listen()
