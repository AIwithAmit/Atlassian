"""
clarification Questions :
1. start, endtime, can i assume at entime other booking can start, its
open [start, endtime)

2. endtime >= starttime

3. unlimited courts available but we must minimize the no of courts

4. return list of assignment list, i will return a list of tuple

(booking id , court id)

"""

from dataclasses import dataclass
import heapq

@dataclass
class BookingRecord:
    Id:int
    Start_time:int
    Finish_time:int

def assignCourts(bookingRecords: list[BookingRecord]) -> list[tuple[int, int]]:

    if not bookingRecords:
        return []

    sorted_bookings = sorted(bookingRecords, key = lambda r : (r.Start_time, r.Finish_time))

    # min heap of (finish time, court id)
    heap : list[tuple[int, int]]= []
    next_court_id = 0

    assigment_by_id = {}

    for rec in sorted_bookings:
        if heap and heap[0][0] <= rec.Start_time:
            finishtime, court_id = heapq.heappop(heap)
        else :
            court_id = next_court_id
            next_court_id += 1
            
        assigment_by_id[rec.Id] = court_id
        heapq.heappush(heap, (rec.Finish_time, court_id))
    
    result = [(rec.Id, assigment_by_id[rec.Id]) for rec in bookingRecords]


    return result

# Small helper to print a summary
def print_assignments(assignments: list[tuple[int,int]]):
    print("BookingId -> CourtId")
    for b, c in assignments:
        print(f"{b} -> {c}")

if __name__ == "__main__":
    bookings = [
        BookingRecord(1, 1, 4),
        BookingRecord(2, 2, 5),
        BookingRecord(3, 3, 6),
        BookingRecord(4, 4, 7),
        BookingRecord(5, 8, 9),
        BookingRecord(6, 5, 8),
    ]
    assignments = assignCourts(bookings)
    print_assignments(assignments)
    # One possible output (court numbering may vary but number of courts is minimal):
    # 1 -> 0
    # 2 -> 1
    # 3 -> 2
    # 4 -> 0   
    # 5 -> 2  
    # 6 -> 1 



# follow up : B b) After each booking, a fixed amount of time, X, is needed to maintain the court before it can be rented again
def assignCourts(bookingRecords: list[BookingRecord], maintance_time = 0) -> list[tuple[int, int]]:

    if not bookingRecords:
        return []

    sorted_bookings = sorted(bookingRecords, key = lambda r : (r.Start_time, r.Finish_time))

    # min heap of (finish time, court id)
    heap : list[tuple[int, int]]= []
    next_court_id = 0

    assigment_by_id = {}

    for rec in sorted_bookings:
        if heap and heap[0][0] <= rec.Start_time:
            _, court_id = heapq.heappop(heap)
        else :
            court_id = next_court_id
            next_court_id += 1

        assigment_by_id[rec.Id] = court_id
        heapq.heappush(heap, (rec.Finish_time + maintance_time, court_id))
    
    result = [(rec.Id, assigment_by_id[rec.Id]) for rec in bookingRecords]


    return result


"""
c) Court only need maintainenece after X amount of usage
How would you modify the code if each court also had a Y maintainence time that occurred after X bookings?
The function should now become something like
Def assign_court_with_maintainence(booking_records: list{BookingRecord],

Maintainence_time: int,

Durability: int) -> list[Court]:
"""

def assignCourts(bookingRecords: list[BookingRecord], durability = 0, maintance_time = 0) -> list[tuple[int, int]]:

    if not bookingRecords:
        return []

    sorted_bookings = sorted(bookingRecords, key = lambda r : (r.Start_time, r.Finish_time))

    # min heap of (finish time, court id)
    heap : list[tuple[int, int, int]]= []
    next_court_id = 0

    assigment_by_id = {}

    for rec in sorted_bookings:
        if heap and heap[0][0] <= rec.Start_time:
            _, court_id, usage_count = heapq.heappop(heap)
        else :
            court_id = next_court_id
            next_court_id += 1
            usage_count = 0

        assigment_by_id[rec.Id] = court_id
        usage_count += 1

        if usage_count >= durability :
            next_free_time = rec.Finish_time + maintance_time
            usage_count = 0
        else:
            next_free_time = rec.Finish_time

        heapq.heappush(heap, (next_free_time, court_id, usage_count))
    
    result = [(rec.Id, assigment_by_id[rec.Id]) for rec in bookingRecords]


    return result

#d)The original problem can be made simpler by removing the “assigning each booking to a specific court” part. The candidate needs to find the minimum number of courts needed to accommodate all the bookings
from dataclasses import dataclass
from typing import List

@dataclass(frozen=True)
class BookingRecord:
    Id: int
    Start_time: int
    Finish_time: int

def min_courts_needed(bookings: List[BookingRecord]) -> int:
    """
    Return the minimum number of courts required to accommodate all bookings.
    Assumes intervals are [Start_time, Finish_time) (start inclusive, finish exclusive),
    so a booking that starts at t can use a court that finished at t.
    """
    if not bookings:
        return 0

    starts = sorted(b.Start_time for b in bookings)
    ends   = sorted(b.Finish_time for b in bookings)

    s_ptr = 0
    e_ptr = 0
    used = 0
    max_used = 0
    n = len(bookings)

    while s_ptr < n:
        # If next booking starts before the earliest finishing booking ends,
        # we need an extra court.
        if starts[s_ptr] < ends[e_ptr]:
            used += 1
            max_used = max(max_used, used)
            s_ptr += 1
        else:
            # A court freed (ends[e_ptr] <= starts[s_ptr]) -> reuse it
            used -= 1
            e_ptr += 1

    return max_used

#e) Check if booking conflict - Write a function that if given two bookings to check if they conflict with each other
def bookings_conflict(b1: BookingRecord, b2: BookingRecord) -> bool:
    """
    Return True if bookings b1 and b2 conflict (time overlap).
    Assumes intervals are [Start_time, Finish_time) (start inclusive, finish exclusive).
    """
    return b1.Start_time < b2.Finish_time and b2.Start_time < b1.Finish_time