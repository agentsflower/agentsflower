# Session Handoff

Background session devin, 2026-10-21 ~08:35Z (devin-background): resolved the
T-094 accept need end to end. Root cause was contract authoring, not the
product: T-094's `Allowed files` used comma-separated bullets and gate.py
parses only the first token per bullet, so five inherited-base files read as
out of scope. Per the T-084 carrier precedent: T-094 rejected -> T-095
carrier (one path per line) verified PASS on 0477331; its merge then hit the
predicted stale-branch conflict vs main 2.15.5 -> T-096 merge-only successor
landed it (merge 8b588f9, commit 6754959, suite 424/0/3 on the merge SHA;
VERSION/AGENTS = 2.15.5, both changelog entries verbatim). Ledger T-096 done.

What waits: T-036 and T-066 are `blocked` - Jev selects swe-2-max for both
but effort-xhigh confidence stays ~0.42-0.45 across four assessments
(complexity ~1.9/2), so the admission gate refuses and only a human
`Routing exception:` line or a re-scope decision opens them (details +
options in questions.md, 2026-10-21 entry). After the answer: T-036 -> its
tester -> T-038 -> T-044 -> T-046 -> T-048, then T-066.

State: main 8b588f9 @ 2.15.5 holds the whole routing stack (assessment,
admission, scheduler integration, preferred-CLI independence, fixed-clock
test repair). Rejected draft branches/worktrees kept for the human: t-076,
t-082, t-087, t-093, t-094, t-095; T-091's 0bf4ac0 is merged history -
cleanup is safe but stays the human's call.

Known-issues gained: gate.py `paths()` takes only the first whitespace token
per `Allowed files` bullet - comma-separated lines silently fail the scope
check; author one path per line. gate.py endcheck still crashes on a
deleted worktree (recorded earlier).

Human prefers Devin for all roles, reports no usage limits until 2026-11-01
(qualitative, not measured). Codex and Claude CLIs statically excluded in
docs/model-options.json ("until" fields) until the human restores them;
agy limited until 2026-10-21T22:09Z.

Conductor running hidden (PID 10656), 1-minute rounds, 1200s worker cap.
Autostart at logon off; current-session restart in runbook/worker-recovery.md.

Result criteria need `- ID: pass - evidence`; T-036 aligns the stale role
examples. Only AgentFlow and disposable fixtures; no external rollout/push/
tags/releases. Source authority remains origin vcherstar/AgentFlow.

Read: project-rules.md, current-step.md, questions.md (T-036/T-066 routing
decision is the one open ask), ledger, T-096 Result.
