"""
Find the closest Org for target Employees
a) Imagine you are the team that maintains the Atlassian employee directory. At Atlassian – there are multiple groups, and each can have one or more groups. Every employee is part of a group. You are tasked with designing a system that could find the closest common parent group giv a target set of employees in the organization.
"""
from collections import defaultdict, deque
from unittest import TestCase

"""
          CEO 

    eng        ops

ML     sde       support

parent group {"CEO": None,
"Eng" : "CEO"
}

employees = {
"Alice" : "eng"
}
"""
class orgLCA:
    def __init__(
        self, 
        group_parents,
        employee_group
        ) -> None:
        self.group_parents = group_parents
        self.employee_group = employee_group
        self.cache = {}
        self.preprocess()
    
    def preprocess(self):
        # extract root
        roots = [g for g, p in self.group_parents.items() if p is None]

        if len(roots) != 1:
            raise ValueError("orgs must have one parent")

        self.root:str = roots[0]

        #build childrens and compute depths
        self.children = defaultdict(list)

        for g, p in self.group_parents.items():
            if p:
                self.children[p].append(g)
        
        self.depths = {}
        q = deque()
        dist = 0
        q.append(self.root)
        self.depths[self.root] = dist

        while q:
            size = len(q)
            while size:
                group = q.popleft()
                for child in self.children[group]:
                    self.depths[child] = dist+1
                    q.append(child) 
                size -= 1
            dist += 1

    def find_lca(self, groups):
        if len(groups) == 1:
            return groups[0]
        
        def lca(a, b):
            key = tuple(sorted((a, b))) # a b and b a has same thing

            if key in self.cache:
                return self.cache[key]

            #ensure a is depper
            if self.depths[a] < self.depths[b]:
                a, b = b, a
            
            while self.depths[a] > self.depths[b]:
                a = self.group_parents[a]
            
            #lift together
            while a != b:
                a = self.group_parents[a]
                b = self.group_parents[b]
            
            self.cache[key] = a
            
            return a
        
        # we will find lca of oth and 1st then from of 
        #lca of this lca and next group in group list and so on
        common = groups[0]

        for g in groups[1:]:
            common = lca(common, g)
        
        return common
    
    def get_common_group_for_employees(self, employees):
        groups = list(set(self.employee_group[emp] for emp in employees))

        return self.find_lca(groups)

class TestOrgLCA(TestCase):
    def setUp(self):
        group_parents = {
            "CEO": None,
            "Eng": "CEO", 
            "Sales": "CEO",
            "FE": "Eng", 
            "BE": "Eng",
            "Intern": "FE",
            "EU": "Sales", 
            "US": "Sales"
        }
        employee_group = {
            "alice": "FE",
            "bob": "BE",
            "carol": "Sales",
            "dave": "Intern",
            "erin": "EU",
            "frank": "US"
        }
        self.lca = orgLCA(group_parents, employee_group)

    def test_single_employee(self):
        self.assertEqual(self.lca.get_common_group_for_employees(["alice"]), "FE")
        self.assertEqual(self.lca.get_common_group_for_employees(["dave"]), "Intern")

    def test_siblings_in_same_team(self):
        # alice(FE) + bob(BE) → Eng
        self.assertEqual(self.lca.get_common_group_for_employees(["alice", "bob"]), "Eng")

    def test_employee_and_manager(self):
        # alice(FE) + dave(Intern) → FE
        self.assertEqual(self.lca.get_common_group_for_employees(["alice", "dave"]), "FE")

    def test_cross_departments(self):
        # alice(FE) + carol(Sales) → CEO
        self.assertEqual(self.lca.get_common_group_for_employees(["alice", "carol"]), "CEO")

    def test_same_department_diff_teams(self):
        # erin(EU) + frank(US) → Sales
        self.assertEqual(self.lca.get_common_group_for_employees(["erin", "frank"]), "Sales")

    def test_multiple_employees(self):
        # alice(FE), bob(BE), dave(Intern) → Eng
        self.assertEqual(self.lca.get_common_group_for_employees(["alice", "bob", "dave"]), "Eng")
        # alice(FE), erin(EU), frank(US) → CEO
        self.assertEqual(self.lca.get_common_group_for_employees(["alice", "erin", "frank"]), "CEO")

