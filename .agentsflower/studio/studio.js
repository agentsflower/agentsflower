/**
 * AgentsFlower Studio Frontend Controller
 * Pure Vanilla JS, high-performance, real-time SDLC cockpit.
 */

document.addEventListener('DOMContentLoaded', () => {
  // Application State
  const state = {
    currentTab: 'kanban',
    currentStage: 'all',
    searchQuery: '',
    tasks: [],
    projects: [],
    quotas: [],
    selectedTask: null,
  };

  // DOM Elements
  const appVersionEl = document.getElementById('appVersion');
  const projectSelectEl = document.getElementById('projectSelect');
  const navItems = document.querySelectorAll('.nav-item');
  const viewPanels = document.querySelectorAll('.view-panel');
  const activeTabTitle = document.getElementById('activeTabTitle');
  const globalSearchInput = document.getElementById('globalSearchInput');
  const stageFilterBtns = document.querySelectorAll('.pill-btn');

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

  // Creator Form
  const createTaskForm = document.getElementById('createTaskForm');
  const btnQuickCreate = document.getElementById('btnQuickCreate');

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
    await loadStatus();
    await loadProjects();
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

    // Task Creator Form
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

    // Update Topbar Title
    const titleMap = {
      kanban: 'Task Board',
      graft: 'Knowledge Graph & Blast Radius',
      capacity: 'Model Quota & Dispatch Hub',
      creator: 'Task Contract Generator',
    };
    activeTabTitle.textContent = titleMap[tabName] || 'Studio';
  }

  // --- Load Status ---
  async function loadStatus() {
    const data = await fetchJSON('/api/status');
    if (data && data.version) {
      appVersionEl.textContent = `v${data.version}`;
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
        opt.textContent = p.name + (p.is_current ? ' (Current)' : '');
        opt.selected = p.is_current;
        projectSelectEl.appendChild(opt);
      });
    }
  }

  // --- Load Tasks ---
  async function loadTasks() {
    const res = await fetchJSON('/api/tasks');
    if (res && res.data && res.data.tasks) {
      state.tasks = res.data.tasks;
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
    // Filter tasks
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

    // Clear columns
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
          <span class="badge" style="background:rgba(99,102,241,0.2); color:#c7d2fe">${t.status}</span>
        </div>
      </div>

      ${t.goal ? `
      <div>
        <div class="drawer-section-title">Goal</div>
        <p class="drawer-text" style="white-space:pre-wrap; background:rgba(0,0,0,0.25); padding:12px; border-radius:8px;">${escapeHTML(t.goal)}</p>
      </div>` : ''}

      ${t.allowed_files && t.allowed_files.length ? `
      <div>
        <div class="drawer-section-title">Allowed Files (${t.allowed_files.length})</div>
        <ul style="list-style:none; display:flex; flex-direction:column; gap:6px;">
          ${t.allowed_files.map(f => `<li style="font-family:var(--font-mono); font-size:0.8rem; background:rgba(255,255,255,0.03); padding:4px 8px; border-radius:4px;">${escapeHTML(f)}</li>`).join('')}
        </ul>
      </div>` : ''}

      ${t.commit ? `
      <div>
        <div class="drawer-section-title">Verified Commit</div>
        <div style="font-family:var(--font-mono); font-size:0.8rem; color:#a5b4fc">${t.commit}</div>
      </div>` : ''}

      <div style="margin-top:auto; padding-top:20px; display:flex; gap:10px;">
        <button class="btn btn-primary" onclick="alert('Worker dispatch for ${t.id} triggered via conductor.')">Launch Worker</button>
        <button class="btn btn-secondary" onclick="navigator.clipboard.writeText('${t.id}'); alert('Copied ID to clipboard');">Copy Task ID</button>
      </div>
    `;

    taskDrawerOverlay.classList.add('active');
    taskDrawer.classList.add('active');
  }

  function closeDrawer() {
    taskDrawerOverlay.classList.remove('active');
    taskDrawer.classList.remove('active');
  }

  // --- Graft AST Handlers ---
  async function handleGraftQuery() {
    const q = graftQueryInput.value.trim();
    if (!q) return;

    graftResultsContainer.innerHTML = '<span style="color:#a5b4fc">Querying Graft knowledge graph...</span>';
    const res = await fetchJSON('/api/graft/query', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question: q })
    });

    if (res && res.output) {
      graftResultsContainer.textContent = res.output;
    } else {
      graftResultsContainer.textContent = res && res.error ? `Error: ${res.error}` : 'No response from Graft.';
    }
  }

  async function handleGraftImpact() {
    const target = graftQueryInput.value.trim();
    if (!target) {
      alert('Enter a symbol name or file path to calculate blast radius impact.');
      return;
    }

    graftResultsContainer.innerHTML = '<span style="color:#a5b4fc">Calculating AST blast radius...</span>';
    const res = await fetchJSON('/api/graft/impact', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ target: target })
    });

    if (res && res.data) {
      graftResultsContainer.textContent = JSON.stringify(res.data, null, 2);
    } else if (res && res.raw) {
      graftResultsContainer.textContent = res.raw;
    } else {
      graftResultsContainer.textContent = res && res.error ? `Error: ${res.error}` : 'Impact analysis completed without data.';
    }
  }

  async function handleGraftRefresh() {
    graftResultsContainer.innerHTML = '<span style="color:#a5b4fc">Rebuilding graph in runtime directory...</span>';
    const res = await fetchJSON('/api/graft/query', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question: 'build' })
    });
    graftResultsContainer.textContent = res && res.output ? res.output : 'Refresh completed.';
  }

  // --- Capacity Grid Rendering ---
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
    const tid = document.getElementById('newTaskTid').value.trim();
    const title = document.getElementById('newTaskTitle').value.trim();
    const stage = document.getElementById('newTaskStage').value;
    const role = document.getElementById('newTaskRole').value;
    const tool = document.getElementById('newTaskTool').value;
    const goal = document.getElementById('newTaskGoal').value.trim();
    const allowedRaw = document.getElementById('newTaskAllowed').value.trim();
    const criteriaRaw = document.getElementById('newTaskCriteria').value.trim();

    const allowed = allowedRaw ? allowedRaw.split(/[,\n]+/).map(s => s.trim()).filter(Boolean) : [];
    const criteria = criteriaRaw ? criteriaRaw.split('\n').map(s => s.trim()).filter(Boolean) : [];

    const submitBtn = document.getElementById('btnSubmitTask');
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span>Registering...</span>';

    const res = await fetchJSON('/api/task/create', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
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
      await loadTasks();
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
