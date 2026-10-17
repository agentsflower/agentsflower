# Current Step

2026-10-17: Stage 3/4 closed (pilot at 2.12.0, drift audit clean). Repository-
only scope since 2026-10-17: no external rollout, no WatermarkRemover/other-
project work; installer/migration validation via disposable AgentFlow fixtures
(project-rules.md). Mandatory Jev adequacy routing active (model-options.json +
recorded route.py assessments in .runtime).

Stage 5 chain progress: T-028 rejected on independent fail review -> T-050
done+accepted (2.12.2); T-030 rejected on partial review -> T-052 done, tester
T-053 running (devin, verifying the quoted-phrase fix on 5b3797b). T-042 mockup
done and merged - AWAITING HUMAN VARIANT SELECTION (questions.md).

NEXT: when T-053 verdict lands, decide T-052 per lifecycle (accept or successor).
Then T-032 (swe-2-max, assessed) -> its tester -> T-034 -> T-040 (routing
enforcement, depends T-034) -> T-036 -> T-038, each with a tester. Dashboard
impl T-044 -> T-046 -> T-048 launches only after T-038 accepted AND the human's
mockup selection is recorded. Every launch requires the persisted route.py
assessment (mandatory adequacy policy). Codex is environment-blocked for
workers on Windows (sandbox denies writes outside the checkout); testers run
on devin swe-2-max/swe-2-high under the documented same-tool necessity.

CI run 39026298541 triaged: windows-latest and macos-latest test jobs fail at
the unittest step; ubuntu and package jobs pass; logs need authenticated access
(details in known-issues). No tags, publication, deployment or future stage
push authorized.