if __name__ == "__main__":
    import unittest
    unittest.main()


"""
b) The Atlassian hierarchy sometimes can have shared group across an org or employees shared across different groups – How will the code evolve n this case if the requirement is to provide ONE closest common group
c) The system now introduced 4 methods to update the structure of the hierarchy in the org. Supose these dynamic updates are done in separate threads while getCommonGroupForEmployees is being called, How ill your system handled reads and writes into the system efficiently such that at any given time getCommonGroupForEmployees always reflects the latest updated state of the hierarchy?
"""

from collections import deque, defaultdict
from readerwriterlock import rwlock  # pip install readerwriterlock [1][2]
import unittest


class DAGOrg:
    def __init__(self, group_parents, employee_groups) -> None:
        # Use a fair readers–writer lock to allow many concurrent reads and serialize writes. [1][2]
        self._rw = rwlock.RWLockFair()

        # Authoritative mutable sources (only touched under write lock). [1]
        self._group_parents_mut: dict[str, list[str]] = {}
        self._employee_groups_mut: dict[str, list[str]] = {}

        # Normalize inputs into mutable sources (same behavior as before). [1]
        all_groups = set(group_parents.keys())
        for parents in group_parents.values():
            for p in parents:
                all_groups.add(p)
        for g in all_groups:
            self._group_parents_mut[g] = list(group_parents.get(g, []))

        for emp, gs in employee_groups.items():
            if isinstance(gs, str):
                self._employee_groups_mut[emp] = [gs]
            else:
                self._employee_groups_mut[emp] = list(gs)

        # Build derived snapshot once during init (single-threaded). [1]
        self._rebuild_snapshot_unlocked()

    # ----- Snapshot rebuild (derived data); callers hold write lock except during __init__ -----
    def _rebuild_snapshot_unlocked(self) -> None:
        # Build parents/children for upward traversals. [1]
        self.parents: dict[str, list[str]] = {g: list(self._group_parents_mut[g]) for g in self._group_parents_mut}
        self.children: dict[str, list[str]] = {g: [] for g in self._group_parents_mut}
        for g, ps in self.parents.items():
            for p in ps:
                if p not in self.children:
                    self.children[p] = []
                self.children[p].append(g)
        # Compute depths via Kahn’s algorithm (raises on cycle, preserving DAG invariant). [1]
        self.depth: dict[str, int] = self._compute_depths()
        # Freeze employee groups view to avoid accidental mutation during reads. [1]
        self.employee_groups_view: dict[str, tuple[str, ...]] = {
            emp: tuple(gs) for emp, gs in self._employee_groups_mut.items()
        }

    def _compute_depths(self) -> dict[str, int]:
        indeg = {g: len(self.parents[g]) for g in self.parents}
        q = deque(g for g, d in indeg.items() if d == 0)
        topo: list[str] = []
        while q:
            u = q.popleft()
            topo.append(u)
            for v in self.children.get(u, []):
                indeg[v] -= 1
                if indeg[v] == 0:
                    q.append(v)
        if len(topo) != len(self.parents):
            raise ValueError("Cycle detected in group graph; expected a DAG")
        depth = {g: 0 for g in self.parents}
        for u in topo:
            du = depth[u]
            for v in self.children.get(u, []):
                if depth[v] < du + 1:
                    depth[v] = du + 1
        return depth

    # ----- Read API: take a read lock briefly, then operate on locals -----
    def closest_common_group_for_employee_groups(self, list_of_group_sets: list[list[str]]) -> str | None:
        # Acquire read lock to take a consistent snapshot pointer (parents/depth). [1][2]
        with self._rw.gen_rlock():
            parents = self.parents
            depth = self.depth
        # Work on local references after lock release to minimize contention. [1]
        K = len(list_of_group_sets)
        if K == 0:
            return None
        normalized_sets: list[list[str]] = []
        for gs in list_of_group_sets:
            idxs: list[str] = []
            for g in gs:
                if g not in parents:
                    raise KeyError(f"Unknown group '{g}'")
                idxs.append(g)
            if not idxs:
                return None
            normalized_sets.append(idxs)
        visit_count: dict[str, int] = defaultdict(int)
        seen_mark: dict[str, int] = {}
        mark = 1
        for starts in normalized_sets:
            q = deque()
            for g in starts:
                if seen_mark.get(g) != mark:
                    seen_mark[g] = mark
                    visit_count[g] += 1
                    q.append(g)
            while q:
                u = q.popleft()
                for p in parents.get(u, []):
                    if seen_mark.get(p) != mark:
                        seen_mark[p] = mark
                        visit_count[p] += 1
                        q.append(p)
            mark += 1
        candidates = [g for g, cnt in visit_count.items() if cnt == K]
        if not candidates:
            return None
        best = max(candidates, key=lambda g: (depth.get(g, 0), g))
        return best

    def get_common_group_for_employees(self, employees: list[str]) -> str | None:
        # Acquire read lock to grab the current employee view atomically. [1][2]
        with self._rw.gen_rlock():
            emp_view = self.employee_groups_view
        list_of_group_sets: list[list[str]] = []
        for e in employees:
            if e not in emp_view:
                raise KeyError(f"Unknown employee '{e}'")
            list_of_group_sets.append(list(emp_view[e]))
        return self.closest_common_group_for_employee_groups(list_of_group_sets)

    # ----- Writer methods: mutate sources and rebuild under write lock -----
    def add_group(self, group: str, parents: list[str]) -> None:
        # Writers take exclusive lock, update sources, rebuild derived snapshot, and publish. [1][2]
        with self._rw.gen_wlock():
            self._group_parents_mut[group] = list(parents)
            for p in parents:
                self._group_parents_mut.setdefault(p, [])
            self._rebuild_snapshot_unlocked()

    def remove_group(self, group: str) -> None:
        with self._rw.gen_wlock():
            if group in self._group_parents_mut:
                del self._group_parents_mut[group]
            for g, ps in list(self._group_parents_mut.items()):
                self._group_parents_mut[g] = [p for p in ps if p != group]
            for emp, gs in list(self._employee_groups_mut.items()):
                self._employee_groups_mut[emp] = [g for g in gs if g != group]
            self._rebuild_snapshot_unlocked()

    def add_employee_groups(self, employee: str, groups: list[str]) -> None:
        with self._rw.gen_wlock():
            self._employee_groups_mut[employee] = list(groups)
            self._rebuild_snapshot_unlocked()

    def remove_employee(self, employee: str) -> None:
        with self._rw.gen_wlock():
            if employee in self._employee_groups_mut:
                del self._employee_groups_mut[employee]
            self._rebuild_snapshot_unlocked()


