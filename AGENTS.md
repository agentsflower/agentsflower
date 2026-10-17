# Agent instructions

This repository is the AgentFlow template. Its product is `.agentflow/` plus the entry points and the guide.

<!-- agentflow:begin -->
## AgentFlow

AgentFlow version: 2.13.3. Workflow files live in `.agentflow/`; this block is template-owned and replaced on update.

Workflow and instruction authority: `.agentflow/docs/ai-handoff-protocol.md`. Start with the applicable session section below. Project settings:
`.agentflow/docs/project-rules.md` (and any rules in this file outside this block).

- With a role (`.agentflow/roles/<role>.md`, or `/start-role <role> ...`): protocol section "Starting a role session".
  Workers (developer, tester, deployer) do not update project memory.
- Without a role (Single Mode): protocol section "Starting a new AI session" before substantial work; "Updating memory"
  before ending a long session.
<!-- agentflow:end -->

## Project rules

### AgentFlow source authority (human instruction, 2026-10-15)

- This is the independently maintained vcherstar/AgentFlow project. The sole remote authority for its versions, releases, updates and migrations is https://github.com/vcherstar/AgentFlow (origin), together with this project's local branch and changelog.
- A fork relationship or a remote named upstream does not authorize using the parent as a source of updates or as the definition of latest. Do not query, recommend, fetch, merge or migrate from AleksandrPankin/AgentFlow unless the human explicitly requests that repository in the current task.
- For version checks, report local VERSION and the version in origin's actual default branch separately. State the exact repository/ref checked. Do not conflate a newer parent release with an update of this project.
- Existing generic instructions mentioning upstream refer to the project's configured local template workflow; they do not override this source-authority rule. Never modify remotes or push without explicit authorization.

- Repository parameters: [.agentflow/docs/project-rules.md](.agentflow/docs/project-rules.md).

- This repository develops the template itself: template-owned files are its product (`.agentflow/README.md`).
- A change to the protocol, a role, a tool or the dashboard gets a `CHANGELOG.md` entry, a version bump in
  `.agentflow/VERSION` and a dated entry in `.agentflow/state/decisions.md`; its migration notes say what an
  installed project must do.
- Keep `.agentflow/tools/install.py` and these entry points in step: `.agentflow/tests/test_install.py` checks it.
- Before a commit: `python -m unittest discover -s .agentflow/tests`.
