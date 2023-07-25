"""
Very simple stress test to make sure that the proxy can handle
lots of requests without being too slow for the users via the
browser.

Increase the number of pods on the proxy by right-clicking
it under Developer --> Topology and then "Edit Pod count".

On PaaS, you can monitor performance by going to

Developer --> Observe

and change Time Range to 5 minutes and Refresh Interval to 15 seconds.

This test is not intended to be run by pytest, just during development.
"""

import concurrent.futures
import runregistry

runregistry.setup("development")

NUM_THREADS = 10
NUM_JOBS = 5000


def fetch_run_data():
    a = runregistry.get_run(355555)


if __name__ == "__main__":
    # Run the same request up to a total of NUM_JOBS times,
    # using a ThreadPoolExecutor to do the requests concurrently.
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=NUM_THREADS)
    for i in range(NUM_JOBS):
        executor.submit(fetch_run_data)
