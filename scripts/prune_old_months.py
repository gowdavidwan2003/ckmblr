#!/usr/bin/env python3
"""Permanently remove one month of daily editions and sources from the repo.

Runs on the last day of each month and removes the month three back: January
goes at the end of April, February at the end of May, and so on. That keeps
the current month plus the three before it. Run on any other day it removes
only months that are already overdue, so a missed month-end is caught up by
the next run.

Deleting a folder in a normal commit leaves every file in git history, so the
repo never shrinks. This rewrites history instead (git filter-repo), so the
removed month is gone from every commit, then force-pushes main to GitHub.
There is no undo.

What goes, for month YYYY-MM:
  editions/YYYY-MM-DD/   daily posts, and the ICO brief filed under its run date
  sources/YYYY-MM-DD/    Coffee Board PDFs, prices, pepper reports, ICO reports
  editions/YYYY-MM/, sources/YYYY-MM/, ico/YYYY-MM/   the older monthly layout
Undated folders (sources/statistics/, sources/advisories/) are never touched.

Dry run unless --apply is given.

  python scripts/prune_old_months.py                  # dry run: what is due today
  python scripts/prune_old_months.py --apply          # the monthly routine
  python scripts/prune_old_months.py --month 2026-09  # only that month, if due

Refuses to run when main has uncommitted changes to tracked files (filter-repo
resets the working tree and would lose them), when local and GitHub main have
diverged, or when not on main. Untracked files are left alone, except inside
the month's own folders, which are deleted from disk as well.

Exit codes
  0  pruned, nothing to prune, or not the last day of the month
  1  refused -- a precondition failed, nothing was changed
  2  the rewrite or the push failed -- GitHub still has the old history
"""

import argparse
import os
import datetime as dt
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BRANCH = "main"
KEEP_MONTHS = 3


def git(*args, check=True):
    r = subprocess.run(["git", *args], cwd=ROOT, capture_output=True,
                       text=True, encoding="utf-8")
    if check and r.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed:\n{r.stderr.strip()}")
    return r.stdout.strip()


def refuse(msg):
    print(f"REFUSED: {msg}\nNothing was changed.")
    sys.exit(1)


def month_back(today, n):
    y, m = today.year, today.month - n
    while m < 1:
        m += 12
        y -= 1
    return f"{y:04d}-{m:02d}"


