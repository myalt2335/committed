import subprocess
import os
import shutil
import time
import sys

BATCH = 100_000
GOAL = 5_555_555
REPO_URL = "https://github.com/myalt2335/commit.git"
REPO_DIR = "work"
CUR_FILE = "curcomit.txt"

SCRIPT_NAME = os.path.basename(sys.argv[0])

STARTUP_SLEEP = 5
BATCH_SLEEP = 2

def log(msg):
    print(msg, flush=True)


def run(cmd, cwd=None, capture=False):
    if capture:
        return subprocess.check_output(cmd, shell=True, cwd=cwd).decode().strip()
    subprocess.run(cmd, shell=True, check=True, cwd=cwd)


def clean():
    if os.path.exists(REPO_DIR):
        shutil.rmtree(REPO_DIR)


def read_current():
    if not os.path.exists(CUR_FILE):
        raise FileNotFoundError(f"{CUR_FILE} not found. Create it with the current commit count.")
    with open(CUR_FILE, "r") as f:
        return int(f.read().strip())


def write_current(val):
    with open(CUR_FILE, "w") as f:
        f.write(str(val))
        f.flush()
        os.fsync(f.fileno())


FINAL_README = """# 5,555,555 commits lol

Please don't hurt me github

This script ran on a single raspberry pi btw I thought that was kinda impressive
"""


def do_batch(total, to_make, final_batch):
    for mode in ("shallow", "partial"):
        log(f"Cloning mode: {mode}")
        clean()

        if mode == "shallow":
            run(f"git clone --depth 1 {REPO_URL} {REPO_DIR}")
        else:
            run(f"git clone --filter=blob:none {REPO_URL} {REPO_DIR}")

        for i in range(to_make):
            commit_num = total + i + 1
            path = os.path.join(REPO_DIR, "commit.py")
            with open(path, "w") as f:
                f.write(f"# commit {commit_num}\n")

            run("git add commit.py", cwd=REPO_DIR)
            run(f'git commit -m "commit {commit_num}"', cwd=REPO_DIR)

        new_total = total + to_make

        if final_batch:
            commit_py = os.path.join(REPO_DIR, "commit.py")
            if os.path.exists(commit_py):
                os.remove(commit_py)

            readme = os.path.join(REPO_DIR, "README.md")
            with open(readme, "w") as f:
                f.write(FINAL_README)

            src_script = os.path.abspath(sys.argv[0])
            dst_script = os.path.join(REPO_DIR, SCRIPT_NAME)
            shutil.copy(src_script, dst_script)

            run("git add -A", cwd=REPO_DIR)
            run(
                'git commit -m "5,555,555 - update README, delete commit.py, add spam.py"',
                cwd=REPO_DIR,
            )
            new_total += 1

        try:
            run("git push", cwd=REPO_DIR)
            clean()
            return new_total
        except subprocess.CalledProcessError:
            log("Push failed.")
            if mode == "shallow":
                log("Retrying batch with partial clone...")
                continue
            else:
                raise

    return total


total = read_current()
log(f"Starting from {total} commits")

if total >= GOAL:
    log("Goal already reached or exceeded.")
    sys.exit(0)

log(f"Sleeping {STARTUP_SLEEP}s before starting...")
time.sleep(STARTUP_SLEEP)

batch_num = 0

while total < GOAL:
    remaining = GOAL - total

    if remaining <= BATCH:
        to_make = remaining - 1
        final_batch = True
    else:
        to_make = BATCH
        final_batch = False

    batch_num += 1
    log(f"\nBatch {batch_num}: making {to_make} commits")
    time.sleep(2)

    total = do_batch(total, to_make, final_batch)

    write_current(total)
    log(f"Total commits now: {total}")

    if final_batch:
        break

    log(f"Sleeping {BATCH_SLEEP}s before next batch...")
    time.sleep(BATCH_SLEEP)

log("\nScript complete.")
