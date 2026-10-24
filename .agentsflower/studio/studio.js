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
    openTabs: [],
    chatModel: 'swe-2-high',
  };

  const CHAT_MODELS = [
    { id: 'swe-2-high', label: 'Devin swe-2-high', note: 'Floor default' },
    { id: 'gemini-4-argon-high', label: 'Gemini 4 Argon High', note: 'gemini-4-argon-high' },
    { id: 'claude-opus-4-6-thinking', label: 'Claude Opus 4.6 Thinking', note: 'claude-opus-4-6-thinking' },
    { id: 'gpt-5-5-high', label: 'GPT-5.5 High', note: 'gpt-5-5-high' },
    { id: 'local-ollama', label: 'Local / Ollama Model', note: 'Offline zero-token' },
  ];

  const PANE_LIMITS = {
    sidebar: { min: 200, max: 450, key: 'af_sidebar_width' },
    chat: { min: 320, max: 650, key: 'af_chat_width' },
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
  const globalSearchInput = document.getElementById('globalSearchInput');
  const stageFilterBtns = document.querySelectorAll('.pill-btn');
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
  const explorerBreadcrumbs = document.getElementById('explorerBreadcrumbs');
  const explorerCodeView = document.getElementById('explorerCodeView');
  const explorerStatusBar = document.getElementById('explorerStatusBar');
  const inspectorTaskSelect = document.getElementById('inspectorTaskSelect');
  const explorerGrid = document.getElementById('explorerGrid');
  const editorTabsBar = document.getElementById('editorTabsBar');
  const sidebarEl = document.querySelector('.sidebar');
  const sidebarResizer = document.getElementById('sidebarResizer');
  const chatResizer = document.getElementById('chatResizer');

  // Chat Cockpit Elements
  const chatStream = document.getElementById('chatStream');
  const chatInput = document.getElementById('chatInput');
  const btnChatSend = document.getElementById('btnChatSend');
  const btnChatNew = document.getElementById('btnChatNew');
  const btnChatPlus = document.getElementById('btnChatPlus');
  const btnChatRefresh = document.getElementById('btnChatRefresh');
  const chatModelPill = document.getElementById('chatModelPill');
  const chatModelSelector = document.getElementById('chatModelSelector');
  const chatModelDropdown = document.getElementById('chatModelDropdown');

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
    setupPaneSplitters();
    setupModelSelector();
    renderAllowedTags();
    renderCriteriaList();
    await loadProjects();
    updateProjectChrome();
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

    // Chat cockpit: task select, composer, header controls
    if (inspectorTaskSelect) {
      inspectorTaskSelect.addEventListener('change', () => {
        state.inspectorTaskId = inspectorTaskSelect.value;
        renderInspector();
      });
    }
    if (btnChatSend) btnChatSend.addEventListener('click', sendChatMessage);
    if (chatInput) {
      chatInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
          e.preventDefault();
          sendChatMessage();
        }
      });
    }
    if (btnChatNew) btnChatNew.addEventListener('click', () => switchTab('creator'));
    if (btnChatPlus) btnChatPlus.addEventListener('click', () => switchTab('creator'));
    if (btnChatRefresh) {
      btnChatRefresh.addEventListener('click', async () => {
        invalidateTreeCache(state.currentProject);
        await loadTasks(state.currentProject);
        renderProjectAccordion();
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
      if (state.currentProject) state.expandedProjects.add(state.currentProject);
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
    state.expandedProjects.add(path);
    closeDrawer();
    renderProjectAccordion();
    updateProjectChrome();
    resetExplorerPane();
    await Promise.all([loadStatus(path), loadTasks(path)]);
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
      const nameHtml = p.has_framework
        ? `${escapeHTML(p.name)} <span class="acc-ver">- v${escapeHTML(String(p.version))} (${p.task_count} tasks)</span>`
        : escapeHTML(p.name);
      const caretPts = isOpen ? '6 9 12 15 18 9' : '18 15 12 9 6 15';
      item.innerHTML = `
        <div class="project-acc-header">
          <span class="project-acc-box"></span>
          <span class="project-acc-name" title="${escapeHTML(p.path)}">${nameHtml}${p.is_current ? '<span class="star">\u2605</span>' : ''}</span>
          ${p.has_framework ? '' : '<span class="uninit-badge">Uninitialized</span>'}
          <svg class="project-acc-caret" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="${caretPts}"/></svg>
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

  // --- File Tree (sidebar accordion + explorer) ---
  function treeKey(projPath, rel) { return `${projPath}::${rel || ''}`; }

  function ftIconFor(e) {
    const FOLDER = '<path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V7z"/>';
    const DOC = '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/>';
    const GIT = '<circle cx="6" cy="6" r="3"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="6" r="3"/><line x1="6" y1="9" x2="6" y2="15"/><path d="M18 9a9 9 0 0 1-9 9"/>';
    let tint = 'file';
    let glyph = DOC;
    if (e.type === 'dir') {
      tint = e.name === '.agentsflower' ? 'tint-agentsflower'
        : e.name === '.claude' ? 'tint-claude' : 'dir';
      glyph = FOLDER;
    } else if (/^\.git(ignore|attributes|modules)$/.test(e.name)) {
      tint = 'tint-git';
      glyph = GIT;
    } else if (/\.(md|markdown)$/i.test(e.name)) {
      tint = 'tint-doc';
    }
    return `<svg class="ft-icon ${tint}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">${glyph}</svg>`;
  }

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
        ${ftIconFor(e)}
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

  // --- Draggable pane splitters ---
  function clamp(v, min, max) { return Math.min(max, Math.max(min, v)); }

  function applyChatWidth(w) {
    if (explorerGrid) {
      explorerGrid.style.gridTemplateColumns = `minmax(0, 1fr) 10px ${w}px`;
    }
  }

  function bindResizer(resizerEl, limits, measure, apply) {
    if (!resizerEl) return;
    resizerEl.addEventListener('mousedown', (e) => {
      e.preventDefault();
      let last = null;
      const onMove = (ev) => {
        last = clamp(Math.round(measure(ev)), limits.min, limits.max);
        apply(last);
      };
      const onUp = () => {
        document.removeEventListener('mousemove', onMove);
        document.removeEventListener('mouseup', onUp);
        resizerEl.classList.remove('dragging');
        document.body.classList.remove('pane-resizing');
        if (last !== null) {
          try { localStorage.setItem(limits.key, String(last)); } catch (err) { /* localStorage unavailable */ }
        }
      };
      resizerEl.classList.add('dragging');
      document.body.classList.add('pane-resizing');
      document.addEventListener('mousemove', onMove);
      document.addEventListener('mouseup', onUp);
    });
  }

  function restorePaneWidths() {
    try {
      const sb = parseInt(localStorage.getItem(PANE_LIMITS.sidebar.key), 10);
      if (sidebarEl && Number.isFinite(sb)) {
        sidebarEl.style.width = `${clamp(sb, PANE_LIMITS.sidebar.min, PANE_LIMITS.sidebar.max)}px`;
      }
      const cw = parseInt(localStorage.getItem(PANE_LIMITS.chat.key), 10);
      if (Number.isFinite(cw)) {
        applyChatWidth(clamp(cw, PANE_LIMITS.chat.min, PANE_LIMITS.chat.max));
      }
    } catch (err) { /* localStorage unavailable */ }
  }

  function setupPaneSplitters() {
    restorePaneWidths();
    bindResizer(sidebarResizer, PANE_LIMITS.sidebar,
      (ev) => ev.clientX - sidebarEl.getBoundingClientRect().left,
      (w) => { sidebarEl.style.width = `${w}px`; });
    bindResizer(chatResizer, PANE_LIMITS.chat,
      (ev) => {
        const chatPane = explorerGrid.querySelector('.explorer-chat-pane');
        return chatPane.getBoundingClientRect().right - ev.clientX;
      },
      applyChatWidth);
  }

  // --- IDE Explorer: breadcrumbs, code viewer ---
  function resetExplorerPane() {
    state.explorerPath = '';
    state.openTabs = [];
    renderEditorTabs();
    if (explorerBreadcrumbs) explorerBreadcrumbs.innerHTML = '<span class="crumb-leaf">Select a file to preview its contents</span>';
    if (explorerCodeView) explorerCodeView.innerHTML = '<div class="code-empty">Click a file in the workspace tree to inspect it here.</div>';
    if (explorerStatusBar) explorerStatusBar.textContent = 'Ready';
  }

  async function openExplorerFile(projPath, rel) {
    if (!rel) return;
    if (projPath !== state.currentProject) {
      await switchProject(projPath);
    }
    state.explorerPath = rel;
    const tabKey = treeKey(projPath, rel);
    if (!state.openTabs.some(t => t.key === tabKey)) {
      state.openTabs.push({ key: tabKey, proj: projPath, rel, name: rel.split('/').pop() });
    }
    renderEditorTabs();
    renderExplorerBreadcrumbs(projPath, rel);
    explorerCodeView.innerHTML = '<div class="code-empty">Loading...</div>';
    const res = await fetchJSON(`/api/file/read?project=${encodeURIComponent(projPath)}&path=${encodeURIComponent(rel)}`);
    if (res && res.ok) {
      const ext = rel.includes('.') ? rel.split('.').pop().toLowerCase() : '';
      const lines = res.content.split('\n');
      explorerCodeView.innerHTML = lines.map((line, i) =>
        `<div class="cl"><span class="ln">${i + 1}</span><span class="lc">${highlightCode(line, ext) || '&nbsp;'}</span></div>`
      ).join('');
      explorerStatusBar.textContent = `${rel}  ·  ${lines.length} lines  ·  ${res.size} bytes${res.truncated ? '  ·  truncated to 256 KB' : ''}`;
    } else {
      explorerCodeView.innerHTML = `<div class="code-empty">${escapeHTML(res && res.error ? res.error : 'Unable to read file')}</div>`;
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
      html += `<span class="crumb-sep">&gt;</span>`;
      html += i === segs.length - 1
        ? `<span class="crumb-leaf">${escapeHTML(s)}</span>`
        : `<span class="crumb" data-dir="${escapeHTML(dirPath)}">${escapeHTML(s)}</span>`;
    });
    if (segs.length > 1) {
      html += `<span class="crumb-sep">&gt;</span><span class="crumb" data-dir="${escapeHTML(segs.slice(0, -1).join('/'))}">..</span>`;
    }
    explorerBreadcrumbs.innerHTML = html;
    explorerBreadcrumbs.querySelectorAll('.crumb').forEach(c => {
      c.addEventListener('click', () => revealDirInTree(projPath, c.dataset.dir));
    });
  }

  async function revealDirInTree(projPath, dirRel) {
    const parts = (dirRel || '').split('/').filter(Boolean);
    let acc = '';
    parts.forEach(seg => {
      acc = acc ? `${acc}/${seg}` : seg;
      state.openDirs.add(treeKey(projPath, acc));
    });
    renderProjectAccordion();
  }

  // --- Editor file tabs bar ---
  function renderEditorTabs() {
    if (!editorTabsBar) return;
    editorTabsBar.innerHTML = '';
    const activeKey = state.explorerPath ? treeKey(state.currentProject, state.explorerPath) : '';
    state.openTabs.forEach(t => {
      const tab = document.createElement('div');
      tab.className = `editor-tab${t.key === activeKey ? ' active' : ''}`;
      tab.title = t.rel;
      tab.innerHTML = `
        ${ftIconFor({ type: 'file', name: t.name })}
        <span class="editor-tab-name">${escapeHTML(t.name)}</span>
        <button type="button" class="editor-tab-close" title="Close tab">&times;</button>`;
      tab.addEventListener('click', () => openExplorerFile(t.proj, t.rel));
      tab.querySelector('.editor-tab-close').addEventListener('click', (ev) => {
        ev.stopPropagation();
        closeFileTab(t.key);
      });
      editorTabsBar.appendChild(tab);
    });
  }

  function closeFileTab(key) {
    const idx = state.openTabs.findIndex(t => t.key === key);
    if (idx === -1) return;
    const removed = state.openTabs.splice(idx, 1)[0];
    if (removed.rel === state.explorerPath && removed.proj === state.currentProject) {
      const next = state.openTabs[idx - 1] || state.openTabs[state.openTabs.length - 1];
      if (next) {
        openExplorerFile(next.proj, next.rel);
      } else {
        resetExplorerPane();
      }
    }
    renderEditorTabs();
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

  // --- Task Inception & Chat Cockpit ---
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

  function chatToolLabel(t) {
    const toolNames = { devin: 'Devin', claude: 'Claude', codex: 'Codex', agy: 'Gemini' };
    const toolName = toolNames[(t.tool || '').toLowerCase()] || (t.tool ? t.tool : 'Devin');
    return t.model ? `${toolName} ${t.model}` : `${toolName} swe-2-high`;
  }

  function execStatusText(t) {
    const status = (t.status || '').toLowerCase();
    const base = `\u0417\u0430\u0434\u0430\u0447\u0430 ${t.id}: ${t.title}`;
    if (status === 'in progress') return `${base} \u2014 \u0443\u0441\u043f\u0435\u0448\u043d\u043e \u0440\u0430\u0437\u0431\u043b\u043e\u043a\u0438\u0440\u043e\u0432\u0430\u043d\u0430, \u0443\u0442\u0432\u0435\u0440\u0436\u0434\u0435\u043d\u0430 \u0432 \u0440\u0435\u0435\u0441\u0442\u0440\u0435 \u0438 \u0437\u0430\u043f\u0443\u0449\u0435\u043d\u0430 \u043d\u0430 \u0438\u0441\u043f\u043e\u043b\u043d\u0435\u043d\u0438\u0435!`;
    if (status === 'review') return `${base} \u2014 \u0438\u0441\u043f\u043e\u043b\u043d\u0435\u043d\u0438\u0435 \u0437\u0430\u0432\u0435\u0440\u0448\u0435\u043d\u043e, \u0430\u0440\u0442\u0435\u0444\u0430\u043a\u0442 \u043f\u0435\u0440\u0435\u0434\u0430\u043d \u043d\u0430 \u043d\u0435\u0437\u0430\u0432\u0438\u0441\u0438\u043c\u0443\u044e \u043f\u0440\u043e\u0432\u0435\u0440\u043a\u0443!`;
    if (status === 'done') return `${base} \u2014 \u043f\u0440\u043e\u0432\u0435\u0440\u043a\u0430 \u043f\u0440\u043e\u0439\u0434\u0435\u043d\u0430, \u0440\u0435\u0437\u0443\u043b\u044c\u0442\u0430\u0442 \u043f\u0440\u0438\u043d\u044f\u0442 \u0438 \u0441\u043b\u0438\u0442 \u0432 main!`;
    return `${base} \u2014 \u0443\u0442\u0432\u0435\u0440\u0436\u0434\u0435\u043d\u0430 \u0432 \u0440\u0435\u0435\u0441\u0442\u0440\u0435 \u0438 \u0433\u043e\u0442\u043e\u0432\u0430 \u043a \u0437\u0430\u043f\u0443\u0441\u043a\u0443!`;
  }

  function renderInspector() {
    if (!chatStream) return;
    const t = state.tasks.find(x => x.id === state.inspectorTaskId);
    if (!t) {
      chatStream.innerHTML = '<div class="empty-state"><p>No task selected or no tasks in this workspace.</p></div>';
      return;
    }
    const toolLabel = chatToolLabel(t);
    updateChatModelPill();
    const running = (t.status || '').toLowerCase() === 'in progress';
    const statusLabel = running ? 'RUNNING Attempt 1' : String(t.status || 'ready').toUpperCase();
    const workedDetail = running
      ? 'Gate preflight: pass\nContract locked\nAttempt 1 in progress'
      : 'Gate preflight: pass\nContract locked\nAttempt history in .runtime/';
    chatStream.innerHTML = `
      <div class="chat-bubble user">\u043f\u0440\u0438\u0441\u0442\u0443\u043f\u0430\u0439 \u043a ${escapeHTML(t.id)}</div>
      <div class="chat-worked" id="chatWorked"><span class="chat-worked-caret">&#8250;</span><span>Worked for 2m</span></div>
      <div class="chat-worked-detail" id="chatWorkedDetail" style="display:none">${escapeHTML(workedDetail)}</div>
      <div class="chat-exec-card">
        <div class="exec-status-text">${escapeHTML(execStatusText(t))}</div>
        <div class="exec-meta">
          <div class="exec-meta-row"><span class="k">Task ID</span><span class="v">${escapeHTML(t.id)}</span></div>
          <div class="exec-meta-row"><span class="k">Role</span><span class="v">${escapeHTML(t.role || '\u2014')}</span></div>
          <div class="exec-meta-row"><span class="k">Tool</span><span class="v">${escapeHTML(toolLabel)}</span></div>
          <div class="exec-meta-row"><span class="k">Worktree</span><span class="v">${escapeHTML(t.worktree || '\u2014')}</span></div>
          <div class="exec-meta-row"><span class="k">Status</span><span class="v${running ? ' running' : ''}">${escapeHTML(statusLabel)}</span></div>
        </div>
        <div class="exec-diff" id="execDiff">
          <div class="exec-diff-summary" id="execDiffSummary">
            <span id="execDiffText">loading diff...</span>
            <span class="diff-badge add" id="execDiffAdd">+0</span>
            <span class="diff-badge del" id="execDiffDel">-0</span>
            <span class="diff-caret">&#8250;</span>
          </div>
          <div class="exec-diff-files" id="execDiffFiles"></div>
        </div>
      </div>`;
    const workedEl = document.getElementById('chatWorked');
    const workedDetailEl = document.getElementById('chatWorkedDetail');
    if (workedEl && workedDetailEl) {
      workedEl.addEventListener('click', () => {
        const open = workedDetailEl.style.display === 'none';
        workedDetailEl.style.display = open ? 'block' : 'none';
        workedEl.classList.toggle('open', open);
      });
    }
    const diffEl = document.getElementById('execDiff');
    const diffSummaryEl = document.getElementById('execDiffSummary');
    if (diffEl && diffSummaryEl) {
      diffSummaryEl.addEventListener('click', () => diffEl.classList.toggle('open'));
    }
    chatStream.scrollTop = 0;
    loadInspectorGit();
  }

  async function loadInspectorGit() {
    const textEl = document.getElementById('execDiffText');
    const addEl = document.getElementById('execDiffAdd');
    const delEl = document.getElementById('execDiffDel');
    const filesEl = document.getElementById('execDiffFiles');
    if (!textEl || !addEl || !delEl || !filesEl) return;
    const res = await fetchJSON(`/api/project/git?project=${encodeURIComponent(state.currentProject)}`);
    if (!textEl.isConnected) return;
    let files = [];
    let adds = 0;
    let dels = 0;
    if (res && res.ok && res.is_git) {
      const m = (res.diffstat || '').match(/(\d+)\s+files?\s+changed(?:,\s*(\d+)\s+insertions?\(\+\))?(?:,\s*(\d+)\s+deletions?\(-\))?/);
      if (m) {
        adds = parseInt(m[2] || '0', 10);
        dels = parseInt(m[3] || '0', 10);
      }
      files = (res.changed || []).map(l => l.replace(/^[ MADRCU?!]{1,3}/, '').trim()).filter(Boolean).slice(0, 30);
      const n = files.length || (m ? parseInt(m[1], 10) : 0);
      textEl.textContent = `${n} file${n === 1 ? '' : 's'} changed`;
    } else if (res && res.ok) {
      textEl.textContent = 'not a git repository';
    } else {
      textEl.textContent = 'diff unavailable';
    }
    addEl.textContent = `+${adds}`;
    delEl.textContent = `-${dels}`;
    filesEl.innerHTML = files.length
      ? files.map(f => `<span class="diff-file" data-path="${escapeHTML(f)}" title="${escapeHTML(f)}">${escapeHTML(f)}</span>`).join('')
      : '<span class="diff-file-none">No uncommitted changes vs HEAD.</span>';
    filesEl.querySelectorAll('.diff-file').forEach(el => {
      el.addEventListener('click', () => openExplorerFile(state.currentProject, el.dataset.path));
    });
  }

  function sendChatMessage() {
    if (!chatInput || !chatStream) return;
    const text = chatInput.value.trim();
    if (!text) return;
    const bubble = document.createElement('div');
    bubble.className = 'chat-bubble user';
    bubble.textContent = text;
    chatStream.appendChild(bubble);
    chatInput.value = '';
    chatStream.scrollTop = chatStream.scrollHeight;
  }

  // --- Chat model selector ---
  function currentChatModel() {
    return CHAT_MODELS.find(m => m.id === state.chatModel) || CHAT_MODELS[0];
  }

  function updateChatModelPill() {
    if (!chatModelPill) return;
    const m = currentChatModel();
    chatModelPill.innerHTML = `${escapeHTML(m.label)} <span class="model-caret">&#8963;</span>`;
    chatModelPill.title = `Chat model: ${m.label}`;
  }

  function renderModelDropdown() {
    if (!chatModelDropdown) return;
    chatModelDropdown.innerHTML = '';
    CHAT_MODELS.forEach(m => {
      const opt = document.createElement('button');
      opt.type = 'button';
      opt.className = `model-option${m.id === state.chatModel ? ' active' : ''}`;
      opt.setAttribute('role', 'menuitem');
      opt.innerHTML = `<span>${escapeHTML(m.label)}</span><span class="model-id">${escapeHTML(m.note)}</span>`;
      opt.addEventListener('click', (ev) => {
        ev.stopPropagation();
        state.chatModel = m.id;
        try { sessionStorage.setItem('af_chat_model', m.id); } catch (err) { /* storage unavailable */ }
        updateChatModelPill();
        renderModelDropdown();
        chatModelSelector.classList.remove('open');
      });
      chatModelDropdown.appendChild(opt);
    });
  }

  function setupModelSelector() {
    if (!chatModelSelector || !chatModelPill) return;
    try {
      const saved = sessionStorage.getItem('af_chat_model');
      if (saved && CHAT_MODELS.some(m => m.id === saved)) state.chatModel = saved;
    } catch (err) { /* storage unavailable */ }
    updateChatModelPill();
    renderModelDropdown();
    chatModelPill.addEventListener('click', (ev) => {
      ev.stopPropagation();
      chatModelSelector.classList.toggle('open');
    });
    document.addEventListener('click', (ev) => {
      if (!chatModelSelector.contains(ev.target)) {
        chatModelSelector.classList.remove('open');
      }
    });
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
