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
    analyticsSubTab: 'graph',
    expandedProjects: new Set(),
    openDirs: new Set(),
    treeCache: {},
    explorerPath: '',
    inspectorTaskId: 'research',
    threads: { research: [] },
    researchMeta: {},
    threadCollapsed: new Set(),
    pendingInstall: null,
    openTabs: [],
    chatModel: 'swe-2-high',
    chatModels: [],
    chatPlatform: 'devin',
    platformData: {},
    capacityData: null,
    defaultWorkerModel: null,
    costAnalytics: null,
    costStageFilter: 'all',
  };

  const CHAT_PLATFORMS = [
    { key: 'devin', label: 'Devin' },
    { key: 'claude', label: 'Claude Code' },
    { key: 'codex', label: 'Codex' },
    { key: 'agy', label: 'Antigravity' },
    { key: 'ollama', label: 'Local Ollama' },
  ];

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
  const analyticsFrameWrapper = document.getElementById('analyticsFrameWrapper');
  const costRoiDashboard = document.getElementById('costRoiDashboard');
  const costStageFilterEl = document.getElementById('costStageFilter');
  const btnRebuildDashboard = document.getElementById('btnRebuildDashboard');
  const btnOpenExternalDashboard = document.getElementById('btnOpenExternalDashboard');
  const subTabButtons = document.querySelectorAll('.btn-subtab');
  const analyticsBuiltStamp = document.getElementById('analyticsBuiltStamp');
  const btnDashThemeToggle = document.getElementById('btnDashThemeToggle');
  const workspacePathEl = document.getElementById('workspacePath');
  const btnCapacityRefresh = document.getElementById('btnCapacityRefresh');

  // Explorer Elements
  const explorerBreadcrumbs = document.getElementById('explorerBreadcrumbs');
  const explorerCodeView = document.getElementById('explorerCodeView');
  const explorerStatusBar = document.getElementById('explorerStatusBar');
  const threadSelector = document.getElementById('threadSelector');
  const threadPill = document.getElementById('threadPill');
  const threadDropdown = document.getElementById('threadDropdown');
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
  const btnSynthesizeTasks = document.getElementById('btnSynthesizeTasks');
  const chatModelPill = document.getElementById('chatModelPill');
  const chatModelSelector = document.getElementById('chatModelSelector');
  const chatModelDropdown = document.getElementById('chatModelDropdown');
  const chatPlatformPill = document.getElementById('chatPlatformPill');
  const chatPlatformSelector = document.getElementById('chatPlatformSelector');
  const chatPlatformDropdown = document.getElementById('chatPlatformDropdown');
  const chatPlatformStatus = document.getElementById('chatPlatformStatus');

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
    setupThreadSelector();
    renderAllowedTags();
    renderCriteriaList();
    await loadProjects();
    updateProjectChrome();
    await loadStatus();
    await loadTasks();
    await loadCapacity();
    await loadCostAnalytics();
    paintDashThemeToggle();
    updateAnalyticsFrame();
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
        switchTab('explorer');
        activateResearchThread();
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
    if (globalSearchInput) {
      globalSearchInput.addEventListener('input', (e) => {
        state.searchQuery = e.target.value.toLowerCase().trim();
        renderKanban();
      });
    }

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

    // Chat cockpit: hierarchical thread switcher, composer, header controls
    if (btnChatSend) btnChatSend.addEventListener('click', sendChatMessage);
    if (chatInput) {
      chatInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
          e.preventDefault();
          sendChatMessage();
        }
      });
    }
    if (btnChatNew) btnChatNew.addEventListener('click', activateResearchThread);
    if (btnChatPlus) btnChatPlus.addEventListener('click', activateResearchThread);
    if (btnSynthesizeTasks) btnSynthesizeTasks.addEventListener('click', synthesizeTasksFromDiscussion);
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

    if (costStageFilterEl) {
      costStageFilterEl.addEventListener('change', () => {
        state.costStageFilter = costStageFilterEl.value || 'all';
        if (state.costAnalytics) renderCostDashboard(state.costAnalytics);
      });
    }

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
        await loadCostAnalytics(state.currentProject);
        btnRebuildDashboard.disabled = false;
        btnRebuildDashboard.innerHTML = `
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M23 4v6h-6"/><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/></svg>
          <span>Rebuild Analytics</span>
        `;
        if (res && res.ok) {
          updateAnalyticsFrame(true);
        } else if (state.analyticsSubTab !== 'costs') {
          alert('Analytics rebuild error: ' + (res ? res.error : 'Unknown error'));
        }
      });
    }

    // Dashboard theme toggle: shared localStorage key + postMessage into the embedded frame
    if (btnDashThemeToggle) {
      btnDashThemeToggle.addEventListener('click', () => {
        const next = dashTheme() === 'dark' ? 'light' : 'dark';
        try { localStorage.setItem('dash-theme', next); } catch(e) {}
        paintDashThemeToggle();
        try { analyticsFrame.contentWindow.postMessage({ af: 'dash-theme', theme: next }, location.origin); } catch(e) {}
      });
    }

    // Build stamp: the embedded dashboard posts af-dash-meta; scrape same-origin #hdr .gen as fallback
    window.addEventListener('message', (ev) => {
      if (ev.origin !== location.origin) return;
      const d = ev.data || {};
      if (d.af === 'dash-meta' && d.generated) setAnalyticsBuilt(d.generated);
    });
    if (analyticsFrame) {
      analyticsFrame.addEventListener('load', () => {
        try {
          const doc = analyticsFrame.contentDocument;
          if (doc && doc.documentElement) {
            doc.documentElement.setAttribute('data-embedded', '1');
          }
          if (doc && doc.getElementById('hdr')) {
            analyticsFrame.contentDocument.getElementById('hdr').style.display = 'none';
          }
          const gen = doc && doc.querySelector('#hdr .gen');
          if (gen && gen.textContent) setAnalyticsBuilt(gen.textContent.replace(/^Built\s*/, '').trim());
        } catch(e) {}
      });
    }

    // Model Quota Hub rescan
    if (btnCapacityRefresh) {
      btnCapacityRefresh.addEventListener('click', async () => {
        btnCapacityRefresh.disabled = true;
        await loadCapacity(true);
        btnCapacityRefresh.disabled = false;
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
    if (state.analyticsSubTab === 'costs') {
      if (analyticsFrameWrapper) analyticsFrameWrapper.style.display = 'none';
      if (costRoiDashboard) costRoiDashboard.style.display = 'flex';
      loadCostAnalytics(state.currentProject);
      return;
    }
    if (costRoiDashboard) costRoiDashboard.style.display = 'none';
    if (analyticsFrameWrapper) analyticsFrameWrapper.style.display = '';
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
    const baseQs = qs.length ? `?${qs.join('&')}` : '';
    // embedded=1 tells the dashboard page to hide its own #hdr topbar (Studio supplies the chrome)
    analyticsFrame.src = `${targetUrl}${baseQs}${baseQs ? '&' : '?'}embedded=1`;
    if (btnOpenExternalDashboard) btnOpenExternalDashboard.href = `${targetUrl}${baseQs}`;
    setAnalyticsBuilt('');
  }

  // --- Cost & ROI Dashboard (Plan vs Fact Telemetry) ---
  async function loadCostAnalytics(projPath = '') {
    const target = projPath || state.currentProject;
    const query = target ? `?project=${encodeURIComponent(target)}` : '';
    const res = await fetchJSON(`/api/analytics/costs${query}`);
    if (res && res.ok) {
      state.costAnalytics = res;
      renderCostDashboard(res);
    }
  }

  function formatSignedUsd(val) {
    const n = Number(val) || 0;
    if (Math.abs(n) < 0.000001) return '$0.00';
    const absStr = Math.abs(n) < 0.01 ? ('$' + Math.abs(n).toFixed(4)) : ('$' + Math.abs(n).toFixed(2));
    return (n > 0 ? '+' : '-') + absStr;
  }

  function formatDeltaPct(pct) {
    const n = Number(pct) || 0;
    if (Math.abs(n) < 0.01) return '0.0%';
    return (n > 0 ? '+' : '') + n.toFixed(1) + '%';
  }

  function renderCostDashboard(data) {
    const summary = (data && data.summary) || data || {};
    const stages = (data && data.stages) || [];
    const tasks = (data && data.tasks) || [];

    const elPlanned = document.getElementById('costTotalPlanned');
    const elActual = document.getElementById('costTotalActual');
    const elSavings = document.getElementById('costNetSavings');
    const elFreePct = document.getElementById('costLocalFreePct');

    const elPlannedMeta = document.getElementById('costPlannedTokensMeta');
    const elActualMeta = document.getElementById('costActualTokensMeta');
    const elSavingsMeta = document.getElementById('costSavingsMeta');
    const elFreeMeta = document.getElementById('costLocalFreeMeta');

    const totalPlanUsd = Number(summary.total_planned_usd ?? summary.planned_cost_usd) || 0;
    const totalActualUsd = Number(summary.total_actual_usd ?? summary.actual_cost_usd) || 0;
    const netSavingsUsd = Number(summary.net_savings_usd ?? (totalPlanUsd - totalActualUsd)) || 0;
    const deltaPct = Number(summary.delta_pct) || 0;
    const freePct = Number(summary.local_free_tokens_pct) || 0;

    if (elPlanned) elPlanned.textContent = formatUsdCost(totalPlanUsd);
    if (elActual) elActual.textContent = formatUsdCost(totalActualUsd);
    if (elSavings) {
      elSavings.textContent = (netSavingsUsd < 0 ? '-' : '') + formatUsdCost(Math.abs(netSavingsUsd));
      elSavings.className = 'cost-card-value ' + (netSavingsUsd >= 0 ? 'text-emerald' : 'text-amber');
    }
    if (elFreePct) elFreePct.textContent = freePct.toFixed(1) + '%';

    if (elPlannedMeta) {
      elPlannedMeta.textContent = `${formatTokenCount(summary.planned_tokens || 0)} across ${summary.task_count || tasks.length} tasks`;
    }
    if (elActualMeta) {
      elActualMeta.textContent = `${formatTokenCount(summary.actual_tokens || 0)} · ${summary.model_calls || 0} calls · ${Math.round(summary.execution_time_seconds || 0)}s`;
    }
    if (elSavingsMeta) {
      elSavingsMeta.textContent = `Delta: ${formatSignedUsd(summary.delta_usd || 0)} (${formatDeltaPct(deltaPct)})`;
    }
    if (elFreeMeta) {
      elFreeMeta.textContent = `${formatTokenCount(summary.local_free_tokens || 0)} zero-cost ($0)`;
    }

    if (costStageFilterEl) {
      const prevFilter = state.costStageFilter || 'all';
      costStageFilterEl.innerHTML = '<option value="all">All Stages (' + tasks.length + ')</option>' +
        stages.map(s =>
          `<option value="${escapeHTML(String(s.stage))}"${String(s.stage) === String(prevFilter) ? ' selected' : ''}>${escapeHTML(s.label || ('Stage ' + s.stage))} (${s.task_count || 0})</option>`
        ).join('');
    }

    const stageBarEl = document.getElementById('costStageBar');
    const stageDistEl = document.getElementById('costStageDistribution');
    const stageColors = ['#6366f1', '#3b82f6', '#10b981', '#f59e0b', '#a855f7', '#ec4899', '#14b8a6', '#f97316'];

    if (stageBarEl) {
      if (!stages.length) {
        stageBarEl.innerHTML = '<div class="cost-stage-bar-empty">No stage cost data available</div>';
      } else {
        stageBarEl.innerHTML = stages.map((s, idx) => {
          const share = Math.max(4, Number(s.share_actual_pct || s.share_planned_pct) || (100 / stages.length));
          const color = stageColors[idx % stageColors.length];
          const label = s.label || ('Stage ' + s.stage);
          return `<div class="cost-stage-segment" style="width:${share}%; background:${color};" title="${escapeHTML(label)}: Plan ${escapeHTML(formatUsdCost(s.planned_cost_usd))} / Fact ${escapeHTML(formatUsdCost(s.actual_cost_usd))}"></div>`;
        }).join('');
      }
    }

    if (stageDistEl) {
      if (!stages.length) {
        stageDistEl.innerHTML = '<div class="empty-state">No stages registered in this workspace.</div>';
      } else {
        const maxStageCost = Math.max(
          0.0001,
          ...stages.map(s => Math.max(Number(s.planned_cost_usd) || 0, Number(s.actual_cost_usd) || 0))
        );
        stageDistEl.innerHTML = stages.map((s, idx) => {
          const color = stageColors[idx % stageColors.length];
          const planW = Math.min(100, Math.round(((Number(s.planned_cost_usd) || 0) / maxStageCost) * 100));
          const actW = Math.min(100, Math.round(((Number(s.actual_cost_usd) || 0) / maxStageCost) * 100));
          const dPct = Number(s.delta_pct) || 0;
          const dClass = dPct <= 0 ? 'under' : 'over';
          return `<div class="cost-stage-row" data-stage="${escapeHTML(String(s.stage))}">
            <div class="cost-stage-info">
              <span class="cost-stage-dot" style="background:${color}"></span>
              <span class="cost-stage-name">${escapeHTML(s.label || ('Stage ' + s.stage))}</span>
              <span class="cost-stage-count">${s.task_count || 0} tasks</span>
            </div>
            <div class="cost-stage-bars-wrap">
              <div class="cost-dual-bar">
                <div class="cost-bar-plan" style="width:${planW}%" title="Planned: ${escapeHTML(formatUsdCost(s.planned_cost_usd))}"></div>
              </div>
              <div class="cost-dual-bar">
                <div class="cost-bar-fact" style="width:${actW}%; background:${color}" title="Actual: ${escapeHTML(formatUsdCost(s.actual_cost_usd))}"></div>
              </div>
            </div>
            <div class="cost-stage-metrics">
              <span>Plan: <strong>${escapeHTML(formatUsdCost(s.planned_cost_usd))}</strong></span>
              <span>Fact: <strong>${escapeHTML(formatUsdCost(s.actual_cost_usd))}</strong></span>
              <span class="cost-delta-pill ${dClass}">${escapeHTML(formatDeltaPct(dPct))}</span>
            </div>
          </div>`;
        }).join('');
      }
    }

    const tbody = document.getElementById('costTaskTableBody');
    if (tbody) {
      const filteredTasks = (state.costStageFilter && state.costStageFilter !== 'all')
        ? tasks.filter(t => String(t.stage) === String(state.costStageFilter))
        : tasks;
      if (!filteredTasks.length) {
        tbody.innerHTML = '<tr><td colspan="8" class="empty-state">No tasks found for the selected filter.</td></tr>';
      } else {
        const grouped = new Map();
        filteredTasks.forEach(t => {
          const stg = String(t.stage || '1');
          if (!grouped.has(stg)) grouped.set(stg, []);
          grouped.get(stg).push(t);
        });
        const sortedStageKeys = [...grouped.keys()].sort((a, b) => (parseInt(a, 10) || 0) - (parseInt(b, 10) || 0));
        const rowsHtml = [];
        sortedStageKeys.forEach(stg => {
          const groupTasks = grouped.get(stg);
          const stgLabel = (groupTasks[0] && groupTasks[0].stage_label) || stageLabel(stg);
          const grpPlan = groupTasks.reduce((acc, x) => acc + (Number(x.planned_cost_usd) || 0), 0);
          const grpFact = groupTasks.reduce((acc, x) => acc + (Number(x.actual_cost_usd) || 0), 0);
          rowsHtml.push(
            `<tr class="cost-stage-group-row" data-stage-group="${escapeHTML(stg)}">
              <td colspan="8">
                <strong>${escapeHTML(stgLabel)}</strong>
                <span class="cost-group-meta">${groupTasks.length} task${groupTasks.length === 1 ? '' : 's'} · Plan ${escapeHTML(formatUsdCost(grpPlan))} · Fact ${escapeHTML(formatUsdCost(grpFact))}</span>
              </td>
            </tr>`
          );
          groupTasks.forEach(t => {
            const dPct = Number(t.delta_pct) || 0;
            const dClass = dPct < 0 ? 'under' : (dPct > 0 ? 'over' : 'neutral');
            rowsHtml.push(
              `<tr class="cost-task-row" data-task-id="${escapeHTML(t.id)}" data-stage="${escapeHTML(String(t.stage))}">
                <td><span class="task-stage-badge">${escapeHTML(t.stage_label || ('Stage ' + t.stage))}</span></td>
                <td><span class="task-tid">${escapeHTML(t.id)}</span></td>
                <td class="cost-cell-title" title="${escapeHTML(t.title)}">${escapeHTML(t.title)}</td>
                <td><span class="model-tier-pill">${escapeHTML(t.model || 'swe-2-high')}</span></td>
                <td class="cost-cell-num" data-plan-usd="${escapeHTML(String(t.planned_cost_usd || 0))}">${escapeHTML(formatUsdCost(t.planned_cost_usd))}</td>
                <td class="cost-cell-num" data-fact-usd="${escapeHTML(String(t.actual_cost_usd || 0))}">${escapeHTML(formatUsdCost(t.actual_cost_usd))}</td>
                <td class="cost-cell-num"><span class="cost-delta-pill ${dClass}">${escapeHTML(formatDeltaPct(dPct))}</span></td>
                <td><span class="cost-status-badge status-${escapeHTML(String(t.status || 'ready').replace(/\s+/g, '-').toLowerCase())}">${escapeHTML(t.status || 'ready')}</span></td>
              </tr>`
            );
          });
        });
        tbody.innerHTML = rowsHtml.join('');
      }
    }
  }

  // --- Embedded dashboard bridge: build stamp + theme toggle ---
  const DASH_SUN = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>';
  const DASH_MOON = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg>';
  function dashTheme() {
    try { return localStorage.getItem('dash-theme') || 'dark'; } catch(e) { return 'dark'; }
  }
  function paintDashThemeToggle() {
    if (!btnDashThemeToggle) return;
    const dark = dashTheme() === 'dark';
    btnDashThemeToggle.innerHTML = dark ? DASH_SUN : DASH_MOON;
    btnDashThemeToggle.title = dark ? 'Dashboard: switch to light theme' : 'Dashboard: switch to dark theme';
  }
  function setAnalyticsBuilt(ts) {
    if (!analyticsBuiltStamp) return;
    analyticsBuiltStamp.textContent = ts ? `Built ${ts}` : 'Built —';
    analyticsBuiltStamp.title = ts ? `Dashboard built ${ts}` : 'Dashboard build timestamp';
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
    await loadResearchThreads(target);
    populateInspectorTasks();
  }

  // --- Persistent research threads (folders, refs, forking) ---
  function normalizeRefId(raw) {
    const s = String(raw || '').trim();
    if (/^t-\d{1,4}$/i.test(s)) return s.toUpperCase();
    const flat = s.toLowerCase().replace(/[^a-z0-9]+/g, '');
    if (flat === 'research' || flat === 'taskresearch') return 'research';
    const m = flat.match(/^(?:taskresearch|research)(\d{1,4})$/);
    return m ? 'research-' + String(parseInt(m[1], 10)).padStart(3, '0') : '';
  }

  function extractRefsFromText(text) {
    const refs = [];
    const push = (tok) => {
      const n = normalizeRefId(tok);
      if (n && !refs.includes(n)) refs.push(n);
    };
    const refRe = /\bref\s*:\s*(t-\d+|research\s*-?\s*\d+|task\s+research\s*-?\s*\d*)/gi;
    const forkRe = /\bfork\s+from\s+(research\s*-?\s*\d+|task\s+research\s*-?\s*\d*)/gi;
    let m;
    while ((m = refRe.exec(text || '')) !== null) push(m[1]);
    while ((m = forkRe.exec(text || '')) !== null) push(m[1]);
    return refs;
  }

  function researchMeta(id) {
    return state.researchMeta[id] || null;
  }

  function researchFolderName(id) {
    const meta = researchMeta(id);
    return meta && meta.folder ? meta.folder : '';
  }

  async function loadResearchThreads(projPath = '') {
    const target = projPath || state.currentProject;
    const query = target ? `?project=${encodeURIComponent(target)}` : '';
    const res = await fetchJSON(`/api/research/list${query}`);
    state.researchMeta = {};
    if (res && res.ok && Array.isArray(res.threads)) {
      res.threads.forEach(r => {
        if (!r || !r.id) return;
        state.researchMeta[r.id] = r;
        const local = state.threads[r.id] || [];
        const localMsgs = local.filter(it => it.type === 'message');
        const serverMsgs = (r.messages || [])
          .filter(m => m && m.content)
          .map(m => ({ type: 'message', role: m.role || 'user', content: m.content }));
        const msgs = serverMsgs.length >= localMsgs.length ? serverMsgs : localMsgs;
        state.threads[r.id] = msgs.concat(local.filter(it => it.type !== 'message'));
      });
    }
    renderThreadDropdown();
    updateThreadPill();
  }

  async function updateResearchThread(id, fields) {
    const res = await fetchJSON('/api/research/update', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ project: state.currentProject, id, ...fields }),
    });
    if (res && res.ok && res.thread) {
      state.researchMeta[id] = res.thread;
    } else {
      if (!state.researchMeta[id]) {
        state.researchMeta[id] = { id, name: '', folder: '', refs: [] };
      }
      Object.assign(state.researchMeta[id], fields);
    }
    renderThreadDropdown();
    updateThreadPill();
    if ((state.inspectorTaskId || 'research') === id) renderInspector();
  }

  // --- Model Quota Hub: live CLI probe ---
  async function loadCapacity(force = false) {
    const params = [];
    if (state.currentProject) params.push(`project=${encodeURIComponent(state.currentProject)}`);
    if (force) params.push('refresh=1');
    const res = await fetchJSON(`/api/capacity/probe${params.length ? '?' + params.join('&') : ''}`);
    if (res && res.ok) {
      state.capacityData = res;
      state.defaultWorkerModel = res.default_model || null;
      renderCapacityHub(res);
      applyCapacityModels(res);
    } else {
      const meta = document.getElementById('capacityScanMeta');
      if (meta) meta.textContent = 'CLI probe failed: /api/capacity/probe unreachable';
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
  function availableStageNumbers(currentStage) {
    const nums = new Set([1, 2, 3, 4, 5, 6, 7, 8]);
    const cur = parseInt(String(currentStage || '1'), 10);
    if (Number.isFinite(cur) && cur >= 1) {
      nums.add(cur);
      nums.add(cur + 1);
    }
    state.tasks.forEach(x => {
      const n = parseInt(String(x.stage || '1'), 10);
      if (Number.isFinite(n) && n >= 1) {
        nums.add(n);
        nums.add(n + 1);
      }
    });
    return [...nums].sort((a, b) => a - b);
  }

  async function moveTaskStage(taskId, targetStage, statusEl = null, selectEl = null) {
    const prevTask = state.tasks.find(x => x.id === taskId);
    const prevStage = prevTask ? String(prevTask.stage || '1') : '1';
    if (statusEl) {
      statusEl.style.display = 'block';
      statusEl.style.color = 'var(--text-muted)';
      statusEl.textContent = 'Validating DAG stage transition...';
    }
    try {
      const resp = await fetch('/api/task/move-stage', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          project: state.currentProject,
          id: taskId,
          stage: targetStage,
        }),
      });
      const data = await resp.json().catch(() => null);
      if (resp.ok && data && data.ok) {
        if (statusEl) {
          statusEl.style.display = 'block';
          statusEl.style.color = 'var(--accent-emerald, #34d399)';
          statusEl.textContent = 'Moved ' + taskId + ' to ' + (data.stage_label || stageLabel(targetStage));
        }
        await loadTasks(state.currentProject);
        return data;
      }
      const errMsg = (data && (data.diagnostic || data.error))
        ? (data.diagnostic || data.error)
        : ('Cannot move ' + taskId + ' to ' + stageLabel(targetStage));
      if (selectEl) selectEl.value = prevStage;
      if (statusEl) {
        statusEl.style.display = 'block';
        statusEl.style.color = '#f87171';
        statusEl.textContent = errMsg;
      }
      return data || { ok: false, error: errMsg };
    } catch (err) {
      if (selectEl) selectEl.value = prevStage;
      const fallback = 'Stage move failed: ' + (err && err.message ? err.message : 'network error');
      if (statusEl) {
        statusEl.style.display = 'block';
        statusEl.style.color = '#f87171';
        statusEl.textContent = fallback;
      }
      return { ok: false, error: fallback };
    }
  }

  function openTaskDrawer(t) {
    state.selectedTask = t;
    drawerTaskId.textContent = t.id;
    drawerTaskTitle.textContent = t.title;
    const stageOpts = availableStageNumbers(t.stage).map(n =>
      `<option value="${n}"${String(n) === String(t.stage) ? ' selected' : ''}>${escapeHTML(stageLabel(String(n)))}</option>`
    ).join('');

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
        <div class="metric-row" style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
          <span style="color:var(--text-subtle)">Stage:</span>
          <select id="drawerStageSelect" class="research-ctl-select" aria-label="Move task stage">${stageOpts}</select>
        </div>
        <div id="drawerStageMoveStatus" class="stage-move-diagnostic" style="display:none; font-size:0.76rem; margin-bottom:8px;"></div>
        <div class="metric-row" style="display:flex; justify-content:space-between; margin-bottom:8px;">
          <span style="color:var(--text-subtle)">Depends on:</span>
          <span style="font-weight:600">${escapeHTML(t.depends || 'none')}</span>
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

    const drawerStageSel = document.getElementById('drawerStageSelect');
    const drawerStageStatus = document.getElementById('drawerStageMoveStatus');
    if (drawerStageSel) {
      drawerStageSel.addEventListener('change', () => {
        moveTaskStage(t.id, drawerStageSel.value, drawerStageStatus, drawerStageSel);
      });
    }

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

  // --- Render Capacity Hub (live platform cards) ---
  function renderCapacityHub(data) {
    const grid = document.getElementById('toolsCapacityGrid');
    if (!grid) return;
    grid.innerHTML = '';
    const defaultModelId = state.defaultWorkerModel && state.defaultWorkerModel.model;

    (data.platforms || []).forEach(p => {
      const card = document.createElement('div');
      card.className = 'capacity-item-card';
      const modelRows = (p.models || []).map(m => {
        const meta = [m.context, m.pricing].filter(Boolean).join(' \u00B7 ');
        const isDefault = m.id === defaultModelId;
        return `<div class="model-row">
          <span class="m-id" title="${escapeHTML(m.label || m.id)}">${escapeHTML(m.id)}</span>
          <span class="m-meta${m.free ? ' m-free' : ''}">${escapeHTML(meta)}</span>
          <button type="button" class="btn-set-default${isDefault ? ' is-default' : ''}"
                  data-model="${escapeHTML(m.id)}" data-tool="${escapeHTML(p.key)}"
                  ${isDefault ? 'disabled' : ''}>${isDefault ? 'Default \u2713' : 'Set default'}</button>
        </div>`;
      }).join('');
      card.innerHTML = `
        <div class="capacity-card-top">
          <span class="capacity-tool-title">${escapeHTML(p.label)}${p.version ? `<span class="platform-version">${escapeHTML(p.version)}</span>` : ''}</span>
          <span class="status-badge ${escapeHTML(p.status)}">${escapeHTML(p.status_label || p.status)}</span>
        </div>
        ${p.note ? `<div class="platform-note">${escapeHTML(p.note)}</div>` : ''}
        ${(p.models || []).length ? `<details class="platform-models">
          <summary>${p.models.length} available model${p.models.length === 1 ? '' : 's'}</summary>
          <div class="platform-model-list">${modelRows}</div>
        </details>` : ''}
      `;
      card.querySelectorAll('.btn-set-default[data-model]').forEach(btn => {
        btn.addEventListener('click', () => setDefaultWorkerModel(btn.dataset.model, btn.dataset.tool));
      });
      grid.appendChild(card);
    });

    const meta = document.getElementById('capacityScanMeta');
    if (meta) {
      const platforms = data.platforms || [];
      const active = platforms.filter(p => p.status === 'active').length;
      meta.textContent = `Scanned ${platforms.length} platforms \u00B7 ${active} active \u00B7 ${data.generated_at || ''}${data.cached ? ` \u00B7 cached (TTL ${data.ttl}s)` : ''}`;
    }
    renderLocalFreeSection(data.local_free || {}, defaultModelId);
    updateDefaultModelPill();
  }

  function renderLocalFreeSection(localFree, defaultModelId) {
    const instEl = document.getElementById('localModelsInstalled');
    const sugEl = document.getElementById('localModelsSuggested');
    if (instEl) {
      const installed = localFree.installed || [];
      instEl.innerHTML = installed.length
        ? ''
        : '<div class="empty-state">No local models detected on 127.0.0.1:11434 - install Ollama and pull an open-weight model.</div>';
      installed.forEach(m => {
        const isDefault = m.id === defaultModelId;
        const item = document.createElement('div');
        item.className = 'local-model-item';
        item.innerHTML = `
          <div><div class="lm-id">${escapeHTML(m.id)}</div><div class="lm-note">${escapeHTML(m.context || m.family || '')}</div></div>
          <span class="lm-free">$0 local</span>
          <button type="button" class="btn-set-default${isDefault ? ' is-default' : ''}" ${isDefault ? 'disabled' : ''}>${isDefault ? 'Default \u2713' : 'Set default'}</button>`;
        item.querySelector('.btn-set-default').addEventListener('click', () => setDefaultWorkerModel(m.id, 'ollama'));
        instEl.appendChild(item);
      });
    }
    if (sugEl) {
      const suggested = localFree.suggested || [];
      sugEl.innerHTML = suggested.length ? '' : '<div class="empty-state">No suggestions.</div>';
      suggested.forEach(s => {
        const item = document.createElement('div');
        item.className = 'local-model-item';
        item.innerHTML = `
          <div><div class="lm-id">${escapeHTML(s.id)}</div><div class="lm-note">${escapeHTML(s.note || '')}</div><code class="lm-install">${escapeHTML(s.install || '')}</code></div>
          <span class="lm-free">$0</span>`;
        sugEl.appendChild(item);
      });
    }
  }

  function updateDefaultModelPill() {
    const pill = document.getElementById('defaultWorkerModelPill');
    if (!pill) return;
    const d = state.defaultWorkerModel;
    pill.textContent = d && d.model ? `Default: ${d.model}` : 'Default: \u2014';
    pill.title = d && d.model
      ? `Project default worker model: ${d.model}${d.tool ? ' (' + d.tool + ')' : ''}`
      : 'No project default worker model set';
  }

  async function setDefaultWorkerModel(modelId, tool) {
    const res = await fetchJSON('/api/capacity/default-model', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ project: state.currentProject, model: modelId, tool: tool })
    });
    if (res && res.ok) {
      state.defaultWorkerModel = res.default_model;
      state.chatModel = modelId;
      if (CHAT_PLATFORMS.some(p => p.key === tool)) {
        state.chatPlatform = tool;
        try { sessionStorage.setItem('af_chat_platform', tool); } catch (err) { /* storage unavailable */ }
      }
      ensureChatModelListed(modelId, tool);
      try { sessionStorage.setItem('af_chat_model', modelId); } catch (err) { /* storage unavailable */ }
      updateDefaultModelPill();
      updateChatPlatformPill();
      renderPlatformDropdown();
      updatePlatformStatusPill();
      updateChatModelPill();
      renderModelDropdown();
      if (state.capacityData) renderCapacityHub(state.capacityData);
    } else {
      alert('Could not persist default model: ' + (res && res.error ? res.error : 'unknown error'));
    }
  }

  function ensureChatModelListed(modelId, tool) {
    if (!state.chatModels.some(m => m.id === modelId)) {
      state.chatModels.unshift({ id: modelId, label: `${tool || 'CLI'} ${modelId}`, note: modelId });
    }
  }

  // Map a probed platform record to the chat model dropdown entries for that platform.
  function platformModelList(p) {
    if (!p || !(p.models || []).length) return CHAT_MODELS.slice();
    return p.models.map(m => ({
      id: m.id,
      label: `${p.label} ${m.id}`,
      note: m.free ? 'free / local' : (m.pricing || m.context || p.status_label || '')
    }));
  }

  function applyCapacityModels(data) {
    (data.platforms || []).forEach(p => { state.platformData[p.key] = p; });
    const d = data.default_model;
    let savedPlatform = null, savedModel = null;
    try {
      savedPlatform = sessionStorage.getItem('af_chat_platform');
      savedModel = sessionStorage.getItem('af_chat_model');
    } catch (err) { /* storage unavailable */ }
    if (savedPlatform && CHAT_PLATFORMS.some(p => p.key === savedPlatform)) {
      state.chatPlatform = savedPlatform;
    } else if (d && d.tool && CHAT_PLATFORMS.some(p => p.key === d.tool)) {
      state.chatPlatform = d.tool;
    }
    state.chatModels = platformModelList(state.platformData[state.chatPlatform]);
    if (savedModel && state.chatModels.some(m => m.id === savedModel)) {
      state.chatModel = savedModel;
    } else if (d && d.model) {
      state.chatModel = d.model;
      ensureChatModelListed(d.model, d.tool);
    } else if (!state.chatModels.some(m => m.id === state.chatModel)) {
      state.chatModel = state.chatModels[0] ? state.chatModels[0].id : CHAT_MODELS[0].id;
    }
    updateChatPlatformPill();
    renderPlatformDropdown();
    updatePlatformStatusPill();
    updateChatModelPill();
    renderModelDropdown();
  }

  // --- Chat platform selector (dynamic per-platform model probing) ---
  function platformLabel(key) {
    const pl = CHAT_PLATFORMS.find(p => p.key === key);
    return pl ? pl.label : key;
  }

  function platformStatusOf(key) {
    const p = state.platformData[key];
    return p ? (p.status_label || p.status || '') : '';
  }

  function updateChatPlatformPill() {
    if (!chatPlatformPill) return;
    chatPlatformPill.innerHTML = `${escapeHTML(platformLabel(state.chatPlatform))} <span class="model-caret">&#8963;</span>`;
    chatPlatformPill.title = `Chat platform: ${platformLabel(state.chatPlatform)}`;
  }

  function renderPlatformDropdown() {
    if (!chatPlatformDropdown) return;
    chatPlatformDropdown.innerHTML = '';
    CHAT_PLATFORMS.forEach(pl => {
      const opt = document.createElement('button');
      opt.type = 'button';
      opt.className = `model-option${pl.key === state.chatPlatform ? ' active' : ''}`;
      opt.setAttribute('role', 'menuitem');
      opt.innerHTML = `<span>${escapeHTML(pl.label)}</span><span class="model-id">${escapeHTML(platformStatusOf(pl.key) || 'not probed yet')}</span>`;
      opt.addEventListener('click', (ev) => {
        ev.stopPropagation();
        selectChatPlatform(pl.key);
        chatPlatformSelector.classList.remove('open');
      });
      chatPlatformDropdown.appendChild(opt);
    });
  }

  function updatePlatformStatusPill() {
    if (!chatPlatformStatus) return;
    const p = state.platformData[state.chatPlatform];
    if (!p || p.status === 'active') {
      chatPlatformStatus.hidden = true;
      chatPlatformStatus.textContent = '';
      return;
    }
    chatPlatformStatus.hidden = false;
    chatPlatformStatus.className = `platform-status-pill status-badge ${p.status || 'missing'}`;
    chatPlatformStatus.textContent = p.status_label || 'Not Installed';
    chatPlatformStatus.title = `${p.note ? p.note + ' — ' : ''}Pick an Active platform or install/authenticate this CLI to use it.`;
  }

  function applyPlatformModels(key) {
    const p = state.platformData[key];
    state.chatModels = platformModelList(p);
    if (!state.chatModels.some(m => m.id === state.chatModel)) {
      state.chatModel = state.chatModels[0] ? state.chatModels[0].id : CHAT_MODELS[0].id;
      try { sessionStorage.setItem('af_chat_model', state.chatModel); } catch (err) { /* storage unavailable */ }
    }
    updatePlatformStatusPill();
    updateChatModelPill();
    renderModelDropdown();
  }

  // Live re-probe of one platform's CLI: populates the dependent model dropdown.
  async function probeChatPlatform(key) {
    const params = [`platform=${encodeURIComponent(key)}`];
    if (state.currentProject) params.push(`project=${encodeURIComponent(state.currentProject)}`);
    const res = await fetchJSON(`/api/capacity/probe?${params.join('&')}`);
    if (res && res.ok && res.platform) {
      state.platformData[key] = res.platform;
    } else if (!state.platformData[key]) {
      state.platformData[key] = {
        key, label: platformLabel(key), status: 'missing',
        status_label: 'Not Installed', models: [], note: 'platform probe unreachable'
      };
    }
    renderPlatformDropdown();
    if (key === state.chatPlatform) applyPlatformModels(key);
  }

  function selectChatPlatform(key) {
    state.chatPlatform = key;
    try { sessionStorage.setItem('af_chat_platform', key); } catch (err) { /* storage unavailable */ }
    updateChatPlatformPill();
    updatePlatformStatusPill();
    probeChatPlatform(key);
  }

  // --- Create Task Form Handler (Guarded: manual creation disabled in Implementations) ---
  async function handleTaskCreate(e) {
    e.preventDefault();
    alert('Manual task creation inside Implementations is disabled; tasks enter exclusively via approved synthesis pool in Researches.');
    switchTab('explorer');
    activateResearchThread();
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
    await Promise.all([loadStatus(path), loadTasks(path), loadCapacity(), loadCostAnalytics(path)]);
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
    if (workspacePathEl) {
      workspacePathEl.textContent = state.currentProject || name;
      workspacePathEl.title = state.currentProject || name;
    }
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
  function getThreadItems(threadId) {
    const key = threadId || 'research';
    if (!state.threads[key]) state.threads[key] = [];
    return state.threads[key];
  }

  function isResearchThread(id) {
    return id === 'research' || (id || '').startsWith('research-');
  }

  function researchThreadIds() {
    const ids = new Set(['research']);
    Object.keys(state.researchMeta).forEach(id => ids.add(id));
    Object.keys(state.threads).forEach(id => { if (isResearchThread(id)) ids.add(id); });
    return [...ids].sort((a, b) => {
      if (a === 'research') return -1;
      if (b === 'research') return 1;
      return a.localeCompare(b);
    });
  }

  function threadLabel(id) {
    const meta = researchMeta(id);
    if (id === 'research') return '🔍 ' + (meta && meta.name ? meta.name : 'Research & Inception');
    if (isResearchThread(id)) {
      return '🔍 ' + (meta && meta.name ? meta.name : 'Research #' + id.slice('research-'.length));
    }
    const t = state.tasks.find(x => x.id === id);
    return t ? t.id + ' — ' + t.title : String(id);
  }

  function groupTasksByStage(tasks) {
    const groups = {};
    tasks.forEach(t => {
      const key = String(t.stage || '0');
      (groups[key] = groups[key] || []).push(t);
    });
    return Object.keys(groups)
      .sort((a, b) => (parseInt(a, 10) || 0) - (parseInt(b, 10) || 0) || a.localeCompare(b))
      .map(k => ({ stage: k, tasks: groups[k] }));
  }

  function stageLabel(stageKey) {
    const n = parseInt(stageKey, 10);
    return 'Stage ' + (isNaN(n) ? stageKey : String(n).padStart(2, '0'));
  }

  function threadCaretSvg() {
    return '<svg class="thread-caret" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"/></svg>';
  }

  function buildCollapsibleHeader(cls, collapseKey, title, count) {
    const collapsed = state.threadCollapsed.has(collapseKey);
    const header = document.createElement('button');
    header.type = 'button';
    header.className = cls;
    header.setAttribute('data-collapse-key', collapseKey);
    header.setAttribute('aria-expanded', collapsed ? 'false' : 'true');
    header.innerHTML = threadCaretSvg() +
      '<span class="thread-title">' + escapeHTML(title) + '</span>' +
      '<span class="thread-count">' + count + '</span>';
    header.addEventListener('click', () => toggleThreadCollapse(collapseKey));
    return header;
  }

  function buildCollapsibleBody(cls) {
    const body = document.createElement('div');
    body.className = cls;
    const inner = document.createElement('div');
    inner.className = 'thread-body-inner';
    body.appendChild(inner);
    return { body, inner };
  }

  function buildThreadItem(id) {
    const item = document.createElement('button');
    item.type = 'button';
    item.className = 'thread-item' + ((state.inspectorTaskId || 'research') === id ? ' active' : '');
    item.setAttribute('data-thread', id);
    item.setAttribute('role', 'menuitem');
    item.textContent = threadLabel(id);
    item.addEventListener('click', () => selectThread(id));
    if (isResearchThread(id)) {
      item.title = 'Double-click to rename';
      item.addEventListener('dblclick', (ev) => {
        ev.stopPropagation();
        startRenameThread(id, item);
      });
    }
    return item;
  }

  function startRenameThread(id, itemEl) {
    const meta = researchMeta(id);
    const current = (meta && meta.name) || (id === 'research' ? 'Research & Inception' : id);
    const input = document.createElement('input');
    input.type = 'text';
    input.className = 'thread-rename-input';
    input.value = current;
    input.setAttribute('aria-label', 'Rename research thread');
    let done = false;
    const commit = () => {
      if (done) return;
      done = true;
      const name = input.value.trim();
      if (name && name !== current) updateResearchThread(id, { name });
      else renderThreadDropdown();
    };
    input.addEventListener('keydown', (e) => {
      e.stopPropagation();
      if (e.key === 'Enter') { e.preventDefault(); commit(); }
      else if (e.key === 'Escape') { done = true; renderThreadDropdown(); }
    });
    input.addEventListener('blur', commit);
    input.addEventListener('click', (e) => e.stopPropagation());
    itemEl.replaceWith(input);
    input.focus();
    input.select();
  }

  function buildStageGroup(stageKey, tasks) {
    const collapseKey = 'stage:' + stageKey;
    const grp = document.createElement('div');
    grp.className = 'thread-stage-group' + (state.threadCollapsed.has(collapseKey) ? ' collapsed' : '');
    grp.setAttribute('data-stage', stageKey);
    grp.appendChild(buildCollapsibleHeader('thread-stage-header', collapseKey, stageLabel(stageKey), tasks.length));
    const { body, inner } = buildCollapsibleBody('thread-stage-body');
    tasks.forEach(t => inner.appendChild(buildThreadItem(t.id)));
    grp.appendChild(body);
    return grp;
  }

  function buildFolderGroup(folderName, ids) {
    const collapseKey = 'folder:' + folderName;
    const grp = document.createElement('div');
    grp.className = 'thread-folder-group' + (state.threadCollapsed.has(collapseKey) ? ' collapsed' : '');
    grp.setAttribute('data-folder', folderName);
    grp.appendChild(buildCollapsibleHeader('thread-folder-header', collapseKey, '📁 ' + folderName, ids.length));
    const { body, inner } = buildCollapsibleBody('thread-folder-body');
    ids.forEach(id => inner.appendChild(buildThreadItem(id)));
    grp.appendChild(body);
    return grp;
  }

  function buildThreadSection(sectionKey, title, count, withAdd, fill) {
    const collapseKey = 'sec:' + sectionKey;
    const allowAdd = Boolean(withAdd) && sectionKey !== 'implementations';
    const sec = document.createElement('div');
    sec.className = 'thread-section' + (state.threadCollapsed.has(collapseKey) ? ' collapsed' : '');
    sec.setAttribute('data-section', sectionKey);
    sec.setAttribute('data-manual-create', allowAdd ? 'enabled' : 'disabled');
    const top = document.createElement('div');
    top.className = 'thread-section-top';
    top.appendChild(buildCollapsibleHeader('thread-section-header', collapseKey, title, count));
    if (allowAdd) {
      const addBtn = document.createElement('button');
      addBtn.type = 'button';
      addBtn.className = 'thread-add';
      addBtn.title = 'New research thread';
      addBtn.setAttribute('aria-label', 'New research thread');
      addBtn.textContent = '+';
      addBtn.addEventListener('click', (ev) => { ev.stopPropagation(); addResearchThread(); });
      top.appendChild(addBtn);
    }
    sec.appendChild(top);
    const { body, inner } = buildCollapsibleBody('thread-section-body');
    fill(inner);
    sec.appendChild(body);
    return sec;
  }

  function renderThreadDropdown() {
    if (!threadDropdown) return;
    threadDropdown.innerHTML = '';
    const researchIds = researchThreadIds();
    threadDropdown.appendChild(buildThreadSection('researches', '🔍 Researches', researchIds.length, true, (inner) => {
      const unfiled = researchIds.filter(id => !researchFolderName(id));
      const folderNames = [...new Set(researchIds.map(researchFolderName).filter(Boolean))].sort();
      unfiled.forEach(id => inner.appendChild(buildThreadItem(id)));
      folderNames.forEach(fname => {
        inner.appendChild(buildFolderGroup(fname, researchIds.filter(id => researchFolderName(id) === fname)));
      });
    }));
    const groups = groupTasksByStage(state.tasks);
    threadDropdown.appendChild(buildThreadSection('implementations', 'Implementations', state.tasks.length, false, (inner) => {
      groups.forEach(g => inner.appendChild(buildStageGroup(g.stage, g.tasks)));
      if (!groups.length) {
        const empty = document.createElement('div');
        empty.className = 'thread-empty';
        empty.textContent = 'No tasks in this workspace';
        inner.appendChild(empty);
      }
    }));
  }

  function toggleThreadCollapse(collapseKey) {
    if (state.threadCollapsed.has(collapseKey)) {
      state.threadCollapsed.delete(collapseKey);
    } else {
      state.threadCollapsed.add(collapseKey);
    }
    renderThreadDropdown();
    const btn = threadDropdown.querySelector('[data-collapse-key="' + collapseKey + '"]');
    if (btn) btn.focus();
  }

  function openThreadDropdown() {
    if (!threadSelector) return;
    renderThreadDropdown();
    threadSelector.classList.add('open');
    if (threadPill) threadPill.setAttribute('aria-expanded', 'true');
  }

  function closeThreadDropdown() {
    if (!threadSelector) return;
    threadSelector.classList.remove('open');
    if (threadPill) threadPill.setAttribute('aria-expanded', 'false');
  }

  function updateThreadPill() {
    if (!threadPill) return;
    const label = threadLabel(state.inspectorTaskId || 'research');
    threadPill.innerHTML = escapeHTML(label) + ' <span class="model-caret">&#8963;</span>';
    threadPill.title = 'Thread: ' + label;
  }

  function selectThread(id) {
    state.inspectorTaskId = id || 'research';
    closeThreadDropdown();
    updateThreadPill();
    renderThreadDropdown();
    renderInspector();
  }

  function nextResearchSeq() {
    let max = 0;
    researchThreadIds().forEach(id => {
      const m = id.match(/^research-(\d+)$/);
      if (m) max = Math.max(max, parseInt(m[1], 10));
    });
    return max + 1;
  }

  async function addResearchThread(folder = '', forkFrom = '') {
    let id;
    const res = await fetchJSON('/api/research/create', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ project: state.currentProject, folder, fork_from: forkFrom }),
    });
    if (res && res.ok && res.thread && res.thread.id) {
      id = res.thread.id;
      state.researchMeta[id] = res.thread;
      if (!state.threads[id]) state.threads[id] = [];
    } else {
      id = 'research-' + String(nextResearchSeq()).padStart(3, '0');
      state.threads[id] = [];
      state.researchMeta[id] = {
        id, name: 'Task Research - ' + id.slice('research-'.length),
        folder: folder || '', refs: forkFrom ? [normalizeRefId(forkFrom)] : [],
      };
    }
    renderThreadDropdown();
    selectThread(id);
    if (chatInput) chatInput.focus();
  }

  function activateResearchThread() {
    selectThread('research');
    if (chatInput) chatInput.focus();
  }

  function threadFocusables() {
    if (!threadDropdown) return [];
    return Array.from(threadDropdown.querySelectorAll(
      '.thread-item, .thread-add, .thread-section-header, .thread-stage-header, .thread-folder-header'
    )).filter(el => !el.closest('.collapsed'));
  }

  function onThreadKeydown(e) {
    const items = threadFocusables();
    if (!items.length) return;
    const idx = items.indexOf(document.activeElement);
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      items[Math.min(idx + 1, items.length - 1)].focus();
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      items[Math.max(idx - 1, 0)].focus();
    } else if (e.key === 'Enter') {
      e.preventDefault();
      const el = items[idx] || items[0];
      if (el) el.click();
    } else if (e.key === 'Escape') {
      e.preventDefault();
      closeThreadDropdown();
      if (threadPill) threadPill.focus();
    } else if (e.key === 'ArrowRight' || e.key === 'ArrowLeft') {
      const el = items[idx];
      if (!el || !el.getAttribute('data-collapse-key')) return;
      const collapsed = state.threadCollapsed.has(el.getAttribute('data-collapse-key'));
      if ((e.key === 'ArrowRight' && collapsed) || (e.key === 'ArrowLeft' && !collapsed)) {
        e.preventDefault();
        toggleThreadCollapse(el.getAttribute('data-collapse-key'));
      }
    }
  }

  function setupThreadSelector() {
    if (!threadSelector || !threadPill || !threadDropdown) return;
    updateThreadPill();
    renderThreadDropdown();
    threadPill.addEventListener('click', (ev) => {
      ev.stopPropagation();
      if (threadSelector.classList.contains('open')) closeThreadDropdown();
      else openThreadDropdown();
    });
    threadPill.addEventListener('keydown', (e) => {
      if (e.key === 'ArrowDown') {
        e.preventDefault();
        openThreadDropdown();
        const items = threadFocusables();
        if (items.length) items[0].focus();
      } else if (e.key === 'Escape') {
        closeThreadDropdown();
      }
    });
    threadDropdown.addEventListener('keydown', onThreadKeydown);
    document.addEventListener('click', (ev) => {
      if (!threadSelector.contains(ev.target)) closeThreadDropdown();
    });
  }

  function populateInspectorTasks() {
    const prev = state.inspectorTaskId || 'research';
    const valid = isResearchThread(prev) || state.tasks.some(t => t.id === prev);
    if (!valid) state.inspectorTaskId = 'research';
    renderThreadDropdown();
    updateThreadPill();
    renderInspector();
  }

  function chatToolLabel(t) {
    const toolNames = { devin: 'Devin', claude: 'Claude', codex: 'Codex', agy: 'Gemini' };
    const toolName = toolNames[(t.tool || '').toLowerCase()] || (t.tool ? t.tool : 'Devin');
    return t.model ? (toolName + ' ' + t.model) : (toolName + ' swe-2-high');
  }

  function execStatusText(t) {
    const status = (t.status || '').toLowerCase();
    const base = 'Задача ' + t.id + ': ' + t.title;
    if (status === 'in progress') return base + ' — успешно разблокирована, утверждена в реестре и запущена на исполнение!';
    if (status === 'review') return base + ' — исполнение завершено, артефакт передан на независимую проверку!';
    if (status === 'done') return base + ' — проверка пройдена, результат принят и слит в main!';
    return base + ' — утверждена в реестре и готова к запуску!';
  }

  function renderThreadItem(item) {
    if (item.type === 'pool') return createTaskPoolCardElement(item.data, item);
    const bubble = document.createElement('div');
    bubble.className = 'chat-bubble ' + (item.role === 'assistant' ? ('assistant' + (item.error ? ' error' : '')) : 'user');
    bubble.textContent = item.content;
    return bubble;
  }

  function formatTokenCount(tokens) {
    const n = Number(tokens) || 0;
    if (n >= 1000) {
      return (n / 1000).toFixed(1).replace(/\.0$/, '') + 'K tokens';
    }
    return n + ' tokens';
  }

  function formatUsdCost(cost) {
    const c = Number(cost) || 0;
    if (c <= 0) return '$0.00';
    if (c < 0.01) return '$' + c.toFixed(4);
    return '$' + c.toFixed(2);
  }

  function createTaskPoolCardElement(poolData, holder) {
    const card = document.createElement('div');
    card.className = 'task-pool-card';
    const tasks = poolData.tasks || poolData.pool || [];
    const blastFiles = (poolData.blast_radius && poolData.blast_radius.affected_files) || [];
    const registered = Boolean(holder && holder.registered);

    const totalTokens = poolData.planned_tokens != null
      ? Number(poolData.planned_tokens)
      : tasks.reduce((acc, t) => acc + (Number(t.planned_tokens) || 0), 0);
    const totalCostUsd = poolData.planned_cost_usd != null
      ? Number(poolData.planned_cost_usd)
      : tasks.reduce((acc, t) => acc + (Number(t.planned_cost_usd) || 0), 0);

    const header = document.createElement('div');
    header.className = 'pool-card-header';
    header.innerHTML = '<span>✨ Synthesized Task Pool (' + tasks.length + ')</span><span class="badge">Graft AST</span>';
    card.appendChild(header);

    const blastEl = document.createElement('div');
    blastEl.className = 'pool-blast-summary';
    blastEl.textContent = 'AST Blast Radius (' + blastFiles.length + ' files): ' + (blastFiles.join(', ') || 'scoped to workspace');
    card.appendChild(blastEl);

    const budgetEl = document.createElement('div');
    budgetEl.className = 'pool-budget-summary';
    budgetEl.innerHTML =
      '<span>Jev Plan Budget:</span>' +
      '<span class="token-badge">' + escapeHTML(formatTokenCount(totalTokens)) + '</span>' +
      '<span class="cost-badge budget-badge">' + escapeHTML(formatUsdCost(totalCostUsd)) + '</span>';
    card.appendChild(budgetEl);

    tasks.forEach(t => {
      const itemEl = document.createElement('div');
      itemEl.className = 'pool-task-item';
      const isEsc = (t.model || '').includes('argon') || t.tier === 'escalation';
      const stgText = t.stage_label || stageLabel(t.stage || '1');
      const taskTokens = t.planned_tokens != null
        ? Number(t.planned_tokens)
        : ((Number(t.planned_input_tokens) || 0) + (Number(t.planned_output_tokens) || 0));
      const taskCost = t.planned_cost_usd != null ? Number(t.planned_cost_usd) : 0;
      const skills = Array.isArray(t.skills)
        ? t.skills
        : (typeof t.skills === 'string' && t.skills && t.skills !== 'none'
          ? t.skills.split(',').map(s => s.trim()).filter(Boolean)
          : []);
      const skillBadges = skills.map(s =>
        '<span class="skill-badge skill-pill" data-skill="' + escapeHTML(s) + '">' + escapeHTML(s) + '</span>'
      ).join('');
      const allowedList = (t.allowed_files || t.allowed || []).map(f => '<li><code>' + escapeHTML(f) + '</code></li>').join('');
      const critList = (t.criteria || []).map(c => '<li>' + escapeHTML(typeof c === 'object' ? (c.id + ': ' + c.text) : String(c)) + '</li>').join('');
      itemEl.innerHTML =
        '<div class="pool-task-top">' +
          '<span class="task-tid">' + escapeHTML(t.id) + '</span>' +
          '<span class="task-stage-badge">' + escapeHTML(stgText) + '</span>' +
          '<span class="effort-badge">Effort: ' + escapeHTML(t.effort || 'high') + '</span>' +
          '<span class="model-tier-pill' + (isEsc ? ' escalation' : '') + '">' + escapeHTML(t.model || 'swe-2-high') + '</span>' +
          '<span class="token-badge" data-planned-tokens="' + escapeHTML(String(taskTokens)) + '" title="Input: ' + escapeHTML(String(t.planned_input_tokens || 0)) + ' / Output: ' + escapeHTML(String(t.planned_output_tokens || 0)) + '">' + escapeHTML(formatTokenCount(taskTokens)) + '</span>' +
          '<span class="cost-badge budget-badge" data-planned-cost="' + escapeHTML(String(taskCost)) + '">' + escapeHTML(formatUsdCost(taskCost)) + '</span>' +
          skillBadges +
        '</div>' +
        '<div class="task-card-title">' + escapeHTML(t.title) + '</div>' +
        '<details class="pool-task-details">' +
          '<summary>Allowed Files (' + (t.allowed_files || t.allowed || []).length + ') &amp; Acceptance Criteria (' + (t.criteria || []).length + ')</summary>' +
          '<div style="margin-top:6px; font-size:0.74rem;">' +
            '<strong>Allowed Files:</strong><ul style="margin:4px 0 6px 16px;">' + allowedList + '</ul>' +
            '<strong>Acceptance Criteria:</strong><ul style="margin:4px 0 0 16px;">' + critList + '</ul>' +
          '</div>' +
        '</details>';
      card.appendChild(itemEl);
    });

    const approveBtn = document.createElement('button');
    approveBtn.type = 'button';
    approveBtn.className = 'btn-approve-pool';
    approveBtn.disabled = registered;
    approveBtn.textContent = registered
      ? ('✓ Registered in Ledger (' + tasks.map(x => x.id).join(', ') + ')')
      : 'Approve & Register Pool in Ledger';
    approveBtn.addEventListener('click', () => approveAndRegisterPool(tasks, approveBtn, holder));
    card.appendChild(approveBtn);
    return card;
  }

  async function approveAndRegisterPool(tasks, btnEl, holder) {
    if (!tasks || !tasks.length) return;
    btnEl.disabled = true;
    btnEl.textContent = 'Registering pool in ledger...';
    const res = await fetchJSON('/api/task/pool/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ project: state.currentProject, tasks: tasks })
    });
    if (res && res.ok) {
      if (holder) holder.registered = true;
      btnEl.textContent = '✓ Registered in Ledger (' + (res.registered || []).join(', ') + ')';
      await loadTasks(state.currentProject);
      renderProjectAccordion();
    } else {
      btnEl.disabled = false;
      btnEl.textContent = 'Approve & Register Pool in Ledger';
      alert('Failed to register pool: ' + (res && res.error ? res.error : 'Unknown error'));
    }
  }

  async function synthesizeTasksFromDiscussion() {
    if (!chatStream) return;
    const threadKey = state.inspectorTaskId || 'research';
    if (!isResearchThread(threadKey)) {
      activateResearchThread();
      return;
    }
    if (chatInput && chatInput.value.trim()) sendChatMessage();
    const items = getThreadItems(threadKey);
    const messages = items.filter(it => it.type === 'message').map(it => ({ role: it.role, content: it.content }));

    if (btnSynthesizeTasks) {
      btnSynthesizeTasks.disabled = true;
      btnSynthesizeTasks.textContent = '✨ Synthesizing AST Pool...';
    }
    const res = await fetchJSON('/api/task/synthesize', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        project: state.currentProject,
        thread: threadKey,
        model: state.chatModel,
        messages: messages
      })
    });
    if (btnSynthesizeTasks) {
      btnSynthesizeTasks.disabled = false;
      btnSynthesizeTasks.textContent = '✨ Synthesize Tasks from Discussion';
    }
    if (res && res.ok) {
      const holder = { type: 'pool', data: res, registered: false };
      items.push(holder);
      chatStream.appendChild(createTaskPoolCardElement(res, holder));
      chatStream.scrollTop = chatStream.scrollHeight;
    }
  }

  function renderInspector() {
    if (!chatStream) return;
    updateChatModelPill();
    const threadKey = state.inspectorTaskId || 'research';
    if (isResearchThread(threadKey)) {
      if (btnSynthesizeTasks) btnSynthesizeTasks.disabled = false;
      const m = currentChatModel();
      chatStream.innerHTML =
        '<div class="chat-exec-card">' +
          '<div class="exec-status-text">' + escapeHTML(threadLabel(threadKey)) + ' Thread — Free-form architecture ideation &amp; AST task synthesis</div>' +
          '<div class="exec-meta">' +
            '<div class="exec-meta-row"><span class="k">Mode</span><span class="v">Conversational Inception</span></div>' +
            '<div class="exec-meta-row"><span class="k">Model</span><span class="v">' + escapeHTML(m.label) + '</span></div>' +
            '<div class="exec-meta-row"><span class="k">AST Graph</span><span class="v">Graft local blast-radius active</span></div>' +
            '<div class="exec-meta-row"><span class="k">Folder</span><span class="v research-ctl" id="researchFolderCtl"></span></div>' +
            '<div class="exec-meta-row"><span class="k">Refs</span><span class="v research-ctl" id="researchRefsCtl"></span></div>' +
          '</div>' +
        '</div>';
      getThreadItems(threadKey).forEach(it => chatStream.appendChild(renderThreadItem(it)));
      renderResearchControls(threadKey);
      return;
    }

    if (btnSynthesizeTasks) btnSynthesizeTasks.disabled = true;
    const t = state.tasks.find(x => x.id === threadKey);
    if (!t) {
      chatStream.innerHTML = '<div class="empty-state"><p>No task selected or no tasks in this workspace.</p></div>';
      return;
    }
    const toolLabel = chatToolLabel(t);
    const running = (t.status || '').toLowerCase() === 'in progress';
    const statusLabel = running ? 'RUNNING Attempt 1' : String(t.status || 'ready').toUpperCase();
    const workedDetail = running
      ? 'Gate preflight: pass | Contract locked | Attempt 1 in progress'
      : 'Gate preflight: pass | Contract locked | Attempt history in .runtime/';
    const allowedHtml = (t.allowed_files || []).map(f => '<li><code>' + escapeHTML(f) + '</code></li>').join('');
    const critHtml = (t.criteria || []).map(c => '<li>' + escapeHTML((c.id ? c.id + ': ' : '') + (c.text || c)) + '</li>').join('');
    const stageOpts = availableStageNumbers(t.stage).map(n =>
      '<option value="' + n + '"' + (String(n) === String(t.stage) ? ' selected' : '') + '>' + escapeHTML(stageLabel(String(n))) + '</option>'
    ).join('');

    chatStream.innerHTML =
      '<div class="chat-bubble user">приступай к ' + escapeHTML(t.id) + '</div>' +
      '<div class="chat-worked" id="chatWorked"><span class="chat-worked-caret">&#8250;</span><span>Worked for 2m</span></div>' +
      '<div class="chat-worked-detail" id="chatWorkedDetail" style="display:none">' + escapeHTML(workedDetail) + '</div>' +
      '<div class="chat-exec-card">' +
        '<div class="exec-status-text">' + escapeHTML(execStatusText(t)) + '</div>' +
        '<div class="exec-meta">' +
          '<div class="exec-meta-row"><span class="k">Task ID</span><span class="v">' + escapeHTML(t.id) + '</span></div>' +
          '<div class="exec-meta-row"><span class="k">Stage</span><span class="v"><select id="taskStageSelect" class="research-ctl-select" aria-label="Reassign task stage">' + stageOpts + '</select></span></div>' +
          '<div class="exec-meta-row"><span class="k">Depends on</span><span class="v" id="taskDependsOn">' + escapeHTML(t.depends || 'none') + '</span></div>' +
          '<div class="exec-meta-row"><span class="k">Role</span><span class="v">' + escapeHTML(t.role || '—') + '</span></div>' +
          '<div class="exec-meta-row"><span class="k">Tool</span><span class="v">' + escapeHTML(toolLabel) + '</span></div>' +
          '<div class="exec-meta-row"><span class="k">Worktree</span><span class="v">' + escapeHTML(t.worktree || '—') + ' <span id="taskWorktreeStatus" class="badge">checking...</span></span></div>' +
          '<div class="exec-meta-row"><span class="k">Status</span><span class="v' + (running ? ' running' : '') + '">' + escapeHTML(statusLabel) + '</span></div>' +
        '</div>' +
        '<div id="taskStageMoveStatus" class="stage-move-diagnostic" style="display:none; font-size:0.75rem; margin:6px 0;"></div>' +
        '<details class="pool-task-details" open><summary>Contract Scope: Allowed Files &amp; Criteria</summary>' +
          '<div id="taskContextScope" style="margin-top:6px; font-size:0.74rem;">' +
            (t.goal ? '<div id="taskContractGoal" style="margin-bottom:6px;"><strong>Goal:</strong> ' + escapeHTML(t.goal) + '</div>' : '<div id="taskContractGoal" style="margin-bottom:6px;"></div>') +
            '<strong>Allowed Files:</strong><ul id="taskAllowedList" style="margin:4px 0 6px 16px;">' + (allowedHtml || '<li>none</li>') + '</ul>' +
            '<strong>Acceptance Criteria:</strong><ul id="taskCriteriaList" style="margin:4px 0 0 16px;">' + (critHtml || '<li>none</li>') + '</ul>' +
          '</div>' +
        '</details>' +
        '<div class="exec-diff" id="execDiff">' +
          '<div class="exec-diff-summary" id="execDiffSummary">' +
            '<span id="execDiffText">loading diff...</span>' +
            '<span class="diff-badge add" id="execDiffAdd">+0</span>' +
            '<span class="diff-badge del" id="execDiffDel">-0</span>' +
            '<span class="diff-caret">&#8250;</span>' +
          '</div>' +
          '<div class="exec-diff-files" id="execDiffFiles"></div>' +
        '</div>' +
      '</div>';

    getThreadItems(t.id).forEach(it => chatStream.appendChild(renderThreadItem(it)));

    const stageSelEl = document.getElementById('taskStageSelect');
    const stageMoveStatusEl = document.getElementById('taskStageMoveStatus');
    if (stageSelEl) {
      stageSelEl.addEventListener('change', () => {
        moveTaskStage(t.id, stageSelEl.value, stageMoveStatusEl, stageSelEl);
      });
    }
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
    loadTaskThreadContext(t.id);
  }

  function renderResearchControls(threadKey) {
    const folderCtl = document.getElementById('researchFolderCtl');
    const refsCtl = document.getElementById('researchRefsCtl');
    if (!folderCtl || !refsCtl) return;
    const meta = researchMeta(threadKey) || { id: threadKey, folder: '', refs: [] };

    // Folder / category select
    const folders = [...new Set(researchThreadIds().map(researchFolderName).filter(Boolean))].sort();
    const folderSel = document.createElement('select');
    folderSel.className = 'research-ctl-select';
    folderSel.id = 'researchFolderSelect';
    folderSel.title = 'Assign this research thread to a folder';
    const mkOpt = (val, label) => {
      const o = document.createElement('option');
      o.value = val; o.textContent = label;
      return o;
    };
    folderSel.appendChild(mkOpt('', '(unfiled)'));
    folders.forEach(f => folderSel.appendChild(mkOpt(f, '📁 ' + f)));
    folderSel.appendChild(mkOpt('__new__', '+ New folder…'));
    folderSel.value = folders.includes(meta.folder) ? meta.folder : (meta.folder ? '__new__' : '');
    folderSel.addEventListener('change', () => {
      if (folderSel.value === '__new__') {
        folderInput.style.display = '';
        folderInput.focus();
      } else {
        updateResearchThread(threadKey, { folder: folderSel.value });
      }
    });
    const folderInput = document.createElement('input');
    folderInput.type = 'text';
    folderInput.className = 'research-ctl-input';
    folderInput.id = 'researchFolderInput';
    folderInput.placeholder = meta.folder && !folders.includes(meta.folder) ? meta.folder : 'Folder name…';
    folderInput.value = meta.folder && !folders.includes(meta.folder) ? meta.folder : '';
    folderInput.style.display = folderSel.value === '__new__' ? '' : 'none';
    folderInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        e.preventDefault();
        const name = folderInput.value.trim();
        updateResearchThread(threadKey, { folder: name });
      }
    });
    folderCtl.appendChild(folderSel);
    folderCtl.appendChild(folderInput);

    // Context refs: chips + add input + fork-from select
    const chipWrap = document.createElement('span');
    chipWrap.className = 'ref-chip-wrap';
    chipWrap.id = 'researchRefChips';
    (meta.refs || []).forEach(ref => {
      const chip = document.createElement('span');
      chip.className = 'ref-chip';
      chip.setAttribute('data-ref', ref);
      chip.textContent = (ref.startsWith('T-') ? 'Ref: ' : 'Fork: ') + ref + ' ';
      const rm = document.createElement('button');
      rm.type = 'button';
      rm.className = 'ref-chip-x';
      rm.textContent = '×';
      rm.title = 'Remove reference ' + ref;
      rm.addEventListener('click', () => {
        const next = (researchMeta(threadKey) || {}).refs || [];
        updateResearchThread(threadKey, { refs: next.filter(r => r !== ref) });
      });
      chip.appendChild(rm);
      chipWrap.appendChild(chip);
    });
    const refInput = document.createElement('input');
    refInput.type = 'text';
    refInput.className = 'research-ctl-input ref-input';
    refInput.id = 'researchRefInput';
    refInput.placeholder = 'Ref: T-013 or research-001';
    refInput.title = 'Link a task (T-NNN) or research thread; its summary is injected into the prompt';
    refInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        e.preventDefault();
        const n = normalizeRefId(refInput.value);
        if (!n || n === threadKey) return;
        const cur = (researchMeta(threadKey) || {}).refs || [];
        if (!cur.includes(n)) updateResearchThread(threadKey, { refs: cur.concat([n]) });
      }
    });
    chipWrap.appendChild(refInput);
    const forkSel = document.createElement('select');
    forkSel.className = 'research-ctl-select';
    forkSel.id = 'researchForkSelect';
    forkSel.title = 'Fork from an existing research thread';
    forkSel.appendChild(mkOpt('', 'Fork from…'));
    researchThreadIds().filter(id => id !== threadKey).forEach(id => {
      forkSel.appendChild(mkOpt(id, (researchMeta(id) && researchMeta(id).name) || id));
    });
    forkSel.addEventListener('change', () => {
      const target = normalizeRefId(forkSel.value);
      if (!target) return;
      const cur = (researchMeta(threadKey) || {}).refs || [];
      const fields = { fork_from: target };
      if (!cur.includes(target)) fields.refs = cur.concat([target]);
      updateResearchThread(threadKey, fields);
    });
    chipWrap.appendChild(forkSel);
    refsCtl.appendChild(chipWrap);
  }

  async function loadTaskThreadContext(taskId) {
    const res = await fetchJSON('/api/task/context?project=' + encodeURIComponent(state.currentProject) + '&id=' + encodeURIComponent(taskId));
    if (!res || !res.ok || state.inspectorTaskId !== taskId) return;
    const workedDetailEl = document.getElementById('chatWorkedDetail');
    if (workedDetailEl && Array.isArray(res.recent_log) && res.recent_log.length) {
      workedDetailEl.textContent = res.recent_log.join(String.fromCharCode(10));
    }
    const wtBadge = document.getElementById('taskWorktreeStatus');
    if (wtBadge && res.worktree_status) {
      wtBadge.textContent = res.worktree_status.status || (res.worktree_status.exists ? 'active' : 'not created');
    }
    const taskData = res.task || {};
    const depEl = document.getElementById('taskDependsOn');
    if (depEl && taskData.depends) {
      depEl.textContent = taskData.depends;
    }
    const goalEl = document.getElementById('taskContractGoal');
    if (goalEl && taskData.goal) {
      goalEl.innerHTML = '<strong>Goal:</strong> ' + escapeHTML(taskData.goal);
    }
    const allowedListEl = document.getElementById('taskAllowedList');
    if (allowedListEl && Array.isArray(taskData.allowed_files) && taskData.allowed_files.length) {
      allowedListEl.innerHTML = taskData.allowed_files.map(f => '<li><code>' + escapeHTML(f) + '</code></li>').join('');
    }
    const critListEl = document.getElementById('taskCriteriaList');
    if (critListEl && Array.isArray(taskData.criteria) && taskData.criteria.length) {
      critListEl.innerHTML = taskData.criteria.map(c =>
        '<li>' + escapeHTML((c.id ? c.id + ': ' : '') + (c.text || c)) + '</li>'
      ).join('');
    }
  }

  async function loadInspectorGit() {
    const textEl = document.getElementById('execDiffText');
    const addEl = document.getElementById('execDiffAdd');
    const delEl = document.getElementById('execDiffDel');
    const filesEl = document.getElementById('execDiffFiles');
    if (!textEl || !addEl || !delEl || !filesEl) return;
    const res = await fetchJSON('/api/project/git?project=' + encodeURIComponent(state.currentProject));
    if (!textEl.isConnected) return;
    let files = [];
    let adds = 0;
    let dels = 0;
    if (res && res.ok && res.is_git) {
      const m = (res.diffstat || '').match(/([0-9]+) +files? +changed(?:, +([0-9]+) +insertions?\([+]\))?(?:, +([0-9]+) +deletions?\([-]\))?/);
      if (m) {
        adds = parseInt(m[2] || '0', 10);
        dels = parseInt(m[3] || '0', 10);
      }
      files = (res.changed || []).map(l => l.replace(/^[ MADRCU?!]{1,3}/, '').trim()).filter(Boolean).slice(0, 30);
      const n = files.length || (m ? parseInt(m[1], 10) : 0);
      textEl.textContent = n + ' file' + (n === 1 ? '' : 's') + ' changed';
    } else if (res && res.ok) {
      textEl.textContent = 'not a git repository';
    } else {
      textEl.textContent = 'diff unavailable';
    }
    addEl.textContent = '+' + adds;
    delEl.textContent = '-' + dels;
    filesEl.innerHTML = files.length
      ? files.map(f => '<span class="diff-file" data-path="' + escapeHTML(f) + '" title="' + escapeHTML(f) + '">' + escapeHTML(f) + '</span>').join('')
      : '<span class="diff-file-none">No uncommitted changes vs HEAD.</span>';
    filesEl.querySelectorAll('.diff-file').forEach(el => {
      el.addEventListener('click', () => openExplorerFile(state.currentProject, el.dataset.path));
    });
  }

  const CHAT_TIMEOUT_MS = 30000;

  async function sendChatMessage() {
    if (!chatInput || !chatStream) return;
    const text = chatInput.value.trim();
    if (!text) return;
    const threadKey = state.inspectorTaskId || 'research';
    const items = getThreadItems(threadKey);
    const userItem = { type: 'message', role: 'user', content: text };
    items.push(userItem);
    chatStream.appendChild(renderThreadItem(userItem));
    chatInput.value = '';

    const messages = items
      .filter(it => it.type === 'message' && !it.error)
      .map(it => ({ role: it.role, content: it.content }));

    const toolKey = state.chatPlatform || 'devin';
    const modelId = state.chatModel || (currentChatModel() && currentChatModel().id) || 'swe-2-high';
    const isResearch = isResearchThread(threadKey);
    let refsForBody = [];
    if (isResearch) {
      const found = extractRefsFromText(text);
      const cur = ((researchMeta(threadKey) || {}).refs || []).slice();
      const merged = cur.concat(found.filter(r => !cur.includes(r) && r !== threadKey));
      refsForBody = merged.filter(r => r !== threadKey);
      if (found.length && merged.length !== cur.length) {
        updateResearchThread(threadKey, { refs: refsForBody });
      }
    }
    const thinkingEl = document.createElement('div');
    thinkingEl.className = 'chat-bubble assistant thinking';
    thinkingEl.innerHTML =
      '<span class="thinking-dots" aria-hidden="true"><span></span><span></span><span></span></span>' +
      '<span class="thinking-label">Thinking via ' + escapeHTML(platformLabel(toolKey)) + ' (' + escapeHTML(modelId) + ')...</span>';
    chatStream.appendChild(thinkingEl);
    chatStream.scrollTop = chatStream.scrollHeight;

    if (btnChatSend) btnChatSend.disabled = true;
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), CHAT_TIMEOUT_MS);

    let assistantItem;
    try {
      const resp = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          project: state.currentProject,
          tool: toolKey,
          model: modelId,
          thread: threadKey,
          messages: messages,
          refs: refsForBody,
          persist: isResearch,
        }),
        signal: controller.signal,
      });
      const data = await resp.json().catch(() => null);
      if (resp.ok && data && data.ok) {
        assistantItem = {
          type: 'message',
          role: 'assistant',
          content: data.reply || '(empty response)',
          model: data.model || modelId,
          tool: data.tool || toolKey,
          usage: data.usage || null,
        };
      } else {
        const errText = (data && data.error)
          ? data.error
          : ('Chat execution failed (HTTP ' + resp.status + ')');
        assistantItem = {
          type: 'message',
          role: 'assistant',
          error: true,
          content: 'Error [' + platformLabel(toolKey) + ']: ' + errText,
        };
      }
    } catch (err) {
      const isTimeout = err && err.name === 'AbortError';
      const msg = isTimeout
        ? ('CLI execution timed out after 30s (' + platformLabel(toolKey) + ' / ' + modelId + ').')
        : ('Unable to reach /api/chat: ' + (err && err.message ? err.message : 'network error'));
      assistantItem = {
        type: 'message',
        role: 'assistant',
        error: true,
        content: msg,
      };
    } finally {
      clearTimeout(timeoutId);
      if (btnChatSend) btnChatSend.disabled = false;
      if (thinkingEl.parentNode) thinkingEl.parentNode.removeChild(thinkingEl);
    }

    items.push(assistantItem);
    if ((state.inspectorTaskId || 'research') === threadKey) {
      chatStream.appendChild(renderThreadItem(assistantItem));
      chatStream.scrollTop = chatStream.scrollHeight;
    }
  }

  // --- Chat model selector ---
  function chatModelList() {
    return state.chatModels && state.chatModels.length ? state.chatModels : CHAT_MODELS;
  }

  function currentChatModel() {
    const list = chatModelList();
    return list.find(m => m.id === state.chatModel) || list[0];
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
    const p = state.platformData[state.chatPlatform];
    if (p && !(p.models || []).length) {
      const info = document.createElement('div');
      info.className = 'model-option model-empty';
      info.textContent = `${p.status_label || 'Unavailable'}: ${p.note || 'no models reported'} — pick another platform`;
      chatModelDropdown.appendChild(info);
    }
    chatModelList().forEach(m => {
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
    state.chatModels = CHAT_MODELS.slice();
    try {
      const savedPlatform = sessionStorage.getItem('af_chat_platform');
      if (savedPlatform && CHAT_PLATFORMS.some(p => p.key === savedPlatform)) {
        state.chatPlatform = savedPlatform;
      }
      const saved = sessionStorage.getItem('af_chat_model');
      if (saved && chatModelList().some(m => m.id === saved)) state.chatModel = saved;
    } catch (err) { /* storage unavailable */ }
    updateChatPlatformPill();
    renderPlatformDropdown();
    updatePlatformStatusPill();
    updateChatModelPill();
    renderModelDropdown();
    chatModelPill.addEventListener('click', (ev) => {
      ev.stopPropagation();
      chatModelSelector.classList.toggle('open');
    });
    if (chatPlatformPill && chatPlatformSelector) {
      chatPlatformPill.addEventListener('click', (ev) => {
        ev.stopPropagation();
        chatPlatformSelector.classList.toggle('open');
      });
    }
    document.addEventListener('click', (ev) => {
      if (!chatModelSelector.contains(ev.target)) {
        chatModelSelector.classList.remove('open');
      }
      if (chatPlatformSelector && !chatPlatformSelector.contains(ev.target)) {
        chatPlatformSelector.classList.remove('open');
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
