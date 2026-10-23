# Инструкция: как пользоваться AgentsFlower

Шаблон памяти проекта с командой агентов: оркестратор, разработчик, тестировщик, деплоер. Как это устроено внутри — [README](README.md) и [протокол](.agentsflower/docs/ai-handoff-protocol.md). Здесь только «что нажать и что ввести». Английская версия этой инструкции: [GUIDE.md](GUIDE.md).

Шаблон — папка, куда склонирован этот репозиторий. Ниже она обозначена `<AgentsFlower>`: подставь свой путь. Всё, что AgentsFlower кладёт в проект, лежит в одной папке `.agentsflower/`; в корне проекта появляются только маленькие указатели (`AGENTS.md`, `CLAUDE.md`, `.claude/commands/`) и отмеченный блок в `.gitignore`. Свои `docs/`, `tasks/`, `tools/` проекта не трогаются.

Нужно на машине: git, Python 3.10+ (только стандартная библиотека — сторонних зависимостей нет) и CLI инструментов, которыми будут работать исполнители (`claude`, `codex`, `agy`, `devin`). Лаунчер — `run_task.py` (чистый Python, кросс-платформенный); на Windows PowerShell нужен для обёртки `run-task.ps1` и необязательного сторожа: 7 — проверенная версия, совместимость 5.1 не проверена.

---

# Часть 1. Установка