def repo_size():
    out = git("count-objects", "-vH")
    return {k: v for k, v in (l.split(": ", 1) for l in out.splitlines())}


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--month", help="only this YYYY-MM (default: every month that is due)")
    ap.add_argument("--apply", action="store_true", help="actually rewrite history and push")
    ap.add_argument("--today", help=argparse.SUPPRESS)  # YYYY-MM-DD, for testing
    a = ap.parse_args()

    today = dt.date.fromisoformat(a.today) if a.today else dt.date.today()
    last_day = (today + dt.timedelta(days=1)).day == 1
    # months strictly before this one go; on the last day the month three back
    # joins them. Anything older that a missed run left behind goes too.
    cutoff = month_back(today, KEEP_MONTHS - 1 if last_day else KEEP_MONTHS)
    if a.month and not re.fullmatch(r"\d{4}-\d{2}", a.month):
        refuse(f"--month must be YYYY-MM, got {a.month!r}")
    if a.month and a.month >= cutoff:
        refuse(f"{a.month} is not due yet -- months from {cutoff} on are kept today")
    print(f"{today}: removing dated months before {cutoff}   "
          f"({'APPLY' if a.apply else 'dry run'})")

    # --- preconditions
    if git("rev-parse", "--is-shallow-repository") == "true":
        # cloud checkouts can be shallow; the rewrite needs every commit
        print("Shallow clone -- fetching full history first.")
        git("fetch", "--unshallow", "origin")
    branch =git("rev-parse", "--abbrev-ref", "HEAD")
    if branch != BRANCH:
        refuse(f"on branch {branch!r}, not {BRANCH!r}")
    dirty = git("status", "--porcelain", "--untracked-files=no")
    if dirty and not a.apply:
        print("WARNING: --apply will refuse until these are committed or discarded:\n" + dirty)
    elif dirty:
        refuse("uncommitted changes to tracked files -- commit or discard them first:\n" + dirty)
    git("fetch", "origin", BRANCH)
    behind = int(git("rev-list", "--count", f"HEAD..origin/{BRANCH}"))
    ahead = int(git("rev-list", "--count", f"origin/{BRANCH}..HEAD"))
    if behind and ahead:
        refuse(f"local {BRANCH} and GitHub have diverged ({ahead} ahead, {behind} behind)")
    if behind:
        print(f"Fast-forwarding {behind} commit(s) from GitHub first.")
        git("merge", "--ff-only", f"origin/{BRANCH}")
    if ahead and a.apply:
        # push unpushed commits normally first, so local == GitHub before the
        # rewrite and a failed push can always be recovered by resetting to GitHub
        print(f"Pushing {ahead} unpushed commit(s) first.")
        git("push", "origin", BRANCH)
        git("fetch", "origin", BRANCH)

    # --- what goes
    dated = re.compile(r"^(editions|sources|ico)/(\d{4}-\d{2})(-\d{2})?/")
    def due(m):
        return m == a.month if a.month else m < cutoff
    in_history = sorted({p for p in git("log", "--all", "--name-only", "--format=").splitlines()
                         if (x := dated.match(p)) and due(x.group(2))})
    on_disk = sorted(d for top in ("editions", "sources", "ico") if (ROOT / top).is_dir()
                     for d in (ROOT / top).iterdir()
                     if d.is_dir() and (x := dated.match(f"{top}/{d.name}/")) and due(x.group(2)))
    folders = sorted({"/".join(p.split("/")[:2]) for p in in_history}
                     | {d.relative_to(ROOT).as_posix() for d in on_disk})
    if not folders:
        print("Nothing due in history or on disk -- nothing to do.")
        return
    months = sorted({dated.match(f + "/").group(2) for f in folders})
    pattern = rf"^(editions|sources|ico)/({'|'.join(months)})(-[0-9]{{2}})?/"
    print(f"Month(s): {', '.join(months)} -- {len(in_history)} file(s) in git history, "
          f"{len(folders)} folder(s):")
    for f in folders:
        print(f"  {f}/")

    before = repo_size()
    if not a.apply:
        print(f"\nRepo now: {before['size-pack']} packed, {before['size']} loose.")
        print("Dry run -- re-run with --apply to remove permanently.")
        return

    # --- rewrite history
    url = git("remote", "get-url", "origin")
    old_tip = git("rev-parse", f"origin/{BRANCH}")
    if in_history:
        # Windows: the repo sits deep under OneDrive and repack temp names are long
        env = {**os.environ, "GIT_CONFIG_COUNT": "1",
               "GIT_CONFIG_KEY_0": "core.longpaths", "GIT_CONFIG_VALUE_0": "true"}
        r = subprocess.run([sys.executable, "-m", "git_filter_repo", "--force",
                            "--invert-paths", "--path-regex", pattern],
                           cwd=ROOT, env=env, capture_output=True, text=True, encoding="utf-8")
        if r.returncode != 0:
            if "origin" not in git("remote").split():
                git("remote", "add", "origin", url)
            print("FILTER-REPO FAILED -- nothing was pushed, GitHub is untouched, but local\n"
                  "history may be partly rewritten. Do not push. Re-clone from GitHub if unsure.\n"
                  + (r.stderr or r.stdout).strip())
            sys.exit(2)
    # filter-repo drops the origin remote so nothing is pushed by accident
    if "origin" not in git("remote").split():
        git("remote", "add", "origin", url)

    for d in on_disk:
        shutil.rmtree(d, ignore_errors=True)

    if in_history:
        r = subprocess.run(["git", "push", f"--force-with-lease={BRANCH}:{old_tip}",
                            "origin", BRANCH],
                           cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
        if r.returncode != 0:
            print("PUSH FAILED -- history is rewritten here but GitHub still has the old one.\n"
                  "Most likely a daily post was pushed meanwhile. Nothing is lost: run\n"
                  "  git fetch origin && git reset --hard origin/main\n"
                  "then re-run with --apply.\n" + r.stderr.strip())
            sys.exit(2)
        git("fetch", "origin", BRANCH)
        git("branch", f"--set-upstream-to=origin/{BRANCH}", BRANCH)

    after = repo_size()
    print(f"\nRemoved {', '.join(months)}. Repo: {before['size-pack']} -> {after['size-pack']} packed.")
    if in_history:
        print("GitHub main is force-pushed. Any other clone of this repo must be deleted "
              "and cloned fresh -- pushing from an old clone brings the month back.")


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as e:
        refuse(str(e))
