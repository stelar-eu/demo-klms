from __future__ import annotations
from collections import deque
from typing import Callable
from .base import Module, Package, Catalog, Node


class Goal:
    """A goal is a desired state of a KLMS.

    A goal is achieved by running the reconciliation process on the KLMS.

    Formally, a goal object is associated with a catalog object. For each module in the
    catalog, the goal object returns True if the module is to be installed, False if the module is to be uninstalled, 
    and None if we don't care.
    """
    def __init__(self, catalog: Catalog):
        self.catalog = catalog
        self._goal = {}

    def _modset(self, req):
        """Get the set of modules in this goal.

        The method returns a set of all the modules in this goal.
        """
        if isinstance(req, str):
            req = self.catalog.get(req)
        if isinstance(req, list | set):
            flatreq = []
            for r in req:
                flatreq.extend(self._modset(r))
            return flatreq

        if not isinstance(req, Node):
            raise ValueError(f"Adding {req} to {self.fullname}: requirement must be a module or a package")
        
        if isinstance(req, Package):
            return req.modules()
        else:
            assert isinstance(req, Module)
            return [req]

    def set_goal(self, req, g, force=False):
        assert g in (True, False)
        newinstalls = []

        for m in self._modset(req):
            if m.fullname in self._goal and self._goal[m.fullname] is not g:
                if not force:
                    raise ValueError(f"Module {m.fullname} already in goal to uninstall, use force=True to override")
            else:
                newinstalls.append(m)

        for m in newinstalls:
            self._goal[m.fullname] = g

    def install(self, req, force=False):
        """Set the goal of this module to install.

        The method sets the goal of this module to install.
        """
        self.set_goal(req, True)

    def uninstall(self, req, force=False):
        """Set the goal of this module to uninstall.

        The method sets the goal of this module to uninstall.
        """
        self.set_goal(req, False)

    def __or__(self, other):
        """Combine two goals.

        The method combines two goals by taking the union of their goals.
        """
        if not isinstance(other, Goal):
            raise ValueError(f"Cannot combine {self.__class__.__name__} with a goal")
        if other.catalog != self.catalog:
            raise ValueError(f"Cannot combine {self.__class__.__name__} with a goal from another catalog")
        newgoal = Goal(self.catalog)
        newgoal._goal = self._goal.copy()

        conflicts = []
        for k, v in other._goal.items():
            if k in newgoal._goal:
                if newgoal._goal[k] != v:
                    conflicts.append(k)
            else:
                newgoal._goal[k] = v
        if len(conflicts) > 0:
            raise ValueError("Conflicting goals for modules", conflicts)
        return newgoal

    def logical_plan(self) -> tuple[list[Module], list[Module]]:
        """Returns a tuple of two lists of modules.

        The first list is the list of modules to be installed, and the second list is the list of modules to be uninstalled.
        The modules are sorted in the order of their strongly connected index (SCI). Therefore, these lists
        can be used to install and uninstall the modules in the correct order.
        """

        # the set of modules in the final state that need to be installed
        I = set(self.catalog.get(m) for m, v in self._goal.items() if v)

        # the set of modules in the final state that need to be uninstalled
        U = set(self.catalog.get(m) for m, v in self._goal.items() if not v)

        
        # Augment goal to maintain module atomicity
        I = add_all_modules(I)
        U = add_all_modules(U)


        # Augment goal to maintain the requirement invariant
        I = transitive_closure(I, lambda m: m.required)
        U = transitive_closure(U, lambda m: m.enabled)

        C = I & U
        
        if len(C) > 0:
            raise ValueError("Conflict", C)

        # compute the SCI for all modules
        self.catalog.strongly_connected_index()

        Ilist = list(I)
        Ilist.sort(key=lambda m: m.scc_index)
        Ulist = list(U)
        Ulist.sort(key=lambda m: m.scc_index, reverse=True)
        # the set of modules in the final state that need to be installed
        return (Ilist, Ulist)

    def reconcile(self):
        """Reconcile the goal of this module.

        The method reconciles the goal of this module by running the reconciliation process on the KLMS.
        """

        Ilist, Ulist = self.logical_plan()

        for m in Ilist:
            m.do_install()
        for m in Ulist:
            m.do_uninstall()


def add_all_modules(S: set[Module]) -> set[Module]:
    """Return a superset of a set of modules, expanding all top module groups.

    Two Module objects are peers if they have the same top module.
    The returned set is a superset of S which is closed under the 'peer' relation.
    """
    tops = {m.top_module for m in S}
    Sx = set(tops)
    for top in tops:
        peers = set(top.all_submodules())
        Sx |= peers
    return Sx


def transitive_closure(S: set[Module], f: Callable[Module, set[Module]]) -> set[Module]:
    """Compute the transitive closure of a set of modules.

    The method computes the transitive closure of a set of modules by applying the given function to each module in the set.
    The function is applied to each module in the set until no new modules are added to the set.
    """
    Q = deque(S)
    while Q:
        m = Q.popleft()
        for n in f(m):
            if n not in S:
                S.add(n)
                Q.append(n)
    return S


