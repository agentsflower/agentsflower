/**
 * AgentsFlower Studio Frontend Controller
 * Pure Vanilla JS, high-performance, real-time autonomous SDLC cockpit.
 */

document.addEventListener('DOMContentLoaded', () => {
  // Application State
  const state = {
    currentTab: 'kanban',
    currentStage: 'all',
    currentProject: '',
    searchQuery: '',
    tasks: [],
    projects: [],
    quotas: [],
    selectedTask: null,
    allowedFiles: ['.agentsflower/tools/*.py'],
    criteria: [
      'All unit tests pass without regressions: python -m unittest discover -s .agentsflower/tests',
      'Clean git status and verification gate approval.'
    ],
    analyticsSubTab: 'index',
  };

  // DOM Elements
  const appVersionEl = document.getElementById('appVersion');
  const projectSelectEl = document.getElementById('projectSelect');
  const projectActiveDot = document.getElementById('projectActiveDot');
  const uninitProjectBanner = document.getElementById('uninitProjectBanner');
  const btnInstallFramework = document.getElementById('btnInstallFramework');
  const navItems = document.querySelectorAll('.nav-item');
  const viewPanels = document.querySelectorAll('.view-panel');
  const activeTabTitle = document.getElementById('activeTabTitle');
  const globalSearchInput = document.getElementById('globalSearchInput');
  const stageFilterBtns = document.querySelectorAll('.pill-btn');
  const breadcrumbStudio = document.getElementById('breadcrumbStudio');
  const brandHomeBtn = document.getElementById('brandHomeBtn');

  // Stats Elements
  const statTotal = document.getElementById('statTotal');
  const statInProgress = document.getElementById('statInProgress');
  const statReview = document.getElementById('statReview');
  const statDone = document.getElementById('statDone');
  const taskTotalBadge = document.getElementById('taskTotalBadge');

  // Kanban Columns
  const colReadyCards = document.getElementById('colReadyCards');
  const colProgressCards = document.getElementById('colProgressCards');
  const colReviewCards = document.getElementById('colReviewCards');
  const colDoneCards = document.getElementById('colDoneCards');
  const countReady = document.getElementById('countReady');
  const countProgress = document.getElementById('countProgress');
  const countReview = document.getElementById('countReview');
  const countDone = document.getElementById('countDone');

  // Drawer Elements
  const taskDrawer = document.getElementById('taskDrawer');
  const taskDrawerOverlay = document.getElementById('taskDrawerOverlay');
  const btnDrawerClose = document.getElementById('btnDrawerClose');
  const drawerTaskId = document.getElementById('drawerTaskId');
  const drawerTaskTitle = document.getElementById('drawerTaskTitle');
  const drawerBody = document.getElementById('drawerBody');

  // Graft Elements
  const graftQueryInput = document.getElementById('graftQueryInput');
  const btnRunGraftQuery = document.getElementById('btnRunGraftQuery');
  const btnRunGraftImpact = document.getElementById('btnRunGraftImpact');
  const btnGraftRefresh = document.getElementById('btnGraftRefresh');
  const graftResultsContainer = document.getElementById('graftResultsContainer');

  // Task Contract Creator Elements
  const createTaskForm = document.getElementById('createTaskForm');
  const btnQuickCreate = document.getElementById('btnQuickCreate');
  const btnCancelCreate = document.getElementById('btnCancelCreate');
  const inputAllowedFile = document.getElementById('inputAllowedFile');
  const btnAddAllowedFile = document.getElementById('btnAddAllowedFile');
  const allowedTagsContainer = document.getElementById('allowedTagsContainer');
  const criteriaListBuilder = document.getElementById('criteriaListBuilder');
  const btnAddCriterion = document.getElementById('btnAddCriterion');

  // Project Modals
  const btnOpenAttachModal = document.getElementById('btnOpenAttachModal');
  const modalAttachBackdrop = document.getElementById('modalAttachBackdrop');
  const btnCloseAttachModal = document.getElementById('btnCloseAttachModal');
  const btnCancelAttach = document.getElementById('btnCancelAttach');
  const btnConfirmAttach = document.getElementById('btnConfirmAttach');
  const inputAttachPath = document.getElementById('inputAttachPath');

  const btnOpenCreateModal = document.getElementById('btnOpenCreateModal');
  const modalCreateBackdrop = document.getElementById('modalCreateBackdrop');
  const btnCloseCreateModal = document.getElementById('btnCloseCreateModal');
  const btnCancelScaffold = document.getElementById('btnCancelScaffold');
  const btnConfirmScaffold = document.getElementById('btnConfirmScaffold');
  const inputCreatePath = document.getElementById('inputCreatePath');

  // Analytics Elements
  const analyticsFrame = document.getElementById('analyticsFrame');
  const btnRebuildDashboard = document.getElementById('btnRebuildDashboard');
  const btnOpenExternalDashboard = document.getElementById('btnOpenExternalDashboard');
  const subTabButtons = document.querySelectorAll('.btn-subtab');

  // --- API Client ---
  async function fetchJSON(url, options = {}) {
    try {
      const res = await fetch(url, options);
      if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
      return await res.json();
    } catch (err) {
      console.error(`API Fetch failed for ${url}:`, err);
      return null;
    }
  }

  // --- Initialize App ---
  async function init() {
    setupEventListeners();
    renderAllowedTags();
    renderCriteriaList();
    await loadProjects();
    await loadStatus();
    await loadTasks();
    await loadQuotas();
  }

  // --- Event Listeners ---
  function setupEventListeners() {
    // Navigation Tabs
    navItems.forEach(item => {
      item.addEventListener('click', () => {
        const tab = item.dataset.tab;
        switchTab(tab);
      });
    });

    // Home / Board Shortcuts
    if (breadcrumbStudio) breadcrumbStudio.addEventListener('click', () => switchTab('kanban'));
    if (brandHomeBtn) brandHomeBtn.addEventListener('click', () => switchTab('kanban'));
    if (btnCancelCreate) btnCancelCreate.addEventListener('click', () => switchTab('kanban'));

    // Quick Create Button in Topbar
    if (btnQuickCreate) {
      btnQuickCreate.addEventListener('click', () => {
        switchTab('creator');
      });
    }

    // Stage Filters
    stageFilterBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        stageFilterBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        state.currentStage = btn.dataset.stage;
        renderKanban();
      });
    });

    // Search Filter
    globalSearchInput.addEventListener('input', (e) => {
      state.searchQuery = e.target.value.toLowerCase().trim();
      renderKanban();
    });

    // Task Drawer Close
    btnDrawerClose.addEventListener('click', closeDrawer);
    taskDrawerOverlay.addEventListener('click', closeDrawer);

    // Graft Actions
    btnRunGraftQuery.addEventListener('click', handleGraftQuery);
    btnRunGraftImpact.addEventListener('click', handleGraftImpact);
    btnGraftRefresh.addEventListener('click', handleGraftRefresh);
    graftQueryInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') handleGraftQuery();
    });

    // Project Switcher
    projectSelectEl.addEventListener('change', async () => {
      state.currentProject = projectSelectEl.value;
      await loadStatus(state.currentProject);
      await loadTasks(state.currentProject);
    });

    // Framework Install on uninit banner
    if (btnInstallFramework) {
      btnInstallFramework.addEventListener('click', async () => {
        if (!state.currentProject) return;
        btnInstallFramework.disabled = true;
        btnInstallFramework.textContent = 'Initializing AgentsFlower...';
        const res = await fetchJSON('/api/project/create', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ path: state.currentProject })
        });
        btnInstallFramework.disabled = false;
        btnInstallFramework.textContent = 'Initialize AgentsFlower (v2.17.0)';
        if (res && res.ok) {
          alert('AgentsFlower successfully installed in workspace!');
          await loadProjects();
          await loadStatus(state.currentProject);
          await loadTasks(state.currentProject);
        } else {
          alert(`Error initializing: ${res ? res.error : 'Unknown error'}`);
        }
      });
    }

    // Attach Project Modal
    if (btnOpenAttachModal) btnOpenAttachModal.addEventListener('click', () => { modalAttachBackdrop.style.display = 'flex'; });
    if (btnCloseAttachModal) btnCloseAttachModal.addEventListener('click', () => { modalAttachBackdrop.style.display = 'none'; });
    if (btnCancelAttach) btnCancelAttach.addEventListener('click', () => { modalAttachBackdrop.style.display = 'none'; });
    if (btnConfirmAttach) {
      btnConfirmAttach.addEventListener('click', async () => {
        const pathVal = inputAttachPath.value.trim();
        if (!pathVal) return;
        btnConfirmAttach.disabled = true;
        btnConfirmAttach.textContent = 'Attaching...';
        const res = await fetchJSON('/api/project/attach', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ path: pathVal })
        });
        btnConfirmAttach.disabled = false;
        btnConfirmAttach.textContent = 'Attach Workspace';
        if (res && res.ok) {
          modalAttachBackdrop.style.display = 'none';
          inputAttachPath.value = '';
          await loadProjects();
          state.currentProject = pathVal;
          projectSelectEl.value = pathVal;
          await loadStatus(pathVal);
          await loadTasks(pathVal);
        } else {
          alert(`Could not attach project: ${res ? res.error : 'Directory invalid'}`);
        }
      });
    }

    // Scaffold New Project Modal
    if (btnOpenCreateModal) btnOpenCreateModal.addEventListener('click', () => { modalCreateBackdrop.style.display = 'flex'; });
    if (btnCloseCreateModal) btnCloseCreateModal.addEventListener('click', () => { modalCreateBackdrop.style.display = 'none'; });
    if (btnCancelScaffold) btnCancelScaffold.addEventListener('click', () => { modalCreateBackdrop.style.display = 'none'; });
    if (btnConfirmScaffold) {
      btnConfirmScaffold.addEventListener('click', async () => {
        const pathVal = inputCreatePath.value.trim();
        if (!pathVal) return;
        btnConfirmScaffold.disabled = true;
        btnConfirmScaffold.textContent = 'Scaffolding...';
        const res = await fetchJSON('/api/project/create', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ path: pathVal })
        });
        btnConfirmScaffold.disabled = false;
        btnConfirmScaffold.textContent = 'Scaffold Project';
        if (res && res.ok) {
          modalCreateBackdrop.style.display = 'none';
          inputCreatePath.value = '';
          alert('New AgentsFlower project successfully scaffolded!');
          await loadProjects();
          state.currentProject = pathVal;
          projectSelectEl.value = pathVal;
          await loadStatus(pathVal);
          await loadTasks(pathVal);
        } else {
          alert(`Error scaffolding project: ${res ? res.error : 'Directory error'}`);
        }
      });
    }

    // Creator Interactive List Events
    if (btnAddAllowedFile) {
      btnAddAllowedFile.addEventListener('click', () => {
        const val = inputAllowedFile.value.trim();
        if (val) {
          addAllowedFile(val);
          inputAllowedFile.value = '';
        }
      });
    }
    if (inputAllowedFile) {
      inputAllowedFile.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
          e.preventDefault();
          const val = inputAllowedFile.value.trim();
          if (val) {
            addAllowedFile(val);
            inputAllowedFile.value = '';
          }
        }
      });
    }

    // Quick Path Chips
    document.querySelectorAll('[data-add-path]').forEach(btn => {
      btn.addEventListener('click', () => {
        addAllowedFile(btn.dataset.addPath);
      });
    });

    // Quick Criteria Chips
    document.querySelectorAll('[data-add-crit]').forEach(btn => {
      btn.addEventListener('click', () => {
        addCriterion(btn.dataset.addCrit);
      });
    });

    // Add Criterion Button
    if (btnAddCriterion) {
      btnAddCriterion.addEventListener('click', () => {
        addCriterion('');
      });
    }

    // Analytics Sub-tabs
    subTabButtons.forEach(btn => {
      btn.addEventListener('click', () => {
        subTabButtons.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        state.analyticsSubTab = btn.dataset.sub;
        updateAnalyticsFrame();
      });
    });

    // Rebuild Analytics
    if (btnRebuildDashboard) {
      btnRebuildDashboard.addEventListener('click', async () => {
        btnRebuildDashboard.disabled = true;
        btnRebuildDashboard.innerHTML = '<span>Rebuilding...</span>';
        const res = await fetchJSON('/api/dashboard/build', { method: 'POST' });
        btnRebuildDashboard.disabled = false;
        btnRebuildDashboard.innerHTML = `
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M23 4v6h-6"/><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/></svg>
          <span>Rebuild Analytics</span>
        `;
        if (res && res.ok) {
          updateAnalyticsFrame(true);
        } else {
          alert('Analytics rebuild error: ' + (res ? res.error : 'Unknown error'));
        }
      });
    }

    // Task Creator Form Submit
    createTaskForm.addEventListener('submit', handleTaskCreate);
  }

  // --- Switch Tabs ---
  function switchTab(tabName) {
    state.currentTab = tabName;
    navItems.forEach(item => {
      item.classList.toggle('active', item.dataset.tab === tabName);
    });
    viewPanels.forEach(panel => {
      panel.classList.toggle('active', panel.id === `view-${tabName}`);
    });

    const titleMap = {
      kanban: 'Task Board',
      analytics: 'Analytics & Roadmap',
      graft: 'Knowledge Graph & Blast Radius',
      capacity: 'Model Quota & Dispatch Hub',
      creator: 'Task Contract Generator',
      guide: 'Quick Start & Protocol Cockpit',
    };
    activeTabTitle.textContent = titleMap[tabName] || 'Studio';
  }

  // --- Analytics Sub-tab Frame Updater ---
  function updateAnalyticsFrame(forceReload = false) {
    if (!analyticsFrame) return;
    const pathMap = {
      index: '/dashboard/out/index.html',
      graph: '/dashboard/out/graph.html',
      roadmap: '/dashboard/out/roadmap.html',
    };
    const targetUrl = pathMap[state.analyticsSubTab] || pathMap.index;
    const finalUrl = forceReload ? `${targetUrl}?ts=${Date.now()}` : targetUrl;
    analyticsFrame.src = finalUrl;
    if (btnOpenExternalDashboard) btnOpenExternalDashboard.href = targetUrl;
  }

  // --- Interactive Allowed Files Helpers ---
  function addAllowedFile(pathStr) {
    if (!state.allowedFiles.includes(pathStr)) {
      state.allowedFiles.push(pathStr);
      renderAllowedTags();
    }
  }

  function removeAllowedFile(idx) {
    state.allowedFiles.splice(idx, 1);
    renderAllowedTags();
  }

  function renderAllowedTags() {
    if (!allowedTagsContainer) return;
    allowedTagsContainer.innerHTML = '';
    if (state.allowedFiles.length === 0) {
      allowedTagsContainer.innerHTML = '<span style="font-size:0.78rem; color:var(--text-subtle); padding:4px;">No files specified (open scope or none)</span>';
      return;
    }
    state.allowedFiles.forEach((f, idx) => {
      const chip = document.createElement('div');
      chip.className = 'tag-chip';
      chip.innerHTML = `
        <span>${escapeHTML(f)}</span>
        <span class="tag-remove" title="Remove">&times;</span>
      `;
      chip.querySelector('.tag-remove').addEventListener('click', () => removeAllowedFile(idx));
      allowedTagsContainer.appendChild(chip);
    });
  }

  // --- Interactive Criteria List Helpers ---
  function addCriterion(text = '') {
    state.criteria.push(text);
    renderCriteriaList();
    const inputs = criteriaListBuilder.querySelectorAll('.criteria-input');
    if (inputs.length > 0) {
      inputs[inputs.length - 1].focus();
    }
  }

  function removeCriterion(idx) {
    if (state.criteria.length <= 1) {
      state.criteria = [''];
    } else {
      state.criteria.splice(idx, 1);
    }
    renderCriteriaList();
  }

  function syncCriteriaFromDOM() {
    const inputs = criteriaListBuilder.querySelectorAll('.criteria-input');
    state.criteria = Array.from(inputs).map(inp => inp.value);
  }

  function renderCriteriaList() {
    if (!criteriaListBuilder) return;
    criteriaListBuilder.innerHTML = '';
    state.criteria.forEach((text, idx) => {
      const numStr = String(idx + 1).padStart(2, '0');
      const item = document.createElement('div');
      item.className = 'criteria-item';
      item.innerHTML = `
        <span class="criteria-badge">C-${numStr}:</span>
        <input type="text" class="criteria-input" placeholder="Enter measurable acceptance criterion..." value="${escapeHTML(text)}">
        <button type="button" class="criteria-remove" title="Delete criterion">&times;</button>
      `;
      const input = item.querySelector('.criteria-input');
      input.addEventListener('input', () => {
        state.criteria[idx] = input.value;
      });
      item.querySelector('.criteria-remove').addEventListener('click', () => removeCriterion(idx));
      criteriaListBuilder.appendChild(item);
    });
  }

  // --- Load Status ---
  async function loadStatus(projPath = '') {
    const query = projPath ? `?project=${encodeURIComponent(projPath)}` : '';
    const data = await fetchJSON(`/api/status${query}`);
    if (data) {
      if (data.version && appVersionEl) {
        appVersionEl.textContent = `v${data.version}`;
      }
      if (uninitProjectBanner) {
        uninitProjectBanner.style.display = data.has_framework ? 'none' : 'flex';
      }
      if (projectActiveDot) {
        projectActiveDot.style.background = data.has_framework ? 'var(--accent-emerald)' : 'var(--accent-amber)';
      }
    }
  }

  // --- Load Projects ---
  async function loadProjects() {
    const res = await fetchJSON('/api/projects');
    if (res && res.projects) {
      state.projects = res.projects;
      projectSelectEl.innerHTML = '';
      res.projects.forEach(p => {
        const opt = document.createElement('option');
        opt.value = p.path;
        const taskInfo = p.has_framework ? ` (${p.task_count} tasks)` : ' [no flower]';
        opt.textContent = `${p.name} - v${p.version}${taskInfo}${p.is_current ? ' ★' : ''}`;
        if (p.is_current && !state.currentProject) {
          opt.selected = true;
          state.currentProject = p.path;
        }
        projectSelectEl.appendChild(opt);
      });
      if (state.currentProject) {
        projectSelectEl.value = state.currentProject;
      }
    }
  }

  // --- Load Tasks ---
  async function loadTasks(projPath = '') {
    const target = projPath || state.currentProject;
    const query = target ? `?project=${encodeURIComponent(target)}` : '';
    const res = await fetchJSON(`/api/tasks${query}`);
    if (res && res.data && res.data.tasks) {
      state.tasks = res.data.tasks;
      updateMetrics();
      renderKanban();
    } else {
      state.tasks = [];
      updateMetrics();
      renderKanban();
    }
  }

  // --- Load Quotas ---
  async function loadQuotas() {
    const res = await fetchJSON('/api/quotas');
    if (res && res.data && res.data.tools) {
      renderCapacityGrid(res.data.tools);
    }
  }

  // --- Metrics ---
  function updateMetrics() {
    const total = state.tasks.length;
    const progress = state.tasks.filter(t => t.status === 'in progress').length;
    const review = state.tasks.filter(t => t.status === 'review').length;
    const done = state.tasks.filter(t => t.status === 'done').length;

    statTotal.textContent = total;
    statInProgress.textContent = progress;
    statReview.textContent = review;
    statDone.textContent = done;
    taskTotalBadge.textContent = total;
  }

  // --- Render Kanban Board ---
  function renderKanban() {
    let filtered = state.tasks;
    if (state.currentStage !== 'all') {
      filtered = filtered.filter(t => String(t.stage) === state.currentStage);
    }
    if (state.searchQuery) {
      filtered = filtered.filter(t => 
        t.id.toLowerCase().includes(state.searchQuery) ||
        t.title.toLowerCase().includes(state.searchQuery) ||
        t.role.toLowerCase().includes(state.searchQuery) ||
        t.tool.toLowerCase().includes(state.searchQuery)
      );
    }

    colReadyCards.innerHTML = '';
    colProgressCards.innerHTML = '';
    colReviewCards.innerHTML = '';
    colDoneCards.innerHTML = '';

    const cols = {
      ready: [],
      'in progress': [],
      review: [],
      done: []
    };

    filtered.forEach(t => {
      const status = t.status.toLowerCase();
      if (cols[status]) {
        cols[status].push(t);
      } else {
        cols['ready'].push(t);
      }
    });

    countReady.textContent = cols['ready'].length;
    countProgress.textContent = cols['in progress'].length;
    countReview.textContent = cols['review'].length;
    countDone.textContent = cols['done'].length;

    cols['ready'].forEach(t => colReadyCards.appendChild(createTaskCard(t)));
    cols['in progress'].forEach(t => colProgressCards.appendChild(createTaskCard(t)));
    cols['review'].forEach(t => colReviewCards.appendChild(createTaskCard(t)));
    cols['done'].forEach(t => colDoneCards.appendChild(createTaskCard(t)));
  }

  // --- Create Task Card ---
  function createTaskCard(t) {
    const card = document.createElement('div');
    card.className = 'task-card';
    card.innerHTML = `
      <div class="task-card-header">
        <span class="task-tid">${t.id}</span>
        <span class="task-stage-badge">Stage ${t.stage}</span>
      </div>
      <div class="task-card-title">${escapeHTML(t.title)}</div>
      <div class="task-card-footer">
        <span class="task-role-tag">${t.role}</span>
        <span class="task-tool-tag">${t.tool || 'auto'}</span>
      </div>
    `;

    card.addEventListener('click', () => openTaskDrawer(t));
    return card;
  }

  // --- Task Detail Drawer ---
  function openTaskDrawer(t) {
    state.selectedTask = t;
    drawerTaskId.textContent = t.id;
    drawerTaskTitle.textContent = t.title;

    drawerBody.innerHTML = `
      <div>
        <div class="drawer-section-title">Contract Overview</div>
        <div class="metric-row" style="display:flex; justify-content:space-between; margin-bottom:8px;">
          <span style="color:var(--text-subtle)">Role:</span>
          <span style="font-weight:600">${t.role}</span>
        </div>
        <div class="metric-row" style="display:flex; justify-content:space-between; margin-bottom:8px;">
          <span style="color:var(--text-subtle)">Assigned Tool / Model:</span>
          <span style="font-weight:600">${t.tool || 'auto'}</span>
        </div>
        <div class="metric-row" style="display:flex; justify-content:space-between; margin-bottom:8px;">
          <span style="color:var(--text-subtle)">Stage:</span>
          <span style="font-weight:600">${t.stage}</span>
        </div>
        <div class="metric-row" style="display:flex; justify-content:space-between; margin-bottom:8px;">
          <span style="color:var(--text-subtle)">Status:</span>
          <span style="font-weight:700; text-transform:uppercase; color:var(--accent-emerald)">${t.status}</span>
        </div>
      </div>

      <div>
        <div class="drawer-section-title">Goal & Requirements</div>
        <div class="drawer-text" style="white-space:pre-wrap;">${escapeHTML(t.goal || 'No goal description in contract.')}</div>
      </div>

      <div>
        <div class="drawer-section-title">Allowed Files (Explicit Scope)</div>
        <div style="display:flex; flex-direction:column; gap:6px;">
          ${(t.allowed_files && t.allowed_files.length) ? t.allowed_files.map(f => `<code style="background:rgba(0,0,0,0.3); padding:4px 8px; border-radius:4px; font-family:var(--font-mono); font-size:0.8rem; color:#93c5fd;">${escapeHTML(f)}</code>`).join('') : '<span style="color:var(--text-subtle); font-size:0.85rem;">None specified</span>'}
        </div>
      </div>

      <div>
        <div class="drawer-section-title">Independent Verification Authority</div>
        <div class="drawer-text" style="font-size:0.82rem; color:var(--text-muted); background:rgba(255,255,255,0.02); padding:10px; border-radius:6px; border:1px solid var(--border-subtle);">
          Zero-Trust SDLC Policy: Status transitions to <strong>Done</strong> are cryptographically bound to committed tests and independent tester review.
        </div>
      </div>
    `;

    taskDrawer.classList.add('active');
    taskDrawerOverlay.classList.add('active');
  }

  function closeDrawer() {
    taskDrawer.classList.remove('active');
    taskDrawerOverlay.classList.remove('active');
  }

  // --- Graft Tree-sitter Queries ---
  async function handleGraftQuery() {
    const q = graftQueryInput.value.trim();
    if (!q) return;

    btnRunGraftQuery.disabled = true;
    btnRunGraftQuery.innerHTML = '<span>Querying AST...</span>';

    const res = await fetchJSON('/api/graft/query', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question: q, path_scope: '' })
    });

    btnRunGraftQuery.disabled = false;
    btnRunGraftQuery.innerHTML = `
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
      <span>Query AST</span>
    `;

    renderGraftOutput(res);
  }

  async function handleGraftImpact() {
    const q = graftQueryInput.value.trim();
    if (!q) {
      alert('Please enter a target function, class, or symbol name (e.g. "ledger" or "find_projects")');
      return;
    }

    btnRunGraftImpact.disabled = true;
    btnRunGraftImpact.innerHTML = '<span>Tracing callers...</span>';

    const res = await fetchJSON('/api/graft/impact', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ target: q })
    });

    btnRunGraftImpact.disabled = false;
    btnRunGraftImpact.innerHTML = `
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 20V10M12 20V4M6 20v-6"/></svg>
      <span>Blast Radius</span>
    `;

    renderGraftOutput(res);
  }

  async function handleGraftRefresh() {
    graftQueryInput.value = '';
    graftResultsContainer.innerHTML = `
      <div class="empty-state">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <circle cx="12" cy="12" r="10"/>
          <line x1="12" y1="16" x2="12" y2="12"/>
          <line x1="12" y1="8" x2="12.01" y2="8"/>
        </svg>
        <p>Ready to query AST. Enter a symbol, path, or natural language query above.</p>
      </div>
    `;
  }

  function renderGraftOutput(res) {
    if (!res) {
      graftResultsContainer.innerHTML = '<div style="color:#f87171; padding:16px;">Failed to reach Graft AST service.</div>';
      return;
    }

    const output = res.output || res.error || (res.matches ? JSON.stringify(res.matches, null, 2) : 'Query completed with no direct matches.');
    graftResultsContainer.innerHTML = `
      <div style="font-family:var(--font-mono); font-size:0.84rem; line-height:1.6; white-space:pre-wrap; color:#e2e8f0; max-height:400px; overflow-y:auto;">${escapeHTML(output)}</div>
    `;
  }

  // --- Render Capacity Grid ---
  function renderCapacityGrid(tools) {
    const grid = document.getElementById('toolsCapacityGrid');
    if (!grid) return;
    grid.innerHTML = '';

    tools.forEach(tool => {
      const card = document.createElement('div');
      card.className = 'capacity-item-card';
      card.innerHTML = `
        <div class="capacity-card-top">
          <span class="capacity-tool-title">${tool.label}</span>
          <span class="capacity-slots">${tool.slots}</span>
        </div>
        <div style="font-size:0.82rem; color:var(--text-subtle); margin-bottom:12px;">${tool.note}</div>
        <div style="display:flex; align-items:center; gap:6px; font-size:0.75rem;">
          <span class="status-indicator online"></span>
          <span style="color:var(--text-muted); text-transform:uppercase; font-weight:600">${tool.status}</span>
        </div>
      `;
      grid.appendChild(card);
    });
  }

  // --- Create Task Form Handler ---
  async function handleTaskCreate(e) {
    e.preventDefault();
    syncCriteriaFromDOM();

    const tid = document.getElementById('newTaskTid').value.trim();
    const title = document.getElementById('newTaskTitle').value.trim();
    const stage = document.getElementById('newTaskStage').value;
    const role = document.getElementById('newTaskRole').value;
    const tool = document.getElementById('newTaskTool').value;
    const goal = document.getElementById('newTaskGoal').value.trim();

    const allowed = state.allowedFiles.filter(Boolean);
    const criteria = state.criteria.filter(s => s && s.trim());

    const submitBtn = document.getElementById('btnSubmitTask');
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span>Registering...</span>';

    const res = await fetchJSON('/api/task/create', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        project: state.currentProject,
        id: tid,
        title: title,
        stage: stage,
        role: role,
        tool: tool,
        goal: goal,
        allowed: allowed,
        criteria: criteria,
      })
    });

    submitBtn.disabled = false;
    submitBtn.innerHTML = `
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
      <span>Generate Contract & Register in Ledger</span>
    `;

    if (res && res.ok) {
      alert(`Success! Task ${tid} contract generated and registered in ledger.`);
      createTaskForm.reset();
      state.allowedFiles = ['.agentsflower/tools/*.py'];
      state.criteria = [
        'All unit tests pass without regressions: python -m unittest discover -s .agentsflower/tests',
        'Clean git status and verification gate approval.'
      ];
      renderAllowedTags();
      renderCriteriaList();
      await loadTasks(state.currentProject);
      switchTab('kanban');
    } else {
      alert(`Error creating task: ${res ? res.error : 'Unknown server error'}`);
    }
  }

  // Utility
  function escapeHTML(str) {
    if (!str) return '';
    return str
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  // Boot
  init();
});