# ----------------- Unit tests / demo (unchanged behavior) -----------------
class TestDAGOrgClean(unittest.TestCase):
    def setUp(self):
        group_parents = {
            "Root": [],
            "A": ["Root"],
            "B": ["Root"],
            "C": ["A", "B"],
            "D": ["A"],
            "E": ["B"],
            "F": ["C", "D"],
        }
        employee_groups = {
            "alice": "D",
            "bob": "E",
            "carol": "C",
            "dave": ["F", "E"],
            "erin": "Root",
        }
        self.dag = DAGOrg(group_parents, employee_groups)

    def test_shared_parent(self):
        self.assertEqual(self.dag.get_common_group_for_employees(["alice", "carol"]), "A")

    def test_multi_group_employee(self):
        self.assertEqual(self.dag.get_common_group_for_employees(["dave", "carol"]), "C")

    def test_root_employee(self):
        self.assertEqual(self.dag.get_common_group_for_employees(["erin", "bob"]), "Root")

    def test_no_common(self):
        dag2_parents = {"X": [], "Y": ["X"], "Z": []}
        dag2_emps = {"u": ["Y"], "v": ["Z"]}
        dag2 = DAGOrg(dag2_parents, dag2_emps)
        self.assertIsNone(dag2.get_common_group_for_employees(["u", "v"]))

    def test_unknown_employee(self):
        with self.assertRaises(KeyError):
            self.dag.get_common_group_for_employees(["nobody"])


if __name__ == "__main__":
    unittest.main(argv=["first-arg-is-ignored"], exit=False, verbosity=2)


#d) The company consists of a single level of groups with no subgroups. Each group has a set of employees.

