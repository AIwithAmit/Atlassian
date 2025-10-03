"""
Clarification questions:
1. file id, size_bytes, collection_id or list of collection id

2. each file contribute size_bytes to each collection it belongs to

3. whats input type, in records what tye of collection is it a single string
list or what

"""

# base solution single collection per file
from collections import Counter
import collections

Record = tuple[str, int, str]

def generate_report_of_collections(records: list[Record], top_n: int = 10):
    total_size = 0
    coll_total = Counter()
    for id, size, coll in records:
        total_size += size
        coll_total[coll] += size
    
    top_n_list = coll_total.most_common(top_n)
    return total_size, coll_total, top_n_list

# Example:
records = [
    ("f1", 100, "c1"),
    ("f2", 200, "c1"),
    ("f3", 300, "c2"),
    ("f4", 50,  "c3"),
]
print(generate_report_of_collections(records, top_n=2))


# each file can have multiple collection
from collections import Counter

Record = tuple[str, int, str | list[str]]

def generate_report_of_collections(records: list[Record], top_n: int = 10):
    total_size = 0
    coll_total = Counter()
    for id, size, colls in records:
        total_size += size

        if isinstance(colls, str):
            colls = [colls]

        for coll in colls:
            coll_total[coll] += size
    
    top_n_list = coll_total.most_common(top_n)
    return total_size, coll_total, top_n_list

# Example:
records = [
    ("f1", 100, "c1"),
    ("f2", 200, ["c1", "c2"]),
    ("f3", 300, "c2"),
    ("f4", 50,  "c3"),
]
print(generate_report_of_collections(records, top_n=2))

# follow up: How would you handle this in a multithreaded env
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
import math

Record = tuple[str, int, str | list[str]]

def _normalise_collections(colls):
    if isinstance(colls, str):
        yield colls
    elif colls is not None:
        for col in colls:
            yield col

def _process_chunk(records_chunk):
    partial_total = 0
    collections = Counter()
    for id, size, colls in records_chunk:
        partial_total += size
        for col in _normalise_collections(colls):
            collections[col] += size

    return partial_total, collections

def _chunkify(records, n_chunks)->list[list[Record]]:
    if n_chunks <= 1:
        return [records]
        
    chunk_size = math.ceil(len(records) / n_chunks)

    return [records[i:i + chunk_size] for i in range(0, len(records), chunk_size)]

def generate_report_of_collections_multithreaded(records: list[Record], top_n:int = 10, num_workers = None):

    num_workers = num_workers or min(32, max(1, len(records)))
    # no of chunks is no of worker becase we want 1 worker for each chunk
    record_chunks = _chunkify(records, num_workers)

    total_size = 0
    collections = Counter()
    with ThreadPoolExecutor(max_workers=num_workers) as ex:
        futures = [ex.submit(_process_chunk, record_chunk) for record_chunk in record_chunks]

        for ft in as_completed(futures):
            partial_total, colls = ft.result()
            total_size += partial_total
            collections.update(colls)
    
    top_n_list = collections.most_common(top_n)

    return total_size, collections, top_n_list

# Example:
records = [
    ("f1", 100, "c1"),
    ("f2", 200, ["c1", "c2"]),
    ("f3", 300, "c2"),
    ("f4", 50,  "c3"),
]
print(generate_report_of_collections_multithreaded(records, top_n=2))