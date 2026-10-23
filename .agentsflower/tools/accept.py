"""Accept one task after its Result: verify, merge, ledger, cleanup - stopping at the first failure.

  python .agentflow/tools/accept.py T-007            # accept a developer or tester task
  python .agentflow/tools/accept.py T-007 --dry-run  # print the steps without changing anything

Rules: .agentflow/docs/ai-handoff-protocol.md, "Task lifecycle" and "Git rules". Only the Orchestrator (or a
Single Mode session) runs this, from the main folder with every repository on its main branch.

Developer: gate.py verify -> a trial merge in every repository (`git merge-tree`, writes nothing) -> the
           integrated check (the task's Checks run on a temporary trial-merge tree per repository) ->
           git merge --no-ff <branch> in every repository -> ledger review/done -> git worktree remove ->
           git branch -d.
Tester:    gate.py verify -> ledger review/done with the Verifies commits (nothing to merge).
Every step runs only when the previous one succeeded; a conflict found by the trial merge or a Check failing
on the integrated result stops before any repository is merged, and a failed merge is aborted. The printed
log says exactly which steps ran, and .agentflow/tasks/.runtime/<id>.accept.json durably records which
repositories were integrated/merged: an interrupted multi-repository run is resumed from git state and that
file, never claimed atomic. Nothing is force-deleted: worktree removal and `git branch -d` refuse unmerged
or dirty state, and that refusal is reported, not overridden.
"""
import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from paths import FLOW_ROOT, REPO_ROOT  # noqa: E402
import gate  # noqa: E402
import ledger  # noqa: E402

TOOLS = FLOW_ROOT / "tools"


class Stop(Exception):
    pass


