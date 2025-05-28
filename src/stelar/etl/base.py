"""
Set up testing environment for the project.

"""
from __future__ import annotations

import re
# from typing import TYPE_CHECKING, Callable    
from collections import deque
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from stelar.client import Client


class Catalog:
    def __init__(self):
        self.root = {}
        self.goal = {}
        self.client: Client = None

    def add(self, child):
        """Add a child node to this catalog.

        Args:
            child (Node): The child node to add.
        """
        if isinstance(child, list | set):
            for c in child:
                self.add(c)
            return

        if not isinstance(child, Node):
            raise ValueError("Child must be a Node")
        if child.name in self.root:
            raise ValueError(f"Child with name {child.name} already exists")
        if child.parent is not None:
            raise ValueError("Adding a non-toplevel item is not supported")
        if child.catalog is not None:
            raise ValueError(f"Child {child.name} already has a catalog")

        # Add the child to this catalog's root
        child.catalog = self
        self.root[child.name] = child

    def __iadd__(self, child):
        """Add a child node to this catalog.

        Args:
            child (Node): The child node to add.
        """
        self.add(child)
        return self

    def get(self, fullname, default=None):
        """Get a child node by name.

        Args:
            name (str): The name of the child node to get.
            default (Node): The default value to return if the child node is not found. Defaults to None.
        """
        names = fullname.split(".")
        if len(names) == 0:
            raise ValueError(f"Name must be a non-empty string, got {fullname}")
        d = self.root
        for name in names:
            if name not in d:
                return default
            obj = d[name]
            d = obj.children
        return obj

    def __getitem__(self, fullname):
        """Get an attribute of this catalog.

        If the attribute is not found, check if it is a child of this catalog.
        """
        r = self.get(fullname)
        if r is None:
            raise KeyError(f"{self.__class__.__name__} object has no attribute {fullname}")
        return r
    
    def __contains__(self, fullname):
        """Check if this catalog has a child with the given name.

        Args:
            name (str): The name of the child node to check.
        """
        return self.get(fullname) is not None

    def get_package(self, fullname: str) -> Package:
        """Get a package by name, creating it if it does not exist.

        Args:
            fullname (str): The name of the package to get.
        """
        names = fullname.split(".")
        if len(names) == 0:
            raise ValueError(f"Name must be a non-empty string, got {fullname}")
        obj = self
        d = self.root
        for name in names:
            if name not in d:
                p = Package(name)
                obj.add(p)
                obj = p
            else:
                obj = d[name]
                if not isinstance(obj, Package):
                    raise ValueError(f"Name {fullname} is not a package")
                d = obj.children
        return obj

    def modules(self):
        """Return the modules in this catalog.

        The method returns an iterable of all the modules in this catalog, including sub-modules.
        """
        for child in self.root.values():
            if isinstance(child, Module):
                yield child
            elif isinstance(child, Package):
                yield from child.modules()
            else:
                raise ValueError(f"Child {child.name} is not a module or a package")
            
    def all_modules(self):
        """Return an iterator over all modules and submodules in this catalog.
        """
        for child in self.root.values():
            if isinstance(child, Module):
                yield child
                yield from child.all_submodules()
            elif isinstance(child, Package):
                yield from child.all_modules()
            else:
                raise ValueError(f"Child {child.name} is not a module or a package")

    def strongly_connected_index(self) -> dict[str, int]:
        """Compute the strongly connected index for a set of modules.

        The SCI of a module has the following properties:
        - If a module m1 is required by a module m2, then SCI(m1) <= SCI(m2).
        - If SCI(m1) == SCI(m2), then m1 and m2 each require the other.

        The SCI is used to sort the module operations needed:
        All module installs will happen in increasing SCI order
        All module uninstalls will happen in decreasing SCI order

        This assumes that for mutually required modules the installation/uninstall 
        order does not matter.
        """

        # This implementation is based on the SCC algorithm from Kosaraju
        # and Tarjan, which is a linear time algorithm for finding strongly connected components

        for m in self.all_modules():
            m.scc_index = None

        # First, iterate over all modules and start a DFS from each
        visited = set()
        stack = deque(('visit', m) for m in self.all_modules())

        # L is a stack of modules to be postvisited
        L = deque()

        while stack:
            # Visit the top of the stack
            top = stack.pop()
            match top:
                case ('visit', m):
                    # If top is unvisited, mark it as visited and add it to the stack
                    if m not in visited:
                        visited.add(m)
                        stack.append(('push', m))
                        for n in m.enabled:
                            stack.append(('visit', n))
                case ('push', m):
                    # If top is postvisited, add it to the list
                    L.append((m, m))
                case _:
                    raise ValueError(f"Unknown command {top[0]} in stack")

        scc_index = 0

        # Iterate over L and start a DFS in the reverse direction
        while L:
            m, sccbase = L.pop()
            if m.scc_index is None:
                if m is sccbase:
                    sccbase.scc_index = scc_index
                    scc_index += 1
                else:
                    m.scc_index = sccbase.scc_index
                for n in m.required:
                    L.append((n, sccbase))


