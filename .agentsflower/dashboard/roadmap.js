// ===== Roadmap page: three views (cards / journey / matrix) over the shared payload =====
// Facts stay separate: declared status (plan), local task counts (ledger),
// exit-criteria evidence (authored records). Task filters slice only the
// execution data - every declared stage renders regardless of the filters.
const R=(function(){
  const esc=C.esc, col=C.col, ST_ORDER=C.ST_ORDER;
  const mut=s=>`<span class="mut">${s}</span>`;
  const tag=s=>`<span class="tag" style="background:${col(s)}">${s}</span>`;
  const DECL={"Current":"--s-work","Planned":"--s-ready","Closed":"--s-done"};
  const EV={"pass":"--s-done","fail":"--s-rej","stale":"--s-block","pending":"--s-ready","unknown":"--s-canc"};
  const EV_ORDER=["pass","fail","stale","pending","unknown"];
  const BUCKET_OF={"done":"accepted","in progress":"active","review":"review","blocked":"blocked",
                   "ready":"ready","rejected":"rejected","cancelled":"cancelled"};

  // ---- derived stage data (presentation only; payload fields are untouched) ----
  function prepStages(DATA,byId){
    (DATA.stages||[]).forEach(s=>{
      s.tasks=(s.taskIds||[]).map(id=>byId[id]).filter(Boolean);
      s.blockers=s.tasks.filter(t=>!t.final&&((t.blockedBy&&t.blockedBy.length)||t.waitsOwner));
      s.warns=[];
      if(s.duplicate) s.warns.push("duplicate stage id in the plan - not resolved; its tasks stay in the Unmapped group");
      (s.diagnostics||[]).forEach(w=>s.warns.push(w));
    });
  }
  const unmappedTasks=(DATA,byId)=>((DATA.diagnostics||{}).unmappedTaskIds||[]).map(id=>byId[id]).filter(Boolean);

  // ---- shared fact renderers: three separate facts per stage ----
  function countsHtml(tasks,total){
    const c={}; tasks.forEach(t=>c[t.status]=(c[t.status]||0)+1);
    const chips=ST_ORDER.filter(k=>c[k]).map(k=>`<span class="cchip"><i style="background:${col(k)}"></i>${k} ${c[k]}</span>`).join(" ");
    const other=tasks.filter(t=>!ST_ORDER.includes(t.status)).length;
    if(!tasks.length) return total?`<b>0 of ${total}</b> shown · ${mut("all filtered out")}`:`<b>No local tasks</b>`;
    const shown=total!==undefined&&total!==tasks.length?`<b>${tasks.length} of ${total}</b> shown · `:"";
    return shown+chips+(other?` <span class="cchip">other ${other}</span>`:"");
  }
  function evChips(stage){
    const cv=stage.coverage||{};
    if(cv.kind!=="authored") return `<b>not tracked per criterion</b> ${mut("(unstructured exit criteria — coverage unknown)")}`;
    const st=cv.states||{};
    const parts=EV_ORDER.filter(k=>st[k]).map(k=>`<span class="evchip" style="background:var(${EV[k]})">${k} ${st[k]}</span>`).join(" ");
    return (parts||mut("none recorded"))+" "+mut(`(${cv.total} declared criteria)`);
  }
  function declaredHtml(s){
    const lbl=s.declared||(s.declaredRaw?"not recognized":"not declared");
    const raw=s.declared&&s.declaredRaw&&s.declaredRaw.toLowerCase()!==String(s.declared).toLowerCase()
      ?" "+mut(`(plan: "Status: ${esc(s.declaredRaw)}")`)
      :(!s.declared&&s.declaredRaw?" "+mut(`(plan: "Status: ${esc(s.declaredRaw)}")`):"");
    return `<span class="tag decl" style="background:var(${DECL[s.declared]||"--s-canc"})">${esc(lbl)}</span>${raw}`
      +(s.recurring?` <span class="cchip">recurring: ${esc(s.recurring.kind||"")}</span>`:"");
  }
  function factsHtml(s,shown){
    return `<div class="facts">
      <div class="fact"><span class="fl">Declared status</span><span class="fv">${declaredHtml(s)}</span></div>
      <div class="fact"><span class="fl">Local tasks</span><span class="fv">${countsHtml(shown,s.tasks.length)}</span></div>
      <div class="fact"><span class="fl">Exit-criteria evidence</span><span class="fv">${evChips(s)}</span></div>
    </div>`;
  }
  function warnsHtml(s){
    return (s.warns||[]).map(w=>`<div class="warn">⚠ ${esc(w)}</div>`).join("");
  }
  function blockersHtml(s){
    const parts=[];
    s.tasks.forEach(t=>{ if(!t.final&&t.status!=="Blocked"&&(t.status==="In progress"||t.status==="In review"||t.status==="Ready"))
      parts.push(`<a data-go="${t.id}">${t.id}</a> ${mut("("+t.status.toLowerCase()+")")}`); });
    const active=parts.length?`<div class="blk"><b>Active work:</b> ${parts.join(" · ")}</div>`:"";
    if(!s.blockers.length) return active;
    const bl=s.blockers.map(t=>{const w=[]; if(t.blockedBy&&t.blockedBy.length)w.push("waits on "+t.blockedBy.join(", ")); if(t.waitsOwner)w.push("waits on the owner"); return `<a data-go="${t.id}">${t.id}</a> ${mut("("+w.join("; ")+")")}`;});
    return active+`<div class="blk"><b>Active blockers:</b> ${bl.join(" · ")}</div>`;
  }
  function refHtml(ref,kind,exists,href){
    if(!ref) return "";
    if(kind==="url") return ` · ${mut("ref")} <code>${esc(ref)}</code><span class="ev-ext" title="external reference — displayed as recorded, never fetched or verified locally">ext</span>`;
    if(kind==="invalid") return ` · ${mut("ref")} <code>${esc(ref)}</code> ${mut("(rejected)")}`;
    if(exists===false) return ` · ${mut("ref")} <code>${esc(ref)}</code> ${mut("(not found under the project root)")}`;
    if(href) return ` · ${mut("ref")} <a class="src" href="${esc(href)}">${esc(ref)}</a>`;
    return ` · ${mut("ref")} <code>${esc(ref)}</code>`;
  }
  function evidenceTable(s){
    if(!s.criteria) return "";
    const rows=s.criteria.map(c=>{const e=c.evidence||{state:"unknown"};
      return `<tr><td><b>${esc(c.id)}</b></td><td>${esc(c.text)}</td>
        <td><span class="evchip" style="background:var(${EV[e.state]||"--s-canc"})">${esc(e.state)}</span>${e.external?'<span class="ev-ext" title="external reference — displayed as recorded, not verified locally">ext</span>':""}${e.state==="stale"?'<span class="stalemark" title="recorded evidence is stale — not a current pass"> stale</span>':""}</td>
        <td>${esc(e.label||"")}${e.supersededBy?`<br>${mut("superseded by "+esc(e.supersededBy))}`:""}<br>${mut(esc(e.provenance||""))}${e.recorded?mut(" · recorded "+esc(e.recorded)):""}${e.artifact?mut(" · artifact "+esc(e.artifact)):""}${refHtml(e.ref,e.refKind,e.refExists,e.refHref)}</td></tr>`;}).join("");
    return `<details class="fold"><summary>Evidence detail · ${s.criteria.length} criteria</summary><div class="tablewrap"><table class="tmini"><thead><tr><th>ID</th><th>Criterion</th><th>State</th><th>Recorded evidence</th></tr></thead><tbody>${rows}</tbody></table></div></details>`;
  }
  function extrasHtml(s){
    let h="";
    const n=(s.exitCriteria||"").split("\n").length;
    if(s.exitCriteria) h+=`<details class="fold"><summary>Exit criteria — full text · ${n} line${n===1?"":"s"}</summary><pre class="rawtext">${esc(s.exitCriteria)}</pre></details>`;
    h+=evidenceTable(s);
    if(s.recurring){
      const cys=(s.recurring.cycles||[]).map(c=>`<div class="cy"><b>${esc(c.id||"(no cycle id)")}</b> — ${esc(c.result||"not recorded")} ${mut("recorded "+esc(c.recorded||"unknown"))}${refHtml(c.ref,c.refKind,c.refExists,c.refHref)}${c.note?"<br>"+mut(esc(c.note)):""}</div>`).join("");
      h+=`<div class="cycles"><b>Recurring: ${esc(s.recurring.kind||"")}</b> ${mut("— "+esc(s.recurring.note||""))}<br>${cys||mut("no recorded cycles")}</div>`;
    }
    if(s.historicalRefs){
      h+=`<div class="blk"><b>Historical references:</b> ${s.historicalRefs.map(r=>`${esc(r.label)} ${mut("— "+esc(r.note||""))}`).join("<br>")}</div>`;
    }
    return h;
  }
  function taskTable(tasks,total,flag){
    if(!total) return "";
    const rows=tasks.map(t=>`<tr class="row" tabindex="0" data-go="${t.id}"><td><b>${t.id}</b></td><td>${esc(t.title)}${flag&&flag(t)?'<span class="flag">🔎 in text</span>':""}</td><td>${esc(t.role)}</td><td>${tag(t.status)}</td><td class="pill">${esc(t.result)}</td><td class="pill">${esc(t.check)}</td><td class="pill">${esc(t.updated)}</td></tr>`).join("")
      ||`<tr><td colspan="7" class="empty">No tasks match the filters (${total} in stage)</td></tr>`;
    return `<details class="fold" open><summary>Tasks · ${tasks.length===total?total:tasks.length+" of "+total} shown</summary><div class="tablewrap"><table class="tmini"><thead><tr><th>ID</th><th>Title</th><th>Role</th><th>Status</th><th>Outcome</th><th>Check</th><th>Updated</th></tr></thead><tbody>${rows}</tbody></table></div></details>`;
  }

  // ---- execution records for the drill-down: attempts, routing, gate evidence ----
  const unk=v=>(v===undefined||v===null||v==="")?mut("unknown"):esc(v);
  const txt=v=>(v===undefined||v===null||v==="")?"unknown":String(v);
  function attemptRow(a){
    const ident=(a.requestedModel||a.requestedEffort||a.effectiveModel||a.effectiveEffort)
      ?`requested ${esc(txt(a.requestedModel))}${a.requestedEffort?"·"+esc(a.requestedEffort):""} → effective ${esc(txt(a.effectiveModel))}${a.effectiveEffort?"·"+esc(a.effectiveEffort):""}`
      :mut("model identity not recorded");
    return `<tr><td>#${esc(txt(a.n))}</td>
      <td>${esc(txt(a.tool))}${a.role?" · "+esc(a.role):""}${a.manual?" · manual":""}</td>
      <td>${esc(txt(a.status))}${a.exitCode!==undefined&&a.exitCode!==null?" · exit "+esc(a.exitCode):""}${a.stopReason?" · "+esc(a.stopReason):""}${a.limitHit?" · limit hit":""}</td>
      <td>${ident}</td>
      <td>${esc(txt(a.startedAt))} → ${a.finishedAt?esc(a.finishedAt):"—"}</td>
      <td>${a.logRef?`<code>${esc(a.logRef)}</code>`:mut("—")}</td></tr>`;
  }
  function attemptsHtml(t){
    if(t.attempts===null||t.attempts===undefined) return `<div class="rtitle">Attempts</div>`+mut("not recorded");
    if(!t.attempts.length) return `<div class="rtitle">Attempts</div>`+mut("none recorded");
    const notes=t.attempts.filter(a=>a.note).map(a=>`<div class="mut">attempt ${esc(txt(a.n))}: ${esc(a.note)}</div>`).join("");
    const dls=t.attempts.filter(a=>a.deadline||a.workerTimeout||a.target).map(a=>`<div class="mut">attempt ${esc(txt(a.n))}:${a.workerTimeout?" worker timeout "+esc(a.workerTimeout)+"s":""}${a.deadline?" deadline "+esc(a.deadline):""}${a.target?" target "+esc(a.target):""}</div>`).join("");
    return `<div class="rtitle">Attempts · recorded history (${t.attempts.length})</div>
      <div class="tablewrap"><table class="tmini rtab"><thead><tr><th>#</th><th>Tool</th><th>Result</th><th>Model</th><th>Started → finished</th><th>Log</th></tr></thead>
      <tbody>${t.attempts.map(attemptRow).join("")}</tbody></table></div>${notes}${dls}`;
  }
  function kvPairs(o,keys){
    if(!o||typeof o!=="object") return "";
    return keys.filter(k=>o[k]!==undefined&&o[k]!==null&&o[k]!=="").map(k=>`${k} ${esc(String(o[k]))}`).join(" · ");
  }
  function assessHtml(a){
    const req=a.required?`required: effort ${esc(txt(a.required.effort))} · complexity ${esc(txt(a.required.complexity))}`:"";
    const floor=a.floor?kvPairs(a.floor,["option","tool","model","effort","resolvedModel","resolvedTier"]):"";
    const sel=a.selected?kvPairs(a.selected,["option","tool","model","effort","resolvedModel","resolvedEffort","resolvedTier"]):"";
    const avail=a.availability?kvPairs(a.availability,["at","source"]):"";
    const conf=kvPairs(a,["band","complexityConfidence","effortConfidence","optionConfidence","backupProbability"]);
    return `<tr><td>${esc(txt(a.at))}</td><td>${esc(txt(a.source))} · ${esc(txt(a.status))}${a.error?` · ${esc(a.error)}`:""}</td>
      <td>${esc(txt(a.tool))}${a.model?" · "+esc(a.model):""}${a.resolvedEffort||a.effort?" · "+esc(a.resolvedEffort||a.effort):""}${a.applied===true?" · applied":""}${a.applied===false?" · not applied":""}</td>
      <td>${req?`<div><span class="mut">assessment:</span> ${req}</div>`:""}${floor?`<div><span class="mut">floor:</span> ${floor}</div>`:""}${sel?`<div><span class="mut">selection:</span> ${sel}</div>`:""}${avail?`<div><span class="mut">availability:</span> ${avail}</div>`:""}${conf?`<div><span class="mut">confidence:</span> ${conf}</div>`:""}${a.selectionReason?`<div><span class="mut">reason:</span> ${esc(a.selectionReason)}</div>`:""}${a.escalation?`<div><span class="mut">escalation:</span> ${esc(a.escalation)}</div>`:""}</td></tr>`;
  }
  function routeEventHtml(e){
    const ad=e.admitted?kvPairs(e.admitted,["tool","model","effort","tier","option"]):"";
    return `<tr><td>${esc(txt(e.at))}</td><td>${esc(txt(e.event))}</td><td>${ad||mut("—")}${e.deviation?" · deviation":""}${e.reason?` · ${esc(e.reason)}`:""}${e.note?` · ${esc(e.note)}`:""}</td></tr>`;
  }
  function routingHtml(t){
    if(t.routing===null||t.routing===undefined) return `<div class="rtitle">Routing</div>`+mut("not recorded");
    const r=t.routing, as=r.assessments||[], ev=r.events||[];
    if(!as.length&&!ev.length) return `<div class="rtitle">Routing</div>`+mut("no exportable records");
    return `<div class="rtitle">Routing · assessment / floor / selection / availability</div>
      ${as.length?`<div class="tablewrap"><table class="tmini rtab"><thead><tr><th>At</th><th>Source · status</th><th>Choice</th><th>Assessment detail</th></tr></thead><tbody>${as.map(assessHtml).join("")}</tbody></table></div>`:""}
      ${ev.length?`<div class="tablewrap"><table class="tmini rtab"><thead><tr><th>At</th><th>Event</th><th>Admitted</th></tr></thead><tbody>${ev.map(routeEventHtml).join("")}</tbody></table></div>`:""}`;
  }
  function verifyHtml(t){
    if(t.verifications===null||t.verifications===undefined) return `<div class="rtitle">Gate evidence</div>`+mut("not recorded");
    if(!t.verifications.length) return `<div class="rtitle">Gate evidence</div>`+mut("none recorded");
    return `<div class="rtitle">Gate evidence · ${t.verifications.length} record${t.verifications.length===1?"":"s"}</div>`+t.verifications.map(v=>{
      const crit=v.criteria&&typeof v.criteria==="object"?Object.entries(v.criteria).map(([k,x])=>`<span class="evchip" style="background:var(${x==="pass"?"--s-done":x==="fail"?"--s-rej":"--s-ready"})">${esc(k)} ${esc(x)}</span>`).join(" "):"";
      const checks=(v.checks||[]).map(c=>`<div><code>${esc(c.cmd||"")}</code> → exit ${esc(txt(c.exit))}</div>`).join("");
      return `<div class="cy" style="border:1px solid var(--line);border-radius:8px;padding:5px 9px;margin:4px 0;background:var(--chip)">
        <b>#${esc(txt(v.n))}</b> ${esc(txt(v.at))} · attempt ${esc(txt(v.attempt))} · ${esc(txt(v.role))} · <b>${v.ok===true?"PASS":v.ok===false?"FAIL":"unknown"}</b>${v.sha?` · artifact <code>${esc(v.sha)}</code>${v.stale?' <span class="stalemark">STALE — not evidence for the current artifact</span>':""}`:""}${v.gate?` · ${esc(v.gate)}`:""}${v.logRef?` · <code>${esc(v.logRef)}</code>`:""}
        ${crit?`<div style="margin-top:3px">${crit}</div>`:""}${checks}${(v.problems||[]).length?`<div class="mut">problems: ${v.problems.map(esc).join(" · ")}</div>`:""}</div>`;
    }).join("");
  }
  function runtimeCard(t){
    return `<div class="tcard"><h2>Execution records · ${t.id} ${mut("— allowlisted fields only; absent stays unknown")}</h2>
      ${attemptsHtml(t)}${routingHtml(t)}${verifyHtml(t)}</div>`;
  }

  // ---- diagnostics + provenance: a build snapshot, never live monitoring ----
  function diagCard(DATA){
    const D=DATA.diagnostics||{sources:[],warnings:[],gaps:[],unmappedTaskIds:[]};
    const src=(D.sources||[]).map(s=>`<tr><td>${esc(s.file)}</td><td>${esc(s.mtime||"—")}</td><td>${esc(s.fingerprint||"—")}</td><td>${esc(s.status)}${s.detail?" · "+esc(s.detail):""}</td></tr>`).join("");
    return `<h2>Diagnostics — build snapshot</h2>
      <h3>Source freshness</h3>
      <div class="tablewrap"><table class="tmini"><thead><tr><th>Source</th><th>Modified</th><th>Fingerprint</th><th>Read</th></tr></thead><tbody>${src||'<tr><td colspan="4" class="empty">none</td></tr>'}</tbody></table></div>
      <div class="mut" style="font-size:11.5px;margin-top:4px">${esc(D.freshnessNote||"")}</div>
      ${(D.unmappedTaskIds||[]).length?`<h3>Unmapped tasks</h3><div class="mut" style="font-size:12px">${D.unmappedTaskIds.map(esc).join(", ")}</div>`:""}
      <h3>Warnings</h3>${(D.warnings||[]).length?`<ul>${D.warnings.map(w=>`<li>${esc(w)}</li>`).join("")}</ul>`:mut("none")}
      <h3>Known gaps</h3>${(D.gaps||[]).length?`<ul>${D.gaps.map(w=>`<li>${esc(w)}</li>`).join("")}</ul>`:mut("none")}`;
  }
  function provenanceCard(DATA){
    const P=DATA.provenance||{};
    return `<h2>Payload provenance</h2><div style="font-size:12px">
      ${Object.entries(P).map(([k,v])=>`<div><span class="mut">${esc(k)}:</span> ${esc(String(v))}</div>`).join("")}
    </div>`;
  }

  return {DECL,EV,EV_ORDER,BUCKET_OF,mut,tag,prepStages,unmappedTasks,countsHtml,evChips,declaredHtml,
          factsHtml,warnsHtml,blockersHtml,refHtml,evidenceTable,extrasHtml,taskTable,attemptsHtml,
          routingHtml,verifyHtml,runtimeCard,diagCard,provenanceCard};
})();
