"""
clarifying question:
0 Are you looking for continous output or we are processing all the ballots
after votings.

1 what is input type

2 what strategy when there is tie, you can recommend 2 strategy

3 for first time winner, do we consider this as per ballot or per per_point_step

4 can we have dulicated in a ballot like ["A", "A", "B"]
"""

from collections import defaultdict
from enum import CONTINUOUS

POSITION_POINT = [3, 2, 1]


def getResults(ballots : list[list[str]], strategy : int = 1, per_point_step: bool = True)->list[str]:
    
    if not ballots:
        return []

    totalpoints: dict[str, int] = defaultdict(int)
    pos_counts: dict[str, list[int]] = defaultdict(lambda:[0, 0, 0])
    last_update_step : dict[str, int] = defaultdict(int)
    
    candidates = set()
    step = 0

    for ballot in ballots:
        seen = set()  # guard against duplicate names in the same ballot
        for pos, cand in enumerate(ballot[:3]):
            if cand in seen:
                continue
            seen.add(cand)

            pts = POSITION_POINT[pos]
            totalpoints[cand] += pts
            pos_counts[cand][pos] += 1
            candidates.add(cand)

            if per_point_step: # per point step
                step += 1
                last_update_step[cand] = step
        
        if not per_point_step: # per ballot step
            step += 1
            for cand in seen: # if no duplicate then for cand in ballot[:3]
                last_update_step[cand] = step
    
    def key_strategy1(c: str):
        return (-totalpoints[c], last_update_step[c], c)

    def key_strategy2(c: str):
        return (-totalpoints[c], -pos_counts[c][0], -pos_counts[c][1], -pos_counts[c][2], c)
    
    if strategy == 1:
        sorted_list = sorted(candidates, key = key_strategy1)
    elif strategy == 2:
        sorted_list = sorted(candidates, key = key_strategy2)
    else:
        raise ValueError("strategy must be 1 or 2")
    
    return sorted_list

if __name__ == "__main__":
    ballots_example = [
        ["A","B","C"],
        ["B","C","A"],
        ["C","A","B"]
    ]
    print("Strategy 1:", getResults(ballots_example, strategy=1))
    print("Strategy 2:", getResults(ballots_example, strategy=2))

    ballots2 = [
        ["A","B"],   # A+3, B+2
        ["B","A"],   # B+3, A+2  -> both 5
        ["C"]        # C+3
    ]
    print("ballots2 Strategy 1:", getResults(ballots2, strategy=1))
    print("ballots2 Strategy 2:", getResults(ballots2, strategy=2))
    
"""
B, C

time : B*3 + ClogC = B + ClogC

space : O(C)
"""

#leetcode one 

class Solution:
    def rankTeams(self, votes: List[str]) -> str:

        if not votes:
           return ""  # no votes -> no teams

        # number of positions (equals number of teams)
        m = len(votes[0])

        # d maps team_char -> list of counts per position
        # d['A'][0] = number of first-place votes for team 'A'
        d = {}

        # Build the counts
        for vote in votes:
            # assume each vote ranks all teams and has length m
            for pos, team in enumerate(vote):
                if team not in d:
                    # initialize a zero-count list of length m
                    d[team] = [0] * m
                d[team][pos] += 1

        # Get the team names sorted alphabetically first.
        # This ensures alphabetical order is used as the final tie-breaker,
        # because Python's sort is stable.
        teams = sorted(d.keys())

        # Now sort teams by their counts list in descending order.
        # - key=lambda t: d[t] uses the counts list as the sort-key
        # - lists are compared lexicographically in Python (position 0 first, then 1, ...)
        # - reverse=True makes higher counts come first
        ranked = sorted(teams, key=lambda t: d[t], reverse=True)

        # Join into a single string result
        return "".join(ranked)






#for startegy 1 CONTINUOUS

from collections import OrderedDict
from typing import Optional, List


POSITION_POINT = [3, 2, 1]  # points for pos 0,1,2


class BucketNode:
    """Doubly-linked node that holds all candidates with the same score.
    candidates OrderedDict preserves arrival order (earliest first)."""
    def __init__(self, score: int):
        self.score = score
        self.candidates = OrderedDict()
        self.prev = None
        self.next = None