| Что в папке проекта | Вариант |
|---|---|
| Пусто, форк или существующий код без AgentsFlower (даже если есть свои `AGENTS.md`, `tasks/`, `tools/`) | [A. Установить](#a-установить) |
| Папка с несколькими репозиториями (например `code/` с `backend/`, `web/`…) | [A2. Несколько репозиториев](#a2-несколько-репозиториев) |
| Уже есть `.agentsflower/` | [B. Обновить](#b-обновить) |
| Старая раскладка 2.1: `docs/ai-handoff-protocol.md`, `tools/gate.py` в корне | [C. Переход со старой раскладки](#c-переход-со-старой-раскладки) |
| Нужна команда `agentsflower` | [D. Установить из пакета](#d-установить-из-пакета) |
| Нужен MCP-сервер в IDE | [E. MCP-сервер](#e-mcp-сервер-необязательно) |

## A. Установить

### Шаг 1. Git

Агентам нужен git с основной веткой и хотя бы одним коммитом, а установщик ставит шаблон только в **корень** git-репозитория. Для папки с несколькими репозиториями — [A2](#a2-несколько-репозиториев).

Пустая папка:

```bash
cd /path/to/project          # Windows: cd D:\path\to\project
git init -b main
git commit --allow-empty -m "init"
```

Существующий репозиторий: проверь, что всё закоммичено (`git status`), и создай ветку под установку: `git switch -c chore/agentsflower`.

### Шаг 2. Посмотреть, что будет сделано

```bash
python <AgentsFlower>/.agentsflower/tools/install.py /path/to/project --dry-run
```

Ожидаемый результат: список действий, ничего не записано. Установщик ничего не удаляет; если `AGENTS.md`, `CLAUDE.md` или `.gitignore` уже есть, их содержимое остаётся, а управляемый блок встаёт между `agentsflower:begin` и `agentsflower:end`. В `.claude/commands/` появляются однострочные указатели; существующие файлы не трогаются.

Если папка проекта внутри репозитория, а не в его корне, добавь `--inside-repo`.

### Шаг 3. Установить и заполнить

```bash
python <AgentsFlower>/.agentsflower/tools/install.py /path/to/project
```

Затем открой сессию в проекте (Claude Code, VS Code, любой инструмент) и попроси её закончить установку — выбери папку для worktree вне облачной синхронизации, например `D:\tmp` или `~/worktrees`:

```text
AgentsFlower is installed in .agentsflower/. Finish the install:
.agentsflower/docs/ai-handoff-protocol.md, section "Installing or updating AgentsFlower", "Install".
Worktrees folder: <your worktrees folder>.
```

Сессия заполняет `.agentsflower/docs/project-rules.md` (основная ветка, папка worktree, `## Preflight`, `## Tool routing`) и `.agentsflower/docs/project-plan.md` под твой проект; `python .agentsflower/tools/ledger.py show` создаёт реестр задач; один commit. Если инструмент сообщит, что тестовый конфиг по умолчанию может уйти на staging или прод, — это решение за тобой: установщик его не меняет.

## A2. Несколько репозиториев

Workspace — одна папка с несколькими продуктовыми репозиториями (например `code/` с `backend/` и `web/`). AgentsFlower ставится в корень workspace, который сам становится маленьким git-репозиторием, хранящим только файлы AgentsFlower и корневые указатели; продуктовые репозитории не трогаются.

```bash
python <AgentsFlower>/.agentsflower/tools/install.py /path/to/code --workspace --git-init --dry-run
python <AgentsFlower>/.agentsflower/tools/install.py /path/to/code --workspace --git-init
```

После этого проверь: в корне появились `.git` (репозиторий памяти), `.agentsflower/workspace.json` со списком продуктовых репозиториев (по умолчанию — вложенные папки со своим `.git`; другой список: `--repos a,b`) и `.gitignore`, который не исключает нужные AgentsFlower папки (где нужно, добавляется отрицание `!/<папка>`; своё можно открыть такой же строкой вне блока). Закоммить `git add -A && git commit -m "chore: install AgentsFlower"` в репозитории памяти и закончи шаг 3 варианта [A](#a-установить).

В Task File появляется поле `Repo:` (какие репозитории может менять задача), а пути в `Allowed files`, `Do not touch` и `## Checks` начинаются с папки репозитория: `web/src/...`. Каждая задача получает одну папку-worktree с отдельным worktree на каждый затрагиваемый репозиторий. Приёмка сливает ветку с тем же именем в основную ветку каждого затронутого репозитория.

## B. Обновить

```bash
python <AgentsFlower>/.agentsflower/tools/install.py /path/to/project --update --dry-run
python <AgentsFlower>/.agentsflower/tools/install.py /path/to/project --update
```

Обновление заменяет файлы шаблона и откажется работать, пока у них есть незакоммиченные правки; файлы, которые проект сам положил в `.agentsflower/`, показываются в отчёте и сохраняются. Память (`.agentsflower/state/`, Task Files, правила проекта, runbook) никогда не перезаписывается. В сессии Claude Code:

```text
AgentsFlower was updated in .agentsflower/. Finish the update:
.agentsflower/docs/ai-handoff-protocol.md, section "Installing or updating AgentsFlower", "Update".
```

После этого: `.agentsflower/VERSION` новая, миграционные заметки промежуточных записей CHANGELOG применены к открытым Task Files и реестру, в `decisions.md` появилась датированная запись, один commit.

## C. Переход со старой раскладки

Версия 2.1 держала `docs/ai-handoff-protocol.md`, `tools/gate.py` и `tasks/` в корне репозитория. Установщик отказывается работать с такой раскладкой и просит сначала перенести свои файлы в `.agentsflower/`, после чего запускается обычная установка. Раскладка памяти 2.1 переходит в `.agentsflower/state/` и `.agentsflower/docs/`; в 2.1 не было `roles/`, `commands/` и `dashboard/`.

## D. Установить из пакета

Репозиторий также собирает локальный дистрибутив `agentsflower-sdlc` (установка из исходников — на PyPI под этим именем его нет):

```bash
python -m pip install build          # инструментарий разработки, один раз
python -m build                      # пишет dist/agentsflower_sdlc-<ver>-py3-none-any.whl и .tar.gz
python -m pip install dist/agentsflower_sdlc-*.whl
agentsflower --version                  # совпадает с .agentsflower/VERSION
```

Wheel содержит весь шаблон установщика в `agentsflower/template/`, поэтому команда `agentsflower` работает из любой папки:

```bash
agentsflower install <project> [--update] [--dry-run] [--inside-repo] [--workspace] [--repos a,b] [--git-init] [--mcp [--mcp-client claude|cursor]]
agentsflower run T-NNN --role <developer|tester|deployer> [--project <dir>]
agentsflower gate <task|preflight|endcheck|verify|stage> <args> [--project <dir>]
agentsflower done T-NNN [--project <dir>]
agentsflower accept T-NNN [--project <dir>]
agentsflower ledger <add|set|approve|show> [--project <dir>]
agentsflower mcp [--enable-orchestrator-tools] [--project <dir>]
agentsflower hooks <args> [--project <dir>]
agentsflower dashboard [--open] [--project <dir>]
```

`--project` принимает любую папку внутри проекта: команда поднимается до установленного `.agentsflower` и запускает собственные скрипты этого проекта. Без пакета у каждой подкоманды есть прямой эквивалент: `python .agentsflower/tools/<tool>.py` из корня проекта.

## E. MCP-сервер (необязательно)

`.agentsflower/tools/mcp_server.py` отдаёт состояние проекта по Model Context Protocol через stdio. Нужен официальный SDK — опциональное дополнение, основным инструментам он не нужен:

```bash
python -m pip install "agentsflower-sdlc[mcp]"   # или: python -m pip install "mcp>=2.3,<3"
python .agentsflower/tools/mcp_server.py         # или: agentsflower mcp
```

Инструменты по умолчанию (только чтение): `agentflow_status`, `agentflow_get_task`, `agentflow_query_ledger`, плюс `agentflow_run_gate`, который вызывает настоящий `gate.py`. `agentflow_accept_task` существует только за явным флагом оператора `--enable-orchestrator-tools`. Флаг определяет поверхность сервера; он не доказывает роль вызывающего — что доступно серверу, то и вызовет любой, кто до него достучится.

Подключить клиента в конфиг проекта — перезапустить установщик с явным флагом:

```bash
python .agentsflower/tools/install.py <project> --update --mcp                    # Claude Code: .mcp.json
python .agentsflower/tools/install.py <project> --update --mcp --mcp-client cursor  # Cursor: .cursor/mcp.json
```

`--mcp` добавляет запись `agentsflower`, не трогая чужие ключи и другие серверы, указывает её на установленный в проекте сервер с выключенными привилегированными инструментами и откажется при битом файле или неуправляемой конфликтующей записи `agentsflower`, ничего не записав.

## F. Ресурсы машины (по желанию)

Общее расписание машины — сколько слотов инструментов эта машина предлагает проектам AgentsFlower — включается на каждой машине отдельно. `machine_capacity.py` ведёт реестр (`registry.json`, общий для всех проектов одного пользователя ОС; `AGENTFLOW_MACHINE_STATE_DIR` перенаправляет его) проектов, занявших слот. Если ничего не настраивать, всё выше работает как есть: для запуска исполнителя грант не нужен.

Межпроектная диспетчеризация имеет три режима под `AGENTFLOW_SHARED_DISPATCHER` (по умолчанию `off`): `shadow` добавляет в отчёт `tick.py run` read-only превью честного распределения (`dispatchShadow`) — `dispatch.py` моделирует его, ничего не запуская; `active` заставляет сторожа каждого проекта публиковать готовые задачи и запрашивать короткий грант, который лаунчер обменивает на обычную машинную аренду (`run_task.py --dispatch-grant <token>`). Включай `active`, только когда все участвующие проекты обновлены до этой версии — старые лаунчеры не резервируют под гранты.

Наблюдаемые лимиты инструментов записываются по *квота-группам*, а не по CLI: опция в `model-options.json` помечает биллинг-группу провайдера через `quota_group`, холд хранится под `<tool>:<group>` и блокирует только сессии этой группы (голый `<tool>` блокирует все). Объявленные квота-*ожидания* — необязательные файлы проекта: `.agentsflower/docs/quota-policy.json` (`AGENTFLOW_QUOTA_POLICY` переопределяет, `off` выключает) хранит `{"policies": [{"tool", "group"?, "remaining": {"percent_below": n}, "action": "pause|switch|report", "sample_max_age_seconds"?}]}`, а `quota-samples.json` рядом (`AGENTFLOW_QUOTA_SAMPLES` переопределяет) хранит замеры под ключами `<tool>` или `<tool>:<group>`. Без свежего замера состояние `unknown`, и ничего не блокируется — файл выражает пожелание, а не гарантию, что процент соблюдается.

Хелперы `conductor.ps1` / `conductor-panel.ps1` (автоматические круги оркестратора и автозапуск на этой машине) — **только для Windows**: PowerShell и Планировщик заданий. Сторож и запускаемые им фоновые сессии оркестратора работают скрыто: без окна консоли, кнопки на панели задач и перехвата фокуса; видимой остаётся только сама панель. Они не часть основного процесса и на Linux или macOS никогда не нужны.

Пользователям TypeSafe AI: `.agentsflower/docs/typesafe.md` содержит ссылки на официальную документацию и правила, по которым `route.py` выбирает инструмент и модель.

---

# Часть 2. Работа каждый день

## Кто что делает

| Сессия | Запускается | Что делает |
|---|---|---|
| Оркестратор | `/start-role orchestrator` | дробит цель на Task Files, запускает исполнителей, принимает по доказательствам; единственный писатель памяти проекта |
| Разработчик / Тестировщик / Деплоер | `python .agentsflower/tools/run_task.py T-NNN <tool>` (обычно запускает оркестратор) | по одной задаче в свежей сессии; пишет только `## Result` |
| Без роли (Single Mode) | `/start-session` | делает всё сам, включая обновление памяти |

Оркестратор может запускать и через CLI: `agentsflower run T-NNN --role developer` читает поле `Tool:` из Task File и отказывает, если `--role` не совпадает с файлом. Задачи деплоера всегда запускаются с `--manual`: лаунчер готовит попытку, человек стартует инструмент — деплоер никогда не работает без присмотра.

## Жизненный цикл исполнителя

1. `run_task.py T-NNN <tool>` создаёт worktree `worktrees/<repo>-t-NNN-slug` и ветку `t-NNN-slug`, прогоняет preflight-гейт (правила запрета, владение файлами, состояние реестра), записывает попытку и запускает инструмент с промптом задачи — фоновым процессом без окна.
2. Исполнитель делает задачу, прогоняет свои `## Checks` дословно, делает один commit `[T-NNN] <type>: <what>` и заполняет `## Result` в Task File — в основной папке, никогда в копии внутри worktree.
3. Когда попытка завершается, конечная проверка убеждается, что worktree чист, а Task File в основной папке получил Result.
4. Оркестратор запускает `python .agentsflower/tools/gate.py verify T-NNN` — команды `## Checks` выполняются дословно — и при успехе принимает через `python .agentsflower/tools/accept.py T-NNN` (verify, слияние, реестр `done`, удаление worktree и ветки).

Управление зависшей или ручной попыткой:

```bash
python .agentsflower/tools/run_task.py --status          # состояние последней попытки каждой задачи
python .agentsflower/tools/run_task.py T-NNN --stop      # убить всё дерево процессов зависшего исполнителя
python .agentsflower/tools/run_task.py T-NNN --mark-finished  # ручная (--manual) попытка закончилась
python .agentsflower/tools/run_task.py T-NNN --recheck   # повторить конечную проверку после исправления её причины
python .agentsflower/tools/run_task.py --watchdog        # остановить каждую просроченную не-ручную попытку (можно указать T-NNN)
```

## Проверки при запуске и рамки исполнителя

Перед стартом исполнителя лаунчер проверяет (ошибка отклоняет запуск с объяснимой причиной; ничего не стартует):

- **Допуск по маршрутизации**: `python .agentsflower/tools/route.py T-NNN` должен был оставить рабочую запись `assessment` в `.agentsflower/tasks/.runtime/T-NNN.route.json`, совпадающую с текущим `requirementsHash` задачи, и инструмент/модель/effort, к которым сводится запуск — после переопределений `AGENTFLOW_<TOOL>_ARGS` — должны по-прежнему соответствовать записанному требованию. Отсутствующая, устаревшая или не-`ok` запись отклоняет запуск; строка заголовка `Routing exception: <причина>` — аудируемое решение человека в обход.
- **Исполняемый файл и бесплатный пробник доступа**: CLI инструмента существует (`AGENTFLOW_<TOOL>` переопределяет поиск; `AGENTFLOW_<TOOL>_ARGS` добавляет машинные флаги) и отвечает на бесплатный пробник доступа к аккаунту (`AGENTFLOW_<TOOL>_PROBE` переопределяет встроенный; `off` объявляет проверку неподдерживаемой и отклоняет запуск без присмотра).
- **Пробник выбранной модели (по желанию)**: `AGENTFLOW_<TOOL>_MODEL_PROBE=on` запускает ограниченную встроенную проверку выбранной модели инференсом — она может тратить токены, засчитываются только аудированные встроенные проверки, и доступ к аккаунту сам по себе никогда не доказывает право на модель.
- **Наблюдаемые лимиты и ёмкость**: нет живого холда `<tool>`/`<tool>:<group>` и свободна машинная аренда слота/PORT (см. [F. Ресурсы машины](#f-ресурсы-машины-по-желанию)).

Каждый управляемый исполнитель работает **неинтерактивно** под настенными часами лаунчера: `AGENTFLOW_WORKER_TIMEOUT` секунд (по умолчанию 1200; невалидное или пустое значение оставляет умолчание — управляемый исполнитель никогда не бесконечен). `--watchdog` (его сторож вызывает каждый круг) останавливает просроченную попытку снаружи тем же защищённым путём, что и `--stop`. Дальнейшие рамки автономии, каждая отклоняет новую попытку с записанной причиной: `AGENTFLOW_MAX_ATTEMPTS` (8), `AGENTFLOW_TASK_TIMEOUT` (4 ч от первой попытки), `AGENTFLOW_MAX_IDENTICAL_FAILURES` (3), `AGENTFLOW_MAX_TOOL_SWITCHES` (3). Запуск внутри рабочего чекаута другого исполнителя — вложенный помощник и отклоняется, если только правило Preflight не скажет `- delegate: on`. На Windows ограниченный исполнитель также держит запрос на исполнение против автоматического сна по простою (`power_guard.py`, на POSIX — пустышка). Интерактивная работа — это `--manual` попытка в твоей собственной сессии, её сторож не трогает.

Единственная проверка завершённости — `python .agentsflower/tools/gate.py done T-NNN` (`agentsflower done`): обязательные критерии в `pass`, `## Checks` проходят на артефакте и на пробном слиянии с текущей базой — ещё привязанный PASS переиспользуется, а не перемеряется. Необязательный адаптер Codex Stop-хука (`python .agentsflower/tools/hooks.py enable codex`, затем с `--write`) прогоняет ту же проверку при завершении сессии Codex; он сначала проверяет установленную версию Codex, остаётся совещательным и бездействует внутри управляемого исполнителя.

Статус выводится из записей, а не дублируется вручную: `--status`, `tick.py status` и дашборд читают файлы попыток и реестр; `handoff.md` остаётся авторской заметкой, которую пишет сессия.

## Наблюдение за ходом работ

```bash
python .agentsflower/dashboard/build.py          # пишет .agentsflower/dashboard/out/index.html, graph.html и roadmap.html
python .agentsflower/dashboard/build.py --demo   # те же страницы из детерминированной фикстуры, помечено DEMO DATA
agentsflower dashboard --open                    # собрать и открыть index.html; остальные страницы связаны в шапке
```

Дашборд только для чтения и ничего не выдумывает: статусы, роли и вердикты берутся из реестра и Task Files; панель метрик (first-pass gate rate, lead time, счёт вердиктов) считается только по записанным данным — отсутствующая история, время или стоимость показываются как N/A, никогда как ноль или выдуманная выгода. `--demo` существует для скриншотов и проверки вёрстки: он не читает память проекта и пишет только в `out/`. Интерфейс дашборда английский.

Страница roadmap (`out/roadmap.html`) показывает каждый `### Stage` файла `.agentsflower/docs/project-plan.md` в исходном порядке — объявленный статус, счётчики локальных задач и доказательства критериев как три отдельных факта — плюс карточку диагностики. Существующий план менять не нужно; необязательный авторский синтаксис `evidence:`/`Recurring:`/`References:` для покрытия по критериям описан в `.agentsflower/dashboard/README.md`. Перед изменением исходников дашборда сохрани локальную версию: `python .agentsflower/dashboard/snapshot.py save "<что>"`, откат — `snapshot.py restore vN` (какие исходники покрываются, перечислено в том же README).

## Восстановление

- Мёртвая или завершившаяся ошибкой попытка записывается на задачу в `.agentsflower/tasks/.runtime/T-NNN.json`; реестр остаётся `in progress`, пока оркестратор не решит. Каждая попытка заканчивается классифицированным `stopReason` (`completed`, `limit`, `timeout`, `stopped`, `dead`, `environment`, `verification`, `implementation`), а незавершившаяся попытка несёт ещё и ограниченную запись `recovery` на каждый чекаут — ветка, HEAD, отслеживаемые изменения и неотслеживаемые пути (только пути и статус, никогда содержимое файлов) — так что преемник, запущенный по тому же Task File, продолжает с сохранённого черновика. `Resume: <sha>` оставляет worktree и его черновики; `Resume: start fresh` их отбрасывает. Не повторяй неудачный путь, записанный в `.agentsflower/state/known-issues.md`.
- `gate.py verify`, упавший на `completed` Result, означает отклонение задачи: оркестратор пишет преемный Task File с находками — он никогда не правит код исполнителя сам.
- `blocked` Result возвращается оркестратору с вопросом исполнителя.
- Изоляция проверки: тестировщик работает в одноразовом чекауте коммита `Verifies` и ничего не меняет; после его попытки лаунчер проверяет, что ветка, worktree и Task File не тронуты.

## Границы доступа (что поддерживается)

- Исполнители меняют только файлы из `Allowed files`; правила запрета Preflight из `.agentsflower/docs/project-rules.md` (`## Preflight`) применяются `gate.py` перед запуском.
- Для Claude Code разреши только лаунчер — не весь проект:

  ```json
  { "permissions": { "allow": [ "PowerShell(.\\.agentsflower\\tools\\run-task.ps1:*)", "Bash(python .agentsflower/tools/run_task.py:*)" ] } }
  ```

- argv исполнителя фиксирован по инструменту и роли — неперечисленная комбинация отклоняет запуск, а не тихо понижает: Codex `exec --sandbox danger-full-access` (разработчик) или `--sandbox workspace-write` с сетью (тестировщик); Claude `-p` с `--dangerously-skip-permissions` (разработчик) или `--allowedTools Read,Grep,Glob,Bash,Edit` (тестировщик); `agy -p --output-format stream-json`, с добавлением `--dangerously-skip-permissions` для разработчика — каждый управляемый agy-исполнитель, включая тестировщика, это неинтерактивный print-режим, а не чат, ждущий `/exit`; Devin `-p --permission-mode dangerous --respect-workspace-trust false` для обеих ролей — свежий worktree не доверен, и ни один исполнитель не отвечает на запросы подтверждения, а опциональный пробник модели использует более слабый `--permission-mode auto` (пробник ничего не пишет). Только Antigravity IDE остаётся человеко-ведомой, как `--manual` попытка.
- Изоляция — это git worktree и проверки после попытки, а не универсальная песочница: Codex работает в песочнице (`danger-full-access` для разработчика, `workspace-write` для тестировщика), каждый другой инструмент проверяется после попытки. На Windows песочница Codex может отказать в записях, которые исполнителю законно нужны — Result-файл вне чекаута, временные папки для Python — и сделать Codex непригодным для задач исполнителей на этой машине; отдай задачу другому инструменту. Не полагайся на один лаунчер против записей вне `Allowed files` — проверяй конечной проверкой.
- Ни один инструмент не может push, слияние в main или выкладку: слияния принадлежат `accept.py` оркестратора, выкладка — сессии деплоера, которая начинается только после твоего явного «да».

## Если что-то пошло не так

- Строка реестра по задаче — источник правды о её состоянии: `python .agentsflower/tools/ledger.py show`.
- Полный тестовый набор шаблона: `python -m unittest discover -s .agentsflower/tests` (только stdlib, офлайн). Пакетная и MCP-интеграции запускаются явно: `python .agentsflower/tests/check_package.py`, `python .agentsflower/tests/check_mcp.py`.
- Доказательства по платформам: `.agentsflower/docs/release-validation.md` записывает, какие ячейки ОС/Python реально проверены; локальный зелёный прогон никогда не значит зелёный прогон на macOS.
