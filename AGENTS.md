# Agent instructions

This repository is the AgentsFlower template. Its product is `.agentsflower/` plus the entry points and the guide.

<!-- agentsflower:begin -->
## AgentsFlower

AgentsFlower version: 2.17.0. Workflow files live in `.agentsflower/`; this block is template-owned and replaced on update.

Workflow and instruction authority: `.agentsflower/docs/ai-handoff-protocol.md`. Start with the applicable session section below. Project settings:
`.agentsflower/docs/project-rules.md` (and any rules in this file outside this block).

- With a role (`.agentsflower/roles/<role>.md`, or `/start-role <role> ...`): protocol section "Starting a role session".
  Workers (developer, tester, deployer) do not update project memory.
- Without a role (Single Mode): protocol section "Starting a new AI session" before substantial work; "Updating memory"
  before ending a long session.
<!-- agentsflower:end -->

## Project rules

### AgentsFlower source authority (human instruction, 2026-10-23)

- This is the independently maintained AgentsFlower project. The sole remote authority for its versions, releases, updates and migrations is https://github.com/agentsflower/agentsflower (origin), together with this project's local branch and changelog.
- A fork relationship or a remote named upstream does not authorize using the parent as a source of updates or as the definition of latest. Do not query, recommend, fetch, merge or migrate from AleksandrPankin/AgentFlow unless the human explicitly requests that repository in the current task.
- For version checks, report local VERSION and the version in origin's actual default branch separately. State the exact repository/ref checked. Do not conflate a newer parent release with an update of this project.
- Existing generic instructions mentioning upstream refer to the project's configured local template workflow; they do not override this source-authority rule. Never modify remotes or push without explicit authorization.

### Strict prohibition of direct coding in chat / Conductor role boundary (human instruction, 2026-10-24)

- The main IDE / chat session functions EXCLUSIVELY as the Conductor / Single-window Cockpit for communication, architectural discussion, task contract formalization, and human approvals.
- Modifying, writing, or hacking production/project code directly in this chat session is STRICTLY FORBIDDEN.
- All code implementation, refactoring, and bug fixes MUST be executed exclusively by autonomous AgentsFlower worker roles (`developer`, `tester`, etc.) dispatched via `.agentsflower/tools/run-task.py` or `.agentsflower/tools/dispatch.py` in isolated task worktrees.
- No task can be marked done without independent verification by the `tester` role and gate validation.

- Repository parameters: [.agentsflower/docs/project-rules.md](.agentsflower/docs/project-rules.md).

- This repository develops the template itself: template-owned files are its product (`.agentsflower/README.md`).
- A change to the protocol, a role, a tool or the dashboard gets a `CHANGELOG.md` entry, a version bump in
  `.agentsflower/VERSION` and a dated entry in `.agentsflower/state/decisions.md`; its migration notes say what an
  installed project must do.
- Keep `.agentsflower/tools/install.py` and these entry points in step: `.agentsflower/tests/test_install.py` checks it.
- Before a commit: `python -m unittest discover -s .agentsflower/tests`.