# Now, iterate over all modules and set the SCI
NODE_NAME_REGEX = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*$")


def check_node_name(name: str):
    """Check if the name is valid.

    Args:
        name (str): The name to check.
    Raises:
        ValueError: If the name is not valid.
    """
    if not isinstance(name, str):
        raise ValueError(f"Name must be a string, got {type(name)}")
    if not NODE_NAME_REGEX.match(name):
        raise ValueError(f"Name must match regex {NODE_NAME_REGEX.pattern}, got {name}")
    if len(name) > 255:
        raise ValueError(f"Name must be less than 255 characters, got {len(name)}")


class Node:
    """A node is a module or a package.

    A node is a part of a tree structure, where each node can have multiple children.
    The root node is the top-level node in the tree, and it has no parent.
    Each node can have multiple children, which are the nodes that are directly below it in the tree.
    Each node can also have one parent, which is the node that is directly above it in the tree.

    A node can be either a module or a package. A module is a collection of KLMS resources
    (datasets, files, buckets, setting, etc). A package is a collection of modules and other 
    packages.
    """

    catalog : Catalog = None  # The catalog this node belongs to

    def __init__(self, name, parent=None):
        """Initialize a node.
        Args:
            name (str): The name of the node.
            parent (Node): The parent node of this node. Defaults to None.
        """
        check_node_name(name)      
        self.name = name
        self.parent = parent
        self.children = {}
        if parent is not None:
            parent.add(self)

    def add(self, child):
        """Add a child node to this node.

        Args:
            child (Node): The child node to add.
        """
        if not isinstance(child, Package | Module):
            raise ValueError("Child must be a Package or Module")
        if child.name in self.children:
            raise ValueError(f"Child with name {child.name} already exists")
        if child.parent is not None and child.parent is not self:
            raise ValueError("Child's parent must be this node")
        if child.catalog is not None:
            raise ValueError(f"Child {child.name} already has a catalog")

        # Add the child to this node's children
        if child.parent is None:
            child.parent = self
        child.catalog = self.catalog
        self.children[child.name] = child

    def __iadd__(self, child):
        """Add a child node to this node.

        Args:
            child (Node): The child node to add.
        """
        self.add(child)
        return self

    def ancestors(self):
        """Get the ancestors of this node.

        The method returns a list of the node itself, followed by the node's parent's ancestors (if the parent exists).
        The list is in the order of the node itself, then its parent, then its grandparent, and so on.    
        """
        p = self
        anc = []
        while p is not None:
            anc.append(p)
            p = p.parent
        return anc
 
    @property
    def fullname(self):
        """Get the full name of this node.

        The full name is the name of this node, plus the names of all its parents, separated by dots.
        """
        return ".".join(a.name for a in reversed(self.ancestors()))

    def __getitem__(self, name):
        """Get a child node by name.

        Args:
            name (str): The name of the child node to get.
        """
        if name in self.children:
            return self.children[name]
        raise KeyError(f"{self.__class__.__name__} object has no child {name}")

    def __contains__(self, name):
        """Check if this node has a child with the given name.

        Args:
            name (str): The name of the child node to check.
        """
        return name in self.children

    def __repr__(self):
        """Get a string representation of this node.

        The string representation is the class name and the name of this node.
        """
        return f"{self.__class__.__name__}({self.fullname})"


class Package(Node):
    """A package is a collection of modules and other packages.
    
    Packages are named and provide a hierarchical name space for modules.

    One could liken a package to a Java package and a module to a Java class.

    A package is installed if all its modules are installed and all its sub-packages (name-wise) are 
    installed. Packages can be considered as requirements for modules.

    In fact, modules are a special kind of a package, which can have sub-modules but not sub-packages.
    """
    def __init__(self, name, parent=None):
        super().__init__(name, parent)

    def modules(self):
        """Get the modules in this package.

        The method returns an iterable of all the modules in this package, including sub-modules.
        """
        for child in self.children.values():
            if isinstance(child, Module):
                yield child
            elif isinstance(child, Package):
                yield from child.modules()
            else:
                raise ValueError(f"Child {child.name} is not a module or a package")

    def all_modules(self):
        for child in self.children.values():
            if isinstance(child, Module):
                yield child
                yield from child.all_submodules()
            elif isinstance(child, Package):
                yield from child.all_modules()
            else:
                raise ValueError(f"Child {child.name} is not a module or a package")


