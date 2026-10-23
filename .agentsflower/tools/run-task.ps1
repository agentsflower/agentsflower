<#
.SYNOPSIS
  Compatibility wrapper for .agentflow/tools/run_task.py: translates the old parameter names and delegates,
  preserving the exit code.

.EXAMPLE
  .agentflow\tools\run-task.ps1 T-007 codex          # launch a developer or tester task
  .agentflow\tools\run-task.ps1 T-007 -Manual        # same gate and preparation, no process: a human starts the tool
  .agentflow\tools\run-task.ps1 -Status              # process state of the last attempt of every task
  .agentflow\tools\run-task.ps1 T-007 -Stop          # kill a hung worker (whole process tree), release the lock
  .agentflow\tools\run-task.ps1 T-007 -MarkFinished  # a manual attempt has finished
  .agentflow\tools\run-task.ps1 T-007 -Recheck       # run the end check again for an attempt that exited 0 but failed it

.DESCRIPTION
  Rules: .agentflow/docs/ai-handoff-protocol.md, sections "Runtime state" and "Launching workers".
  The launcher itself is Python (run_task.py): the same gate, worktrees, environment, processes and
  tasks\.runtime\T-NNN.json attempt history on Windows, macOS and Linux. This script only maps
  -Status/-Stop/-MarkFinished/-Recheck/-Manual/-Worker/-DispatchGrant and the positional task/tool
  onto the Python CLI and exits with its exit code. Machine settings are the environment variables
  documented in run_task.py (AGENTFLOW_<TOOL>, AGENTFLOW_<TOOL>_ARGS, AGENTFLOW_<TOOL>_PROBE,
  AGENTFLOW_PYTHON, AGENTFLOW_WORKER_PYTHON).
#>
param(
  [Parameter(Position = 0)][string]$TaskId,
  [Parameter(Position = 1)][ValidateSet('codex', 'claude', 'agy', 'devin')][string]$Tool,
  [switch]$Status,
  [switch]$Stop,
  [switch]$MarkFinished,
  [switch]$Recheck,
  [switch]$Manual,
  [switch]$Worker,
  [string]$DispatchGrant
)
$ErrorActionPreference = 'Stop'
$env:PYTHONUTF8 = '1'

# Same interpreter rules as the Python launcher: AGENTFLOW_PYTHON, else python (not the Microsoft Store
# stub), else py -3.
function Resolve-Exe([string]$name, [string]$override) {
  if (-not $override) { return $name }
  $m = Get-Item $override -ErrorAction SilentlyContinue | Sort-Object LastWriteTime | Select-Object -Last 1
  if ($m) { $m.FullName } else { $override }
}
$python = @(if ($env:AGENTFLOW_PYTHON) { Resolve-Exe 'python' $env:AGENTFLOW_PYTHON }
  elseif (($c = Get-Command python -ErrorAction SilentlyContinue) -and $c.Source -notmatch '\\WindowsApps\\') { 'python' }
  elseif (Get-Command py -ErrorAction SilentlyContinue) { 'py'; '-3' }
  else { 'python' })

$argv = @()
if ($TaskId) { $argv += $TaskId }
if ($Tool) { $argv += $Tool }
if ($Status) { $argv += '--status' }
if ($Stop) { $argv += '--stop' }
if ($MarkFinished) { $argv += '--mark-finished' }
if ($Recheck) { $argv += '--recheck' }
if ($Manual) { $argv += '--manual' }
if ($Worker) { $argv += '--worker' }
if ($DispatchGrant) { $argv += '--dispatch-grant', $DispatchGrant }

$py = $python[0]; $pyArgs = @($python | Select-Object -Skip 1)
& $py @pyArgs (Join-Path $PSScriptRoot 'run_task.py') @argv
exit $LASTEXITCODE