class ContinuousVotingSystem:
    """Maintain running scores and arrival-order tie-break using buckets of equal score."""

    def __init__(self):
        # candidate -> score
        self.candidate_map = {}
        # score -> BucketNode
        self.bucket_map = {}
        # DLL of buckets sorted by increasing score
        self.head = None
        self.tail = None

    # ---- bucket helpers ----
    def _link_as_head(self, node: BucketNode) -> None:
        node.next = self.head
        node.prev = None
        if self.head:
            self.head.prev = node
        self.head = node
        if self.tail is None:
            self.tail = node

    def _link_after(self, node, prev) -> None:
        node.prev = prev
        node.next = prev.next
        prev.next = node
        if node.next:
            node.next.prev = node
        else:
            self.tail = node

    def _unlink_and_remove(self, bucket) -> None:
        if bucket.prev:
            bucket.prev.next = bucket.next
        else:
            self.head = bucket.next
        if bucket.next:
            bucket.next.prev = bucket.prev
        else:
            self.tail = bucket.prev
        del self.bucket_map[bucket.score]

    def _create_bucket_for_score(self, score: int, anchor: Optional[BucketNode]) -> BucketNode:
        """Create and insert a new bucket for `score`.
        Prefer inserting near `anchor` when provided to keep locality."""
        node = BucketNode(score)
        self.bucket_map[score] = node

        if self.head is None:
            # empty list
            self._link_as_head(node)
            return node

        # If anchor given, use its position to decide insertion side.
        if anchor is not None:
            if anchor.score <= score:
                # insert after anchor (or at tail)
                if anchor is self.tail:
                    self._link_after(node, anchor)
                else:
                    self._link_after(node, anchor)
                return node
            else:
                # anchor.score > score: insert before anchor (walk backwards if needed)
                prev = anchor.prev
                if prev is None:
                    # becomes new head
                    self._link_as_head(node)
                else:
                    self._link_after(node, prev)
                return node

        # No anchor: fast checks against head/tail
        if score >= self.tail.score:
            self._link_after(node, self.tail)
            return node
        if score <= self.head.score:
            self._link_as_head(node)
            return node

        # Fallback: scan from head to find insertion point (rare)
        cur = self.head
        while cur and cur.score < score:
            cur = cur.next
        # insert before cur (cur is not None here)
        if cur is None:
            # shouldn't happen because we handled tail case
            self._link_after(node, self.tail)
        else:
            prev = cur.prev
            if prev is None:
                self._link_as_head(node)
            else:
                self._link_after(node, prev)
        return node

    def _remove_from_bucket(self, cand: str, old_score: int) -> Optional[BucketNode]:
        """Remove candidate from its old bucket.
        Return anchor bucket to use when inserting a new bucket:
        - if old bucket remains non-empty: return that bucket
        - if old bucket emptied & removed: return old_bucket.prev
        - if no old bucket existed: return None
        """
        old_bucket = self.bucket_map.get(old_score)
        if old_bucket is None:
            return None

        if cand in old_bucket.candidates:
            del old_bucket.candidates[cand]

        if old_bucket.candidates:
            return old_bucket
        # emptied -> remove and return prev as anchor
        prev_bucket = old_bucket.prev
        self._unlink_and_remove(old_bucket)
        return prev_bucket

    # ---- core operations ----
    def add_points(self, cand: str, pts: int) -> None:
        """Add pts to candidate cand. Maintains bucket structure and arrival order."""
        old_score = self.candidate_map.get(cand, 0)
        anchor = self._remove_from_bucket(cand, old_score)
        new_score = old_score + pts

        new_bucket = self.bucket_map.get(new_score)
        if new_bucket is None:
            new_bucket = self._create_bucket_for_score(new_score, anchor)

        # append candidate preserving arrival order
        new_bucket.candidates[cand] = None
        self.candidate_map[cand] = new_score

    def current_winner(self) -> Optional[str]:
        """Return current leader: highest score and earliest arrival in that bucket."""
        if not self.tail or not self.tail.candidates:
            return None
        return next(iter(self.tail.candidates))

    def process_ballot(self, ballot: List[str]) -> None:
        """Process a ballot (top 3 positions -> 3,2,1 points)."""
        for pos, cand in enumerate(ballot[:3]):
            self.add_points(cand, POSITION_POINT[pos])

    def get_ranking(self) -> List[str]:
        """Return full ranking: highest score -> lowest; within same score follow arrival order."""
        result: List[str] = []
        cur = self.tail
        while cur:
            result.extend(list(cur.candidates.keys()))
            cur = cur.prev
        return result


if __name__ == "__main__":
    system = ContinuousVotingSystem()

    ballots = [
        ["A", "B"],   # A+3, B+2
        ["B", "A"],   # B+3, A+2
        ["C"]         # C+3
    ]

    print("Processing per-point (fine-grained):")
    for ballot in ballots:
        for pos, cand in enumerate(ballot[:3]):
            system.add_points(cand, POSITION_POINT[pos])
            print(f" After {cand}+{POSITION_POINT[pos]} -> winner: {system.current_winner()}")

    print("\nFinal ranking:", system.get_ranking())

    system2 = ContinuousVotingSystem()
    print("\nProcessing per-ballot (coarse-grained demo):")
    for ballot in ballots:
        system2.process_ballot(ballot)
        print(f" After ballot {ballot} -> winner: {system2.current_winner()}")

    print("\nFinal ranking (system2):", system2.get_ranking())
