# Questions for the human

- Optional public README source input: exact AI Home Design SaaS URL and
  YouTube Transcript Extension listing URL. Never invent missing IDs/URLs.
- External release gate: CI run 39026298541 on 50adf65 FAILED - all
  windows-latest and macos-latest test jobs exit 1 at the unittest step;
  ubuntu tests and both package-integration jobs pass. Logs are not readable
  without repository auth (API 403). Needed from the human: open the run in the
  browser and paste the failing test names/step output, or authenticate `gh`,
  so the runner-specific failure can be fixed; a rerun happens on the next
  authorized push anyway. Tag/release publication remains human-only.

No additional plan approval is needed for the completed local task pool.
