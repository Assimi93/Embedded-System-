from itertools import permutations
from math import gcd
from functools import reduce

# =============================================================================
# 1) Define the 7 tasks: Each has { name, execution time (C), period/deadline (T) }
# =============================================================================
tasks = [
    {"name": "T1", "C": 2, "T": 10},
    {"name": "T2", "C": 3, "T": 10},
    {"name": "T3", "C": 2, "T": 20},
    {"name": "T4", "C": 2, "T": 20},
    {"name": "T5", "C": 2, "T": 40},
    {"name": "T6", "C": 2, "T": 40},
    {"name": "T7", "C": 3, "T": 80},
]

# =============================================================================
# 2) Compute the hyperperiod (LCM of all periods)
# =============================================================================
def lcm(a, b):
    """Compute the least common multiple of two integers a and b."""
    return abs(a * b) // gcd(a, b)

def calculate_hyperperiod(task_list):
    """Return the LCM of all periods in the given task set."""
    periods = [t["T"] for t in task_list]
    return reduce(lcm, periods)

hyper = calculate_hyperperiod(tasks)  # For T1..T7 above, this is LCM(10,10,20,20,40,40,80) = 80
print("Hyperperiod =", hyper)

# =============================================================================
# 3) Generate all jobs within [0, hyper)
#    Each task τ_i is repeated floor(hyper / T_i) times (which might be hyper/T_i if it divides exactly).
# =============================================================================
jobs = []
for task in tasks:
    task_name = task["name"]
    C = task["C"]
    T = task["T"]

    # How many times does this task repeat in the hyperperiod?
    count = hyper // T  # integer division
    for i in range(count):
        # Create job i+1 of this task
        job_id = f"{task_name}_{i+1}"  # e.g., "T1_1", "T1_2", ...
        arrival_time = i * T
        deadline_time = (i + 1) * T

        jobs.append({
            "job_id": job_id,
            "task_name": task_name,
            "C": C,
            "arrival": arrival_time,
            "deadline": deadline_time
        })

# Check how many jobs we have in total
print("Total number of jobs generated:", len(jobs))
for j in jobs:
    print(j)
print("-" * 60)

# =============================================================================
# 4) Define a function to check schedule feasibility and compute total waiting
#    We'll rename it to "check_schedule_feasibility" as requested.
# =============================================================================
def check_schedule_feasibility(job_sequence, allow_t5_miss=False):
    """
    Evaluates a permutation (job_sequence) to see if each job meets its deadline.
    If T5 is allowed to miss, then T5's jobs can be skipped if they would miss.

    :param job_sequence: a list of jobs in the order they are executed
    :param allow_t5_miss: if True, T5's jobs can exceed their deadline (they get skipped)
                          if False, all jobs must meet their deadline
    :return:
      - A dictionary {"total_waiting": X, "details": [...]} if feasible
      - None if infeasible
    """

    current_time = 0
    total_waiting = 0
    details = []

    for job in job_sequence:
        job_id = job["job_id"]
        task_name = job["task_name"]
        exec_time = job["C"]
        arrival_time = job["arrival"]
        deadline_time = job["deadline"]

        # If CPU is idle but the job hasn't arrived yet, jump to its arrival
        if current_time < arrival_time:
            current_time = arrival_time

        start_time = current_time
        finish_time = start_time + exec_time

        # Deadline check:
        if task_name == "T5" and allow_t5_miss:
            # If it's T5, we allow skipping if it misses
            if finish_time > deadline_time:
                # skip T5's job: do not add to waiting or push time forward
                continue
        else:
            # Must meet the deadline
            if finish_time > deadline_time:
                return None  # not feasible, deadline missed

        # Calculate waiting time: start_time - arrival_time
        waiting_time = start_time - arrival_time
        total_waiting += waiting_time

        # Record details
        details.append({
            "job_id": job_id,
            "task_name": task_name,
            "arrival": arrival_time,
            "deadline": deadline_time,
            "start": start_time,
            "finish": finish_time,
            "waiting": waiting_time
        })

        # Advance the current time
        current_time = finish_time

    # If we reach here, schedule was feasible
    return {
        "total_waiting": total_waiting,
        "details": details
    }

# =============================================================================
# 5) Brute-force check:
#    - Scenario A: T5 must meet its deadline
#    - Scenario B: T5 can miss its deadline
# =============================================================================
all_permutations = permutations(jobs)  # Potentially huge for many jobs!

best_strict = None      # Best schedule if T5 is NOT allowed to miss
best_t5_allowed = None  # Best schedule if T5 is allowed to miss

count_valid_strict = 0
count_valid_t5_allowed = 0

for perm in all_permutations:
    # Convert the tuple to a list
    schedule_list = list(perm)

    # Scenario A
    resA = check_schedule_feasibility(schedule_list, allow_t5_miss=False)
    if resA is not None:
        count_valid_strict += 1
        if (best_strict is None) or (resA["total_waiting"] < best_strict["total_waiting"]):
            best_strict = {
                "order": schedule_list,
                "total_waiting": resA["total_waiting"],
                "details": resA["details"]
            }

    # Scenario B
    resB = check_schedule_feasibility(schedule_list, allow_t5_miss=True)
    if resB is not None:
        count_valid_t5_allowed += 1
        if (best_t5_allowed is None) or (resB["total_waiting"] < best_t5_allowed["total_waiting"]):
            best_t5_allowed = {
                "order": schedule_list,
                "total_waiting": resB["total_waiting"],
                "details": resB["details"]
            }

# =============================================================================
# 6) Print the Results
# =============================================================================
print("\n==========================================================")
print("Scenario A: ALL tasks must meet their deadlines (T5 included)")
print(f"Number of valid permutations: {count_valid_strict}")
if best_strict is None:
    print("=> No feasible schedule found in Scenario A.")
else:
    print("=> Best schedule found has total waiting time =", best_strict["total_waiting"])
    print("   Detailed order of jobs:")
    for d in best_strict["details"]:
        print(f"     Job {d['job_id']} (Task={d['task_name']}):"
              f" arrival={d['arrival']}, start={d['start']}, finish={d['finish']},"
              f" deadline={d['deadline']}, waiting={d['waiting']}")

print("\n==========================================================")
print("Scenario B: T5 can miss deadlines (all other tasks must meet theirs)")
print(f"Number of valid permutations: {count_valid_t5_allowed}")
if best_t5_allowed is None:
    print("=> No feasible schedule found in Scenario B.")
else:
    print("=> Best schedule found has total waiting time =", best_t5_allowed["total_waiting"])
    print("   Detailed order of jobs:")
    for d in best_t5_allowed["details"]:
        print(f"     Job {d['job_id']} (Task={d['task_name']}):"
              f" arrival={d['arrival']}, start={d['start']}, finish={d['finish']},"
              f" deadline={d['deadline']}, waiting={d['waiting']}")
