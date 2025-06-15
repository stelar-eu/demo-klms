from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from stelar.client import Rel, Relationship

from .base import Module, Node
from .s3 import FileModule

if TYPE_CHECKING:
    from stelar.client.package import PackageProxy


class PackageModule(Module):
    """A module that installs a package.

    A STELAR package is defined in the data catalog. It is a package-derived 
    entity.
    """

    def __init__(self, name: str, parent: Optional[Node] = None, *, spec: dict):
        super().__init__(name, parent, spec=spec)
        self.spec = spec
        if "name" not in spec:
            spec["name"] = name
        
    def cursor(self):
        return getattr(self.catalog.client, self.CURSOR_NAME)

    def installed_instance(self):
        return self.cursor().get(self.spec["name"])

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

        requires = [self]
        if isinstance(file, FileModule):
            aspec["url"] = file.url
            requires.append(file)

        res_module = ResourceModule(name, parent=self, spec=aspec)
        for r in requires:
            res_module.require(r)

        return res_module
    


class DatasetModule(PackageModule):
    """A module that installs a dataset.

    A STELAR dataset is defined in the data catalog. It is a package-derived 
    entity.
    """
    CURSOR_NAME = "datasets"



class ResourceModule(Module):
    """A module that installs a resource.

    A STELAR resource is defined in the data catalog. It is a package-derived 
    entity.
    """

    parent : PackageModule

    def __init__(self, name: str, parent: PackageModule, *, spec: dict = {}):
        super().__init__(name, parent=parent, spec=spec)
        self.require(parent)

    def parent_cursor(self):
        cli = self.catalog.client
        ptype = self.spec.get("package_type", "dataset")
        return cli.registry_for_type(ptype)

    def parent_instance(self) -> Optional[PackageProxy]:
        """Get the parent package instance.
        
        Returns:
            PackageModule: The parent package instance if it is installed, 
            otherwise None.
        """
        cli = self.catalog.client
        if self.parent.installed:
            ptype = self.spec.get("package_type", "dataset")
            cursor = self.parent_cursor()
            return cursor.get(self.parent.spec["name"])
        else:
            return None

    def find_in_parent(self):
        # Get the parent package
        cli = self.catalog.client
        dset = self.parent_instance()
        if dset is not None:
            for res in dset.resources:
                if self.matches(res):
                    return res
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
        parent_dset = self.parent_instance()
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


class LicenseModule(Module):
    CURSOR_NAME = "licenses"

    def __init__(self, name: str, parent: Node|None = None, *, spec: dict = {}):
        if "key" not in spec:
            spec["key"] = name
        super().__init__(name, parent, spec=spec)

    def cursor(self):
        return getattr(self.catalog.client, self.CURSOR_NAME)

    def installed_instance(self):
        return self.cursor().get(self.spec["key"])

    def check_installed(self):
        """Check if the package exists.

        The method checks if the package exists in the data catalog.
        """
        return self.spec["key"] in self.cursor()

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



class VocabularyModule(Module):
    """A module that installs a vocabulary.

    A STELAR vocabulary is defined in the data catalog. It is a package-derived 
    entity.
    """
    def __init__(self, name: str, parent: Node|None = None, *, tags: list[str] = [], spec: dict = {}):
        if "name" not in spec:
            spec["name"] = name
        if "tags" not in spec:
            spec["tags"] = tags

        super().__init__(name, parent, spec=spec)

    def check_installed(self):
        return self.spec["name"] in self.catalog.client.vocabularies
    
    def install(self):
        cli = self.catalog.client
        cli.vocabularies.create(**self.spec)

    def uninstall(self):
        cli = self.catalog.client
        cli.vocabularies.get(self.spec["name"]).delete()


class OrganizationModule(Module):
    """A module that installs an organization.

    A STELAR organization is defined in the data catalog. It is a package-derived 
    entity.
    """
    CURSOR_NAME = "organizations"

    def check_installed(self):
        return self.spec["name"] in self.catalog.client.organizations

    def install(self):
        cli = self.catalog.client
        cli.organizations.create(**self.spec)

    def uninstall(self):
        cli = self.catalog.client
        cli.organizations.get(self.spec["name"]).delete()


class RelationshipModule(Module):

    def __init__(self, name: str, parent: Optional[Node] = None, *, spec: dict):
        super().__init__(name, parent, spec=spec)
    
    def check_installed(self):
        try:
            subj = self.spec["subject"].installed_instance()
            obj = self.spec["object"].installed_instance()
            rel = self.spec["relationship"]

            return Relationship.from_triple(subj, rel, obj).exists()
        except Exception:
            return False
    
    def install(self):
        subj = self.spec["subject"].installed_instance()
        obj = self.spec["object"].installed_instance()
        rel = self.spec["relationship"]
        comment = self.spec.get("comment", None)

        return subj.add_relationship(rel, obj, comment=comment)
    
    def uninstall(self):
        subj = self.spec["subject"].installed_instance()
        obj = self.spec["object"].installed_instance()
        rel = self.spec["relationship"]

        subj.relationships.get(rel, obj).delete()