from collections import defaultdict
from readerwriterlock import rwlock  # or inline a tiny RWLock if deps not allowed. [15]
import unittest

class FlatOrg:
    """
    Single-level organization: groups have employees; no subgroups, no hierarchy.
    The common group for multiple employees is any group present in the intersection of their memberships. [3]
    Thread-safe with a readers–writer lock. [15]
    """
    def __init__(self, groups: dict[str, list[str]], employee_groups: dict[str, list[str]]):
        # Lock
        self._rw = rwlock.RWLockFair()
        # Canonical sets under write lock only
        self._groups: set[str] = set(groups.keys())
        self._employee_groups: dict[str, set[str]] = {}
        for emp, gs in employee_groups.items():
            gs_set = set(gs if not isinstance(gs, str) else [gs])
            # Validate that all memberships refer to known groups
            unknown = gs_set - self._groups
            if unknown:
                raise KeyError(f"Unknown group(s) in employee '{emp}': {sorted(unknown)}")
            self._employee_groups[emp] = gs_set

    # ----- Query: intersect memberships -----
    def get_common_group_for_employees(self, employees: list[str]) -> str | None:
        # Empty input => no shared group. [2]
        if not employees:
            return None  # [2]

        # Use reader lock for thread-safety on reads
        with self._rw.gen_rlock():
            # Seed the intersection with the first employee's groups. [1]
            first = employees[0]  # use the first element, not the whole list. [3]
            if first not in self._employee_groups:
                raise KeyError(f"Unknown employee '{first}'")  # [1]
            common = set(self._employee_groups[first])  # copy for in-place intersection. [1]

            # Intersect with remaining employees' groups. [1][2]
            for e in employees[1:]:
                if e not in self._employee_groups:
                    raise KeyError(f"Unknown employee '{e}'")  # [1]
                common &= self._employee_groups[e]  # set intersection. [1][2]
                if not common:
                    return None  # early exit if intersection empties. [2]

            # Deterministic result when multiple groups remain (lexicographically smallest). [1]
            return min(common) if common else None  # [1]


    # ----- Updates (examples) -----
    def add_group(self, group: str) -> None:
        with self._rw.gen_wlock():
            self._groups.add(group)

    def remove_group(self, group: str) -> None:
        with self._rw.gen_wlock():
            if group in self._groups:
                self._groups.remove(group)
            # Remove group from all employee memberships
            for e, gs in list(self._employee_groups.items()):
                if group in gs:
                    gs.remove(group)

    def add_employee_groups(self, employee: str, groups: list[str]) -> None:
        new_set = set(groups if not isinstance(groups, str) else [groups])
        with self._rw.gen_wlock():
            unknown = new_set - self._groups
            if unknown:
                raise KeyError(f"Unknown group(s): {sorted(unknown)}")
            self._employee_groups[employee] = new_set

    def remove_employee(self, employee: str) -> None:
        with self._rw.gen_wlock():
            self._employee_groups.pop(employee, None)

# ---------------- Tests ----------------
class TestFlatOrg(unittest.TestCase):
    def setUp(self):
        groups = {"Eng": [], "HR": [], "Ops": []}  # values unused in flat model
        employee_groups = {
            "alice": ["Eng", "Ops"],
            "bob": ["Eng"],
            "carol": ["HR", "Eng"],
            "dave": ["Ops"],
        }
        self.org = FlatOrg(groups, employee_groups)

    def test_common(self):
        # alice, bob, carol share Eng
        self.assertEqual(self.org.get_common_group_for_employees(["alice","bob","carol"]), "Eng")

    def test_none(self):
        # bob in Eng, dave in Ops -> no shared group
        self.assertIsNone(self.org.get_common_group_for_employees(["bob","dave"]))

    def test_single(self):
        self.assertEqual(self.org.get_common_group_for_employees(["bob"]), "Eng")

    def test_unknown_emp(self):
        with self.assertRaises(KeyError):
            self.org.get_common_group_for_employees(["nobody"])

if __name__ == "__main__":
    # For notebooks: pass argv override; remove argv/exit in scripts. [16]
    unittest.main(argv=["first-arg-is-ignored"], exit=False, verbosity=2)