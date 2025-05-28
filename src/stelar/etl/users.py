
from .base import Module

class UserModule(Module):
    """A module that installs a user.

    A STELAR user is defined in the data catalog. It is a package-derived 
    entity.
    """

    CURSOR_NAME = "users"

    def __init__(self, name: str, parent: Module = None, *, spec: dict):
        self.spec = spec
        if "username" not in spec:
            spec["username"] = name 

        # Because users are not deletable, we are a bit more careful
        # about the spec. We need to check if the user exists and if it does,
        # we need to update it.
        if any(k not in spec 
               or 
               not spec[k] 
               for k in ("email", "email_verified", "first_name", "last_name", "password")):
            raise ValueError(f"UserModule {name} is malformed")

        super().__init__(name, parent, spec=spec)

    def cursor(self):
        return getattr(self.catalog.client, self.CURSOR_NAME)

    def check_installed(self):
        """Check if the user exists.
        The method checks if the user exists in the data catalog.
        """
        return self.spec["username"] in self.cursor()
    
    def install(self):
        """Install the user.
        The method installs the user by calling the install method of each
        module in the package.
        """
        spec = self.spec | {"enabled": True}
        cursor = self.cursor()
        cursor.create(** spec)

    def uninstall(self):
        """Uninstall the user.

        This is tricky because user deletion is not supported in the data catalog.
        The uninstall of an existing user is basically marking her as disabled.
        """
        cursor = self.cursor()
        cursor.get(self.spec["username"]).delete()
