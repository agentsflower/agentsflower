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
    currentProjectName: '',
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
    expandedProjects: new Set(),
    openDirs: new Set(),
    treeCache: {},
    explorerPath: '',
    inspectorTaskId: '',
    pendingInstall: null,
  };

  // DOM Elements
  const appVersionEl = document.getElementById('appVersion');
  const projectAccordionEl = document.getElementById('projectAccordion');
  const activeProjectChip = document.getElementById('activeProjectChip');
  const creatorTargetProject = document.getElementById('creatorTargetProject');
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

  // Explorer Elements
  const explorerFileTree = document.getElementById('explorerFileTree');
  const explorerBreadcrumbs = document.getElementById('explorerBreadcrumbs');
  const explorerCodeView = document.getElementById('explorerCodeView');
  const explorerStatusBar = document.getElementById('explorerStatusBar');
  const btnExplorerTreeRefresh = document.getElementById('btnExplorerTreeRefresh');
  const inspectorTaskSelect = document.getElementById('inspectorTaskSelect');
  const inspectorBody = document.getElementById('inspectorBody');

  // Authorization Gate Modal
  const modalAuthBackdrop = document.getElementById('modalAuthBackdrop');
  const btnCloseAuthModal = document.getElementById('btnCloseAuthModal');
  const btnCancelAuth = document.getElementById('btnCancelAuth');
  const btnConfirmAuth = document.getElementById('btnConfirmAuth');
  const authModalPath = document.getElementById('authModalPath');
  const authModalTitle = document.getElementById('authModalTitle');
  const authModalText = document.getElementById('authModalText');

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
    updateProjectChrome();
    await loadStatus();
    await loadTasks();
    await loadQuotas();
    loadExplorerTree();
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

    // Framework Install on uninit banner -> explicit authorization gate
    if (btnInstallFramework) {
      btnInstallFramework.addEventListener('click', () => {
        if (!state.currentProject) return;
        requestInstallAuthorization(state.currentProject, false);
      });
    }

    // Authorization Gate Modal
    const closeAuthModal = () => {
      modalAuthBackdrop.style.display = 'none';
      const pending = state.pendingInstall;
      state.pendingInstall = null;
      if (pending && pending.onCancel) pending.onCancel();
    };
    if (btnCloseAuthModal) btnCloseAuthModal.addEventListener('click', closeAuthModal);
    if (btnCancelAuth) btnCancelAuth.addEventListener('click', closeAuthModal);
    if (btnConfirmAuth) {
      btnConfirmAuth.addEventListener('click', async () => {
        if (!state.pendingInstall) return;
        const { path, isUpdate } = state.pendingInstall;
        btnConfirmAuth.disabled = true;
        btnConfirmAuth.textContent = 'Installing...';
        const endpoint = isUpdate ? '/api/project/update' : '/api/project/create';
        const res = await fetchJSON(endpoint, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ path: path, authorized: true, update: isUpdate })
        });
        btnConfirmAuth.disabled = false;
        btnConfirmAuth.textContent = 'Authorize & Install';
        modalAuthBackdrop.style.display = 'none';
        state.pendingInstall = null;
        if (res && res.ok) {
          alert('AgentsFlower successfully installed in workspace!');
          await loadProjects();
          await switchProject(canonicalProjectPath(path));
        } else {
          alert(`Error initializing: ${res ? res.error : 'Unknown error'}`);
        }
      });
    }

    // Explorer: refresh file tree + inspector task select
    if (btnExplorerTreeRefresh) {
      btnExplorerTreeRefresh.addEventListener('click', () => {
        invalidateTreeCache(state.currentProject);
        loadExplorerTree();
      });
    }
    if (inspectorTaskSelect) {
      inspectorTaskSelect.addEventListener('change', () => {
        state.inspectorTaskId = inspectorTaskSelect.value;
        renderInspector();
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
          await switchProject(canonicalProjectPath(pathVal));
        } else {
          alert(`Could not attach project: ${res ? res.error : 'Directory invalid'}`);
        }
      });
    }

    // Scaffold New Project Modal -> routed through the explicit authorization gate
    if (btnOpenCreateModal) btnOpenCreateModal.addEventListener('click', () => { modalCreateBackdrop.style.display = 'flex'; });
    if (btnCloseCreateModal) btnCloseCreateModal.addEventListener('click', () => { modalCreateBackdrop.style.display = 'none'; });
    if (btnCancelScaffold) btnCancelScaffold.addEventListener('click', () => { modalCreateBackdrop.style.display = 'none'; });
    if (btnConfirmScaffold) {
      btnConfirmScaffold.addEventListener('click', () => {
        const pathVal = inputCreatePath.value.trim();
        if (!pathVal) return;
        modalCreateBackdrop.style.display = 'none';
        requestInstallAuthorization(pathVal, false, () => {
          modalCreateBackdrop.style.display = 'flex';
        });
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
        const res = await fetchJSON('/api/dashboard/build', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ project: state.currentProject })
        });
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
      explorer: 'Explorer',
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
    const qs = [];
    if (state.currentProject) qs.push(`project=${encodeURIComponent(state.currentProject)}`);
    if (forceReload) qs.push(`ts=${Date.now()}`);
    const finalUrl = qs.length ? `${targetUrl}?${qs.join('&')}` : targetUrl;
    analyticsFrame.src = finalUrl;
    if (btnOpenExternalDashboard) btnOpenExternalDashboard.href = finalUrl;
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
      if (data.project) {
        state.currentProjectName = data.project;
      }
      if (uninitProjectBanner) {
        uninitProjectBanner.style.display = data.has_framework ? 'none' : 'flex';
      }
      if (btnInstallFramework && data.version) {
        btnInstallFramework.textContent = `Initialize AgentsFlower (v${data.version})`;
      }
      updateProjectChrome();
    }
  }

  // --- Load Projects ---
  async function loadProjects() {
    const res = await fetchJSON('/api/projects');
    if (res && res.projects) {
      state.projects = res.projects;
      if (!state.currentProject) {
        const curr = res.projects.find(p => p.is_current) || res.projects[0];
        if (curr) state.currentProject = curr.path;
      }
      const known = new Set(res.projects.map(p => p.path));
      state.expandedProjects = new Set([...state.expandedProjects].filter(p => known.has(p)));
      renderProjectAccordion();
      updateProjectChrome();
    }
  }

  // --- Load Tasks ---
  async function loadTasks(projPath = '') {
    const target = projPath || state.currentProject;
    const query = target ? `?project=${encodeURIComponent(target)}` : '';
    const res = await fetchJSON(`/api/tasks${query}`);
    if (res && res.data && res.data.tasks) {
      state.tasks = res.data.tasks;
    } else {
      state.tasks = [];
    }
    updateMetrics();
    renderKanban();
    populateInspectorTasks();
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
      body: JSON.stringify({ question: q, path_scope: '', project: state.currentProject })
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
      body: JSON.stringify({ target: q, project: state.currentProject })
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

  // --- Global Project Synchronization ---
  function canonicalProjectPath(pathVal) {
    const norm = s => (s || '').replace(/\\/g, '/').replace(/\/+$/, '').toLowerCase();
    const match = state.projects.find(p => norm(p.path) === norm(pathVal));
    return match ? match.path : pathVal;
  }

  async function switchProject(path) {
    if (!path || path === state.currentProject) {
      renderProjectAccordion();
      return;
    }
    state.currentProject = path;
    state.explorerPath = '';
    state.inspectorTaskId = '';
    closeDrawer();
    renderProjectAccordion();
    updateProjectChrome();
    resetExplorerPane();
    await Promise.all([loadStatus(path), loadTasks(path)]);
    loadExplorerTree();
    updateAnalyticsFrame();
  }

  function updateProjectChrome() {
    const proj = state.projects.find(p => p.path === state.currentProject);
    const name = (proj && proj.name) || state.currentProjectName || 'workspace';
    if (activeProjectChip) {
      activeProjectChip.textContent = `\u25C8 ${name}`;
      activeProjectChip.title = state.currentProject || name;
    }
    if (creatorTargetProject) creatorTargetProject.textContent = name;
  }

  // --- Sidebar Multi-Project Accordion ---
  function renderProjectAccordion() {
    if (!projectAccordionEl) return;
    projectAccordionEl.innerHTML = '';
    if (!state.projects.length) {
      projectAccordionEl.innerHTML = '<div class="accordion-loading">No workspaces found</div>';
      return;
    }
    state.projects.forEach(p => {
      const isActive = p.path === state.currentProject;
      const isOpen = state.expandedProjects.has(p.path);
      const item = document.createElement('div');
      item.className = `project-acc-item${isActive ? ' active' : ''}${p.has_framework ? '' : ' uninit'}${isOpen ? ' expanded' : ''}`;
      const meta = p.has_framework ? `<span class="project-acc-meta">v${escapeHTML(String(p.version))} · ${p.task_count}</span>` : '<span class="uninit-badge">Uninitialized</span>';
      item.innerHTML = `
        <div class="project-acc-header">
          <svg class="project-acc-chevron" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 18 15 12 9 6"/></svg>
          <span class="project-acc-dot"></span>
          <span class="project-acc-name" title="${escapeHTML(p.path)}">${escapeHTML(p.name)}${p.is_current ? '<span class="star">\u2605</span>' : ''}</span>
          ${meta}
        </div>
        <div class="project-acc-tree"${isOpen ? '' : ' style="display:none"'}></div>`;
      const header = item.querySelector('.project-acc-header');
      header.addEventListener('click', async () => {
        if (state.expandedProjects.has(p.path)) {
          state.expandedProjects.delete(p.path);
        } else {
          state.expandedProjects.add(p.path);
        }
        await switchProject(p.path);
      });
      projectAccordionEl.appendChild(item);
      if (isOpen) {
        const treeEl = item.querySelector('.project-acc-tree');
        treeEl.innerHTML = '<div class="ft-loading">loading...</div>';
        fetchTree(p.path, '').then(entries => renderTreeNodes(treeEl, p.path, entries));
      }
    });
  }

  // --- File Tree (shared by sidebar accordion and Explorer pane) ---
  function treeKey(projPath, rel) { return `${projPath}::${rel || ''}`; }

  async function fetchTree(projPath, rel) {
    const key = treeKey(projPath, rel);
    if (key in state.treeCache) return state.treeCache[key];
    const res = await fetchJSON(`/api/project/tree?project=${encodeURIComponent(projPath)}&path=${encodeURIComponent(rel || '')}`);
    const entries = (res && res.ok && res.entries) ? res.entries : null;
    state.treeCache[key] = entries;
    return entries;
  }

  function invalidateTreeCache(projPath) {
    const prefix = `${projPath}::`;
    Object.keys(state.treeCache).forEach(k => { if (k.startsWith(prefix)) delete state.treeCache[k]; });
  }

  async function loadDir(childrenEl, projPath, rel) {
    childrenEl.innerHTML = '<div class="ft-loading">loading...</div>';
    const entries = await fetchTree(projPath, rel);
    renderTreeNodes(childrenEl, projPath, entries);
  }

  function renderTreeNodes(container, projPath, entries) {
    container.innerHTML = '';
    if (!entries) {
      container.innerHTML = '<div class="ft-error">Unable to load folder</div>';
      return;
    }
    if (!entries.length) {
      container.innerHTML = '<div class="ft-loading">(empty)</div>';
      return;
    }
    entries.forEach(e => {
      const isDir = e.type === 'dir';
      const open = state.openDirs.has(treeKey(projPath, e.path));
      const node = document.createElement('div');
      const label = document.createElement('div');
      label.className = `ft-node-label${state.explorerPath === e.path ? ' selected' : ''}`;
      label.title = e.path;
      label.innerHTML = `
        <svg class="ft-caret${open ? ' open' : ''}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="${isDir ? '' : 'visibility:hidden'}"><polyline points="9 18 15 12 9 6"/></svg>
        <svg class="ft-icon ${isDir ? 'dir' : 'file'}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">${isDir
          ? '<path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V7z"/>'
          : '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/>'}</svg>
        <span class="ft-name">${escapeHTML(e.name)}</span>`;
      const childrenEl = document.createElement('div');
      childrenEl.className = 'ft-children';
      childrenEl.style.display = open ? 'block' : 'none';
      node.appendChild(label);
      node.appendChild(childrenEl);
      container.appendChild(node);
      const caret = label.querySelector('.ft-caret');
      if (open && isDir) loadDir(childrenEl, projPath, e.path);
      label.addEventListener('click', (ev) => {
        ev.stopPropagation();
        if (isDir) {
          const k = treeKey(projPath, e.path);
          const nowOpen = childrenEl.style.display === 'none';
          childrenEl.style.display = nowOpen ? 'block' : 'none';
          caret.classList.toggle('open', nowOpen);
          if (nowOpen) {
            state.openDirs.add(k);
            loadDir(childrenEl, projPath, e.path);
          } else {
            state.openDirs.delete(k);
          }
        } else {
          container.querySelectorAll('.ft-node-label.selected').forEach(el => el.classList.remove('selected'));
          label.classList.add('selected');
          openExplorerFile(projPath, e.path);
        }
      });
    });
  }

  // --- IDE Explorer: tree, breadcrumbs, code viewer ---
  async function loadExplorerTree() {
    if (!explorerFileTree || !state.currentProject) return;
    explorerFileTree.innerHTML = '<div class="ft-loading">loading...</div>';
    const entries = await fetchTree(state.currentProject, '');
    renderTreeNodes(explorerFileTree, state.currentProject, entries);
  }

  function resetExplorerPane() {
    if (explorerBreadcrumbs) explorerBreadcrumbs.innerHTML = '<span class="crumb-leaf">Select a file to preview its contents</span>';
    if (explorerCodeView) explorerCodeView.innerHTML = '<code class="code-empty">Click a file in the tree to inspect it here.</code>';
    if (explorerStatusBar) explorerStatusBar.textContent = 'Ready';
  }

  async function openExplorerFile(projPath, rel) {
    if (!rel) return;
    if (projPath !== state.currentProject) {
      await switchProject(projPath);
    }
    state.explorerPath = rel;
    renderExplorerBreadcrumbs(projPath, rel);
    explorerCodeView.innerHTML = '<code class="code-empty">Loading...</code>';
    const res = await fetchJSON(`/api/file/read?project=${encodeURIComponent(projPath)}&path=${encodeURIComponent(rel)}`);
    if (res && res.ok) {
      const ext = rel.includes('.') ? rel.split('.').pop().toLowerCase() : '';
      explorerCodeView.innerHTML = `<code>${highlightCode(res.content, ext)}</code>`;
      const lines = res.content.split('\n').length;
      explorerStatusBar.textContent = `${rel}  ·  ${lines} lines  ·  ${res.size} bytes${res.truncated ? '  ·  truncated to 256 KB' : ''}`;
    } else {
      explorerCodeView.innerHTML = `<code class="code-empty">${escapeHTML(res && res.error ? res.error : 'Unable to read file')}</code>`;
      explorerStatusBar.textContent = rel;
    }
    if (state.currentTab !== 'explorer') switchTab('explorer');
  }

  function renderExplorerBreadcrumbs(projPath, rel) {
    if (!explorerBreadcrumbs) return;
    const proj = state.projects.find(p => p.path === projPath);
    const name = (proj && proj.name) || 'workspace';
    const segs = rel.split('/').filter(Boolean);
    let html = `<span class="crumb" data-dir="">${escapeHTML(name)}</span>`;
    segs.forEach((s, i) => {
      const dirPath = segs.slice(0, i + 1).join('/');
      html += `<span class="crumb-sep">/</span>`;
      html += i === segs.length - 1
        ? `<span class="crumb-leaf">${escapeHTML(s)}</span>`
        : `<span class="crumb" data-dir="${escapeHTML(dirPath)}">${escapeHTML(s)}</span>`;
    });
    explorerBreadcrumbs.innerHTML = html;
    explorerBreadcrumbs.querySelectorAll('.crumb').forEach(c => {
      c.addEventListener('click', () => revealDirInTree(projPath, c.dataset.dir));
    });
  }

  async function revealDirInTree(projPath, dirRel) {
    if (!dirRel) {
      loadExplorerTree();
      return;
    }
    const parts = dirRel.split('/').filter(Boolean);
    let acc = '';
    parts.forEach(seg => {
      acc = acc ? `${acc}/${seg}` : seg;
      state.openDirs.add(treeKey(projPath, acc));
    });
    await loadExplorerTree();
  }

  // --- Lightweight syntax highlighting ---
  const HL_DEFS = {
    code: {
      com: String.raw`//[^\n]*|/\*[\s\S]*?\*/`,
      str: String.raw`"(?:\\.|[^"\\\n])*"|'(?:\\.|[^'\\\n])*'|` + '`(?:\\\\.|[^`\\\\])*`',
      kw: 'async|await|break|case|catch|class|const|continue|default|delete|do|else|export|extends|finally|for|from|function|if|import|in|instanceof|let|new|null|of|return|static|super|switch|this|throw|try|typeof|undefined|var|while|yield|true|false',
      kwBare: true,
    },
    py: {
      com: String.raw`#[^\n]*`,
      str: String.raw`"""[\s\S]*?"""|'''[\s\S]*?'''|"(?:\\.|[^"\\\n])*"|'(?:\\.|[^'\\\n])*'`,
      kw: 'and|as|assert|async|await|break|class|continue|def|del|elif|else|except|finally|for|from|global|if|import|in|is|lambda|nonlocal|not|or|pass|raise|return|self|try|while|with|yield|None|True|False|print',
      kwBare: true,
    },
    shell: {
      com: String.raw`#[^\n]*`,
      str: String.raw`"(?:\\.|[^"\\\n])*"|'(?:\\.|[^'\\\n])*'`,
      kw: 'begin|case|do|done|echo|elif|else|end|esac|exit|export|fi|for|function|if|in|local|param|process|return|then|while',
      kwBare: true,
    },
    markup: {
      com: String.raw`<!--[\s\S]*?-->`,
      str: String.raw`"[^"\n]*"|'[^'\n]*'`,
      kw: String.raw`</?[a-zA-Z][^>\n]*>`,
      kwBare: false,
    },
    md: {
      com: String.raw`<!--[\s\S]*?-->`,
      str: String.raw`` + '`[^`\\n]*`',
      kw: String.raw`#{1,6}[^\n]*`,
      kwBare: false,
    },
  };
  const HL_EXT = {
    js: 'code', jsx: 'code', ts: 'code', tsx: 'code', json: 'code', css: 'code',
    py: 'py', psm1: 'shell', ps1: 'shell', sh: 'shell', bash: 'shell',
    yml: 'shell', yaml: 'shell', toml: 'shell', ini: 'shell', cfg: 'shell',
    html: 'markup', htm: 'markup', xml: 'markup', svg: 'markup',
    md: 'md', markdown: 'md',
  };
  const HL_PATTERNS = {};
  function hlPattern(family) {
    if (!HL_PATTERNS[family]) {
      const d = HL_DEFS[family];
      const kw = d.kwBare ? `\\b(?:${d.kw})\\b` : d.kw;
      HL_PATTERNS[family] = new RegExp(`(${d.com})|(${d.str})|(\\b\\d+(?:\\.\\d+)?\\b)|(${kw})`, 'gm');
    }
    return HL_PATTERNS[family];
  }

  function highlightCode(src, ext) {
    const family = HL_EXT[ext];
    if (!family) return escapeHTML(src);
    const re = hlPattern(family);
    re.lastIndex = 0;
    let out = '';
    let last = 0;
    let m;
    while ((m = re.exec(src)) !== null) {
      if (m[0].length === 0) { re.lastIndex += 1; continue; }
      out += escapeHTML(src.slice(last, m.index));
      const cls = m[1] !== undefined ? 'tok-com'
        : m[2] !== undefined ? 'tok-str'
        : m[3] !== undefined ? 'tok-num'
        : (family === 'markup' ? 'tok-tag' : 'tok-kw');
      out += `<span class="${cls}">${escapeHTML(m[0])}</span>`;
      last = m.index + m[0].length;
    }
    return out + escapeHTML(src.slice(last));
  }

  // --- Task Context Inspector ---
  function populateInspectorTasks() {
    if (!inspectorTaskSelect) return;
    const prev = state.inspectorTaskId;
    inspectorTaskSelect.innerHTML = '';
    if (!state.tasks.length) {
      inspectorTaskSelect.innerHTML = '<option value="">No tasks in workspace</option>';
      state.inspectorTaskId = '';
      renderInspector();
      return;
    }
    const stillThere = state.tasks.some(t => t.id === prev);
    const pick = stillThere ? prev : (state.tasks.find(t => t.status === 'in progress') || state.tasks[0]).id;
    state.tasks.forEach(t => {
      const opt = document.createElement('option');
      opt.value = t.id;
      opt.textContent = `${t.id} \u2014 ${t.title}`;
      inspectorTaskSelect.appendChild(opt);
    });
    inspectorTaskSelect.value = pick;
    state.inspectorTaskId = pick;
    renderInspector();
  }

  function renderInspector() {
    if (!inspectorBody) return;
    const t = state.tasks.find(x => x.id === state.inspectorTaskId);
    if (!t) {
      inspectorBody.innerHTML = '<div class="empty-state"><p>No task selected or no tasks in this workspace.</p></div>';
      return;
    }
    const critHtml = (t.criteria && t.criteria.length)
      ? t.criteria.map(c => `
        <label class="criteria-check${c.done ? ' done' : ''}">
          <input type="checkbox" disabled${c.done ? ' checked' : ''}>
          <span><span class="cid">${escapeHTML(c.id)}:</span> ${escapeHTML(c.text)}</span>
        </label>`).join('')
      : '<div class="inspector-diffstat empty">No acceptance criteria in contract.</div>';
    const allowedHtml = (t.allowed_files && t.allowed_files.length)
      ? t.allowed_files.map(f => `<code style="background:rgba(0,0,0,0.3); padding:2px 6px; border-radius:4px; font-family:var(--font-mono); font-size:0.72rem; color:#93c5fd; display:inline-block; margin:2px 2px 2px 0;">${escapeHTML(f)}</code>`).join('')
      : '<span style="color:var(--text-subtle); font-size:0.8rem;">None specified</span>';
    inspectorBody.innerHTML = `
      <div>
        <div class="inspector-section-title">Contract Metadata</div>
        <div class="inspector-meta-row"><span class="k">Task</span><span class="v">${escapeHTML(t.id)}</span></div>
        <div class="inspector-meta-row"><span class="k">Role</span><span class="v">${escapeHTML(t.role)}</span></div>
        <div class="inspector-meta-row"><span class="k">Tool / Model</span><span class="v">${escapeHTML(t.tool || 'auto')}</span></div>
        <div class="inspector-meta-row"><span class="k">Stage</span><span class="v">${escapeHTML(String(t.stage))}</span></div>
        <div class="inspector-meta-row"><span class="k">Status</span><span class="v">${escapeHTML(t.status)}</span></div>
        <div class="inspector-meta-row"><span class="k">Commit</span><span class="v">${escapeHTML(t.commit || '\u2014')}</span></div>
      </div>
      <div>
        <div class="inspector-section-title">Acceptance Criteria</div>
        <div class="criteria-checklist">${critHtml}</div>
      </div>
      <div>
        <div class="inspector-section-title">Allowed Files</div>
        <div>${allowedHtml}</div>
      </div>
      <div>
        <div class="inspector-section-title">Git Diff Summary</div>
        <div class="inspector-diffstat" id="inspectorDiffstat"><span style="color:var(--text-subtle)">loading...</span></div>
      </div>`;
    loadInspectorGit();
  }

  async function loadInspectorGit() {
    const el = document.getElementById('inspectorDiffstat');
    if (!el) return;
    const res = await fetchJSON(`/api/project/git?project=${encodeURIComponent(state.currentProject)}`);
    if (!el.isConnected) return;
    if (res && res.ok && res.is_git) {
      const diff = res.diffstat && res.diffstat.trim() ? res.diffstat : 'No uncommitted changes vs HEAD.';
      const changedList = (res.changed && res.changed.length)
        ? `\n\nWorking tree (${res.changed.length}):\n${res.changed.slice(0, 30).join('\n')}`
        : '';
      el.textContent = `branch: ${res.branch}\n\n${diff}${changedList}`;
      el.classList.remove('empty');
    } else if (res && res.ok) {
      el.textContent = 'Not a git repository.';
      el.classList.add('empty');
    } else {
      el.textContent = (res && res.error) ? res.error : 'Git summary unavailable.';
      el.classList.add('empty');
    }
  }

  // --- Explicit Authorization Gate ---
  function requestInstallAuthorization(path, isUpdate = false, onCancel = null) {
    if (!path) return;
    state.pendingInstall = { path, isUpdate, onCancel };
    if (authModalTitle) {
      authModalTitle.textContent = isUpdate
        ? 'Update AgentsFlower in this workspace?'
        : 'Install AgentsFlower into this workspace?';
    }
    if (authModalText) {
      authModalText.innerHTML = `This runs <code>install.py${isUpdate ? ' --update' : ''}</code> and writes the AgentsFlower template into the target directory. Nothing is installed in the background &mdash; the operation starts only after your explicit confirmation.`;
    }
    if (authModalPath) authModalPath.textContent = path;
    modalAuthBackdrop.style.display = 'flex';
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
