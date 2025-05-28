
from .base import Module
from .s3 import FileModule


class PackageModule(Module):
    """A module that installs a package.

    A STELAR package is defined in the data catalog. It is a package-derived 
    entity.
    """

    def __init__(self, name: str, parent: Module = None, *, spec: dict):
        super().__init__(name, parent, spec=spec)
        self.spec = spec
        if "name" not in spec:
            spec["name"] = name
        
    def cursor(self):
        return getattr(self.catalog.client, self.CURSOR_NAME)

    def check_installed(self):
        """Check if the package exists.

        The method checks if the package exists in the data catalog.
        """
        return self.spec["name"] in self.cursor()

    def install(self):
        """Install the package.

        The method installs the package by calling the install method of each
        module in the package.
        """
        cursor = self.cursor()
        cursor.create(** self.spec)

    def uninstall(self):
        """Uninstall the package.

        The method uninstalls the package by calling the uninstall method of each
        module in the package.
        """
        cursor = self.cursor()
        cursor.get(self.spec["name"]).delete()


class DatasetModule(PackageModule):
    """A module that installs a dataset.

    A STELAR dataset is defined in the data catalog. It is a package-derived 
    entity.
    """
    CURSOR_NAME = "datasets"

    def add_resource(self, name, file: FileModule | None = None, spec: dict = {}):
        """Add a resource to the dataset.

        The method adds a resource to the dataset. The resource is defined by
        the spec.

        Args:
            name (str): The name of the resource.
            spec (dict): The specification of the resource. It should contain
                the necessary fields to create a resource in the data catalog.
        Returns:
            ResourceModule: The resource module that was added to the dataset.
        """
        aspec = spec.copy()
        if file is not None:
            aspec["url"] = file.url
            # aspec["mime_type"] = file.spec.get("mime_type", "application/octet-stream")

        res_module = ResourceModule(name, parent=self, spec=spec)
        res_module.require(self)
        if file is not None:
            res_module.require(file)

        return res_module
    

class ResourceModule(Module):
    """A module that installs a resource.

    A STELAR resource is defined in the data catalog. It is a package-derived 
    entity.
    """

    def __init__(self, name: str, parent: PackageModule, *, spec: dict = {}):
        super().__init__(name, parent=parent, spec=spec)
        self.require(parent)

    def find_in_parent(self):
        # Get the parent package
        cli = self.catalog.client
        if self.parent.installed:
            # Check if the resource exists in the package
            dset = cli.datasets.get(self.parent.spec["name"])

            for res in dset.resources:
                if self.matches(res):
                    return res
                
            return None
        else:
            return None

    def check_installed(self):
        # Get the parent package
        return self.find_in_parent() is not None

    def matches(self, res):
        """Check if the resource matches the spec.

        The method checks if the resource matches the spec.
        """
        return all(
            hasattr(res, k) and v == getattr(res, k)

            for k, v in self.spec.items())

    def install(self):
        cli = self.catalog.client
        parent_dset = cli.datasets.get(self.parent.spec["name"])
        parent_dset.add_resource(**self.spec)

    def uninstall(self):
        resource = self.find_in_parent()
        if resource is not None:
            resource.delete()


class ToolModule(PackageModule):
    """A module that installs a tool.

    A STELAR tool is defined in the data catalog. It is a package-derived 
    entity.
    """
    CURSOR_NAME = "tools"


class WorkflowModule(PackageModule):
    """A module that installs a workflow.

    A STELAR workflow is defined in the data catalog. It is a package-derived 
    entity.
    """
    CURSOR_NAME = "workflows"


class ProcessModule(PackageModule):
    """A module that installs a process.

    A STELAR process is defined in the data catalog. It is a package-derived 
    entity.
    """
    CURSOR_NAME = "processes"


class VocabularyModule(Module):
    """A module that installs a vocabulary.

    A STELAR vocabulary is defined in the data catalog. It is a package-derived 
    entity.
    """
    def __init__(self, name: str, *, tags: list[str] = [], spec: dict = {}):
        if "name" not in spec:
            spec["name"] = name
        if "tags" not in spec:
            spec["tags"] = tags

        super().__init__(name, spec=spec)

    def check_installed(self):
        return self.spec["name"] in self.catalog.client.vocabularies
    
    def install(self):
        cli = self.catalog.client
        cli.vocabularies.create(**self.spec)

    def uninstall(self):
        cli = self.catalog.client
        cli.vocabularies.get(self.spec["name"]).delete()