class Module(Node):
    """
    A class to represent a module of KLMS resources.

    A module is a collection of KLMS resources (datasets, files, buckets, setting, etc).

    Modules are modelled after SQL entities: They support the CREATE and DROP operations, and
    these operations can be qualified by existence (CREATE IF NOT EXISTS, DROP IF EXISTS).
    A module that actually exists on a KLMS is INSTALLED, and a module that does not exist
    on a KLMS is UNINSTALLED. After creation a module is always in the INSTALLED state.
    
    Modules are hierarchical: A module can contain other modules, and these modules can
    contain other modules, and so on. This allows for a tree-like structure of modules.
    
    Also, modules can have dependencies on other modules called requirements, i.e., to create
    a module, its requirements must be already installed. A module whose requirements are
    installed is ENABLED, else it is disabled.

    Sub-modules are modules that are contained in a module. Each top-level module is
    considered installed if all its sub-modules are installed.
    Also, if a sub-module is installed, its parent module is also either installed, or in
    the process of being installed (see goals below).

    Each module on a KLMS has a __goal__ installation state, which may be (temporarily)
    different from its actual state. The goal state is the state that the module should
    be in after all operations to install it are completed (installing requirements, creating the
    resources of the module, etc).

    Goal states are achieved by running the __reconciliation__ process on a KLMS. The reconciliation
    process plans the operations to be performed on the KLMS to achieve the goal state of all
    modules on the KLMS. The reconciliation process should be run a module's goal state changes.

    A module can be in one of the following states:
    - INSTALLED: The module is installed on the KLMS.
    - UNINSTALLED: The module is not installed on the KLMS.
    - ENABLED: The module is enabled on the KLMS, i.e., its requirements are installed.
    - DISABLED: The module is disabled on the KLMS, i.e., its requirements are not installed.
    """

    def __init__(self, name, parent=None, *, spec={}):
        super().__init__(name, parent)
        self.spec = spec
        self.required = set()
        self.enabled = set()
        self._installed = None

    def add(self, child):
        """Add a child node to this node.
        Args:
            child (Node): The child node to add.
        """
        if not isinstance(child, Module):
            raise ValueError(f"Adding {child.name} to {self.fullname}: children of a module must be modules")
        super().add(child)

    def require(self, req):
        """Add a requirement to this module.

        Args:
            module (Module): The module to require.
        """
        if isinstance(req, list | set):
            for r in req:
                self.require(r)
            return
        
        if isinstance(req, str):
            req = self.catalog.get(req)
        if req is None:
            raise ValueError(f"Adding {req} to {self.fullname}: requirement {req} not found")
        if not isinstance(req, Node):
            raise ValueError(f"Adding {req} to {self.fullname}: requirement must be a module or a package")
        
        if isinstance(req, Package):
            for m in req.modules():
                self.required.add(m)
                m.enabled.add(self)
        else:
            assert isinstance(req, Module)
            self.required.add(req)
            req.enabled.add(self)

    @property
    def is_submodule(self):
        """Check if this module is a sub-module of another module.
        """

        return isinstance(self.parent, Module)

    @property
    def top_module(self):
        """Get the top-level module of this module.

        A top-level module is a module that has no parent.
        """
        return self.parent.top_module if self.is_submodule else self

    def submodules(self):
        """Get the sub-modules of this module.

        The method returns an iterable of all the sub-modules of this module.
        """
        for child in self.children.values():
            if isinstance(child, Module):
                yield child
            else:
                raise ValueError(f"Child {child.name} is not a module")

    def all_submodules(self):
        """Get all the submodules of this module.
        
        Submodules of submodules will be returned.
        """
        for child in self.children.values():
            yield child
            yield from child.all_submodules()

    def check_installed(self) -> bool:
        """Check if this module is installed.

        The method returns True if this module is installed, False otherwise.
        """
        raise NotImplementedError("is_installed() not implemented in Module class")
    
    @property
    def installed(self):
        """Check if this module is installed.

        The method returns True if this module is installed, False otherwise.
        """
        if self._installed is None:
            self._installed = self.check_installed()
        return self._installed

    @installed.setter
    def installed(self, value):
        """Set the installed state of this module.

        The method sets the installed state of this module to the given value.
        """
        if not isinstance(value, bool | None):
            raise ValueError(f"Installed state must be a boolean, got {value}")
        self._installed = value

    def _label(self):
        clsname = self.__class__.__name__
        if clsname.endswith("Module"):
            clsname = clsname[:-6]
        return f"{clsname:<12} {self.fullname:<32}"

    def do_install(self):
        self.pre_install()
        if not self.installed:
            print("Install", self._label(), ": installing")
            self.install()
        else:
            print("Install", self._label(), ": unchanged")
        self.post_install()

    def pre_install(self):
        """Called before install.

           Subclasses can add functionality here.
        """
    
    def post_install(self):
        """Called before install.

           Subclasses can add functionality here.
        """
        pass

    def do_uninstall(self):
        self.pre_uninstall()
        if self.installed:
            print("Uninstall", self._label(), ": uninstalling")
            self.uninstall()
        else:
            print("Uninstall", self._label(), ": unchanged")
        self.post_uninstall()

    def pre_uninstall(self):
        pass

    def post_uninstall(self):
        pass

    def install(self):
        """Install this module.

        The method installs this module on the KLMS.
        """
        raise NotImplementedError("install() not implemented in Module class")
    
    def uninstall(self):
        """Uninstall this module.

        The method uninstalls this module from the KLMS.
        """
        raise NotImplementedError("uninstall() not implemented in Module class")
    


