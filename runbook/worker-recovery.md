# Проверка фоновой работы AgentFlow

Проверено 18.10.2026: Windows 10 Pro 19045, AgentFlow 2.15.1.

1. В PowerShell откройте репозиторий:

   ```powershell
   Set-Location -LiteralPath 'E:\Projects\AgentFlow\code'
   pwsh -NoProfile -File .agentflow/tools/conductor-panel.ps1 -Status
   ```

   Результат: «Сторож: работает», время последнего круга обновляется.

2. Проверьте работника:

   ```powershell
   python .agentflow/tools/run_task.py --status
   ```

   У запущенного работника статус `running`. В его JSON в
   `.agentflow/tasks/.runtime/` записаны `workerTimeout` и `deadline` (UTC).
   Первая строка лога подтверждает `power guard: ES_SYSTEM_REQUIRED held`.

3. После обновления перезапустите сторож, чтобы PowerShell загрузил новый цикл:

   ```powershell
   pwsh -NoProfile -File .agentflow/tools/conductor-panel.ps1 -Stop
   $env:AGENTFLOW_WORKER_TIMEOUT='1200'
   $env:AGENTFLOW_DEVIN_MODEL_PROBE='on'
   $env:AGENTFLOW_ORCHESTRATORS='devin'
   $env:AGENTFLOW_DEVIN_ARGS='--model swe-2-high'
   $taskScript=(Resolve-Path '.agentflow/tools/conductor.ps1').Path
   $taskBody='$PSDefaultParameterValues[''Start-Process:WindowStyle'']=''Hidden''; & ''' + $taskScript.Replace("'","''") + ''' -IntervalMinutes 1'
   $taskEncoded=[Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($taskBody))
   Start-Process -FilePath (Get-Command pwsh).Source -WindowStyle Hidden -WorkingDirectory (Get-Location).Path -ArgumentList '-NoProfile','-ExecutionPolicy','Bypass','-EncodedCommand',$taskEncoded
   ```

   Повторите проверку из шага 1: сторож работает, круг обновляется каждую минуту.
   Эти команды используют настроенное окружение AgentFlow и запускают процесс
   для текущего сеанса Windows. Регистрация автозапуска при входе — отдельная
   настройка; на момент проверки она выключена.