def run(cmd, dry, cwd=REPO_ROOT, check=True):
    print(("  (dry run) " if dry else "  $ ") + " ".join(str(c) for c in cmd))
    if dry:
        return ""
    p = subprocess.run([str(c) for c in cmd], cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    out = (p.stdout + p.stderr).strip()
    if out:
        print("    " + out.replace("\n", "\n    "))
    if check and p.returncode:
        raise Stop(f"step failed (exit {p.returncode}): {' '.join(str(c) for c in cmd)}")
    return p.stdout


def remove_setup_links(t, path, dry):
    """Delete `Setup: - link:` junctions inside a checkout before `git worktree remove`: git follows the
    junction and deletes the target's contents (the main folder's copy, such as node_modules). Removing the
    reparse point itself (rmdir for a junction, unlink for a symlink) leaves the target untouched."""
    if not path:
        return
    for s in t.get("setup", []):
        if s["kind"] != "link":
            continue
        p = Path(path) / s["path"]
        try:
            st = p.lstat()
        except OSError:
            continue
        if not (p.is_symlink() or getattr(st, "st_file_attributes", 0) & 0x400):  # FILE_ATTRIBUTE_REPARSE_POINT
            continue
        if dry:
            print(f"  (dry run) unlink junction {p}")
        elif p.is_symlink():
            p.unlink()
        else:
            p.rmdir()


def ledger_rows():
    path = ledger.ledger_path()
    if not path.exists():
        return {}
    _, cols, rows, _, _ = ledger.load(path)
    return {r[0]: dict(zip(cols, r)) for r in rows}


def to_done(tid, sha, dry):
    py = sys.executable
    st = ledger_rows().get(tid, {}).get("Status")
    if st == "done":
        print(f"  ledger: {tid} is already done")
        return
    if st != "review":
        run([py, TOOLS / "ledger.py", "set", tid, "--status", "review"], dry)
    run([py, TOOLS / "ledger.py", "set", tid, "--status", "done", "--commit", sha], dry)


def accept_progress(tid):
    """Durable record of an interrupted acceptance: per-repository integrated/merged state. Resume reads
    git state itself (`todo`); this file shows how far a run got - progress, not a claim of atomicity."""
    p = FLOW_ROOT / "tasks" / ".runtime" / f"{tid}.accept.json"
    if p.exists():
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                data.setdefault("integrated", {})
                data.setdefault("merged", [])
                return p, data
        except (OSError, ValueError):
            pass
    return p, {"taskId": tid, "integrated": {}, "merged": []}


def dirty(repo):
    """Tracked changes that could mix into a merge. Not counted: untracked files, the memory under .agentflow/, and in
    the memory repository the workspace repositories themselves (each is checked on its own). Reads `git status
    --porcelain -z` raw: a trimmed porcelain line loses its leading space and shifts every path by one character."""
    p = subprocess.run(["git", "-C", str(gate.repo_dir(repo)), "status", "--porcelain", "-z"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    own = set(gate.workspace_repos()) if repo == "" else set()
    out, entries = [], p.stdout.split("\0")
    i = 0
    while i < len(entries):
        e = entries[i]
        i += 1
        if len(e) < 4:
            continue
        code, path = e[:2], e[3:].rstrip("/")
        if code[0] in "RC":  # a rename or copy carries its source path as the next entry
            i += 1
        if code == "??" or (repo == "" and (path.startswith(".agentsflower/") or path.startswith(".agentflow/") or path in own)):
            continue
        out.append(f"{code} {path}")
    return out


def accept(tid, dry):
    t = gate.parse(tid)
    status = ledger_rows().get(tid, {}).get("Status")
    if status not in ("in progress", "review", "done"):
        raise Stop(f"{tid}: cannot accept ledger status {status!r}; reconcile the launch before merging")
    repos = t["repos"]
    print(f"{tid}: role {t['role']}, repositories: {', '.join(r or '(this repository)' for r in repos)}")
    for r in sorted(set(repos) | {""}):
        if d := dirty(r):
            raise Stop(f"uncommitted changes in {r or 'the main folder'}: " + "; ".join(d[:5]))

    with tempfile.TemporaryDirectory() as tmp:
        print("1. verify")
        run([sys.executable, TOOLS / "gate.py", "verify", tid, "--out", Path(tmp) / "verify.json"], dry)

    if t["role"] == "tester":
        print("2. ledger")
        to_done(tid, t["sha"], dry)
        print(f"{tid} accepted (tester; nothing to merge).")
        return

    if t["role"] != "developer":
        raise Stop(f"role '{t['role']}': accept handles developer and tester tasks; a deployer is closed by hand")

    shas = gate.parse_shas(gate.result_field(t, "Change"), repos)
    if not shas:
        raise Stop('Result needs "Change: ..." naming one commit per repository')
    for r in shas:
        shas[r] = gate.git("rev-parse", "--verify", "--quiet", f"{shas[r]}^{{commit}}", cwd=gate.repo_dir(r)) or shas[r]
    title = ledger_rows().get(tid, {}).get("Title", "").strip()
    todo = [r for r in repos if not gate.git_ok("merge-base", "--is-ancestor", shas[r], "HEAD", cwd=gate.repo_dir(r))]

    print("2. trial merge")
    for r in repos:
        if r not in todo:
            print(f"  {t['branch']}{' in ' + r if r else ''} is already merged")
            continue
        run(["git", "merge-tree", "--write-tree", "HEAD", t["branch"]], dry, cwd=gate.repo_dir(r))

    print("3. integrated check")
    ppath, prog = accept_progress(tid)
    if dry:
        print("  (dry run) the task Checks run on a temporary trial-merge tree per repository")
    else:
        ppath.parent.mkdir(parents=True, exist_ok=True)
        ip, ichecks, refs = gate.integrated_problems(t, shas, ppath.with_suffix(".log"))
        for c in ichecks:
            print(f"  integrated check exit {c['exit']}: {c['cmd']}")
        bad = ip + [f"check failed on the integrated result (exit {c['exit']}): {c['cmd']}"
                    for c in ichecks if c["exit"]]
        for r in repos:
            prog["integrated"][r] = {"ok": not bad}
        gate.write_atomic(ppath, prog)
        if bad:
            raise Stop("the integrated result does not pass the task Checks: " + "; ".join(bad))

    print("4. merge")
    for r in todo:
        try:
            run(["git", "merge", "--no-ff", t["branch"], "-m", f"Merge {tid}: {title or t['branch']}"], dry, cwd=gate.repo_dir(r))
        except Stop:
            run(["git", "merge", "--abort"], dry, cwd=gate.repo_dir(r), check=False)
            done = todo[:todo.index(r)]
            raise Stop(f"merge of {t['branch']}{' in ' + r if r else ''} failed and was aborted"
                       + (f"; already merged: {', '.join(done)}" if done else "") + "; resolve it in a successor task")
        if not dry:
            if r not in prog["merged"]:
                prog["merged"].append(r)
            gate.write_atomic(ppath, prog)

    print("5. ledger")
    to_done(tid, gate.sha_text(shas), dry)

    print("6. cleanup")
    remove_setup_links(t, t["worktree"], dry)
    for c in t["checkouts"]:
        remove_setup_links(t, c["path"], dry)
        if Path(c["path"]).exists():
            run(["git", "worktree", "remove", c["path"]], dry, cwd=c["repo"])
        else:
            print(f"  worktree {c['path']} is already gone")
        run(["git", "worktree", "prune"], dry, cwd=c["repo"])
        if gate.git_ok("rev-parse", "--verify", "--quiet", f"refs/heads/{t['branch']}", cwd=c["repo"]):
            run(["git", "branch", "-d", t["branch"]], dry, cwd=c["repo"])
        else:
            print(f"  branch {t['branch']} is already deleted in {c['repo']}")
    w = Path(t["worktree"] or "")
    if repos != [""] and w.is_dir() and not any(w.iterdir()) and not dry:
        w.rmdir()  # the empty folder that held the task's worktrees
    print(f"{tid} accepted and merged.")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("id")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    try:
        accept(a.id, a.dry_run)
    except (Stop, gate.TaskError) as e:
        print(f"STOPPED: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
