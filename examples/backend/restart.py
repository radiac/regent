"""
Restart the machine
"""
from subprocess import call

from regent.service import Operation, Service, auth


class Restart(Operation):
    def prepare(self, data):
        """
        Validate the input and prepare the safe context
        """
        service_name = data.get("service_name")
        if not service_name:
            raise ValueError("Missing service name")

        if service_name not in ["nginx", "supervisor"]:
            raise ValueError("Unexpected service name")

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
        if self.service_name == "nginx":
            return True

        # Other operations need to be checked
        return auth.Email(
            to="me@example.com",
            subject="Server wants to restart",
            body="Really restart {}?".format(self.service_name),
        )

    def auth_response(self, auth):
        """
        Process an auth response

        Opportunity to perform tasks after auth is received

        Same return values as auth()
        """
        from .myproject import send_admin_email

        send_admin_email("Restarting {}".format(self.service_name))
        return auth.state

    def perform(self):
        """
        Perform the operation on the service name from the context
        """
        call(["service", "restart", self.service_name])


service = Service(
    socket_path="/tmp/regent-restart.sock",
    socket_secret="123456",
)
service.register("restart", Restart)
service.listen()
