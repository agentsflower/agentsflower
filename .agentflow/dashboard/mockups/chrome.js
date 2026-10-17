// ===== Shared mockup code (M namespace): header, filters, stage facts, task card, diagnostics =====
// The real filterbar.js is inlined above; the page templates each call M.* for their own view.
const M=(function(){
  const ST={"Cancelled":"--s-canc","Rejected":"--s-rej","Blocked":"--s-block","Ready":"--s-ready","In progress":"--s-work","In review":"--s-review","Done":"--s-done"};
  const ST_ORDER=Object.keys(ST), FINAL=new Set(["Done","Rejected","Cancelled"]);
  const DECL={"Current":"--s-work","Planned":"--s-ready","Closed":"--s-done"};
  const EV={"pass":"--s-done","fail":"--s-rej","stale":"--s-block","pending":"--s-ready","unknown":"--s-canc"};
  const col=s=>`var(${ST[s]||"--s-ready"})`;
  const esc=s=>String(s==null?"":s).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
  const sorted=a=>[...new Set(a)].sort((x,y)=>String(x).localeCompare(String(y),"en",{numeric:true}));
  const tag=s=>`<span class="tag" style="background:${col(s)}">${s}</span>`;
  const mut=s=>`<span class="mut">${s}</span>`;

  // ---- header: same chrome as the real pages, plus the proposed Roadmap nav item ----
  const SUN='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>';
  const MOON='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg>';
  function initHeader(generated,project){
    let saved=null; try{ saved=localStorage.getItem("dash-theme"); }catch(e){}
    if(saved) document.documentElement.dataset.theme=saved;
    const hdr=document.getElementById("hdr");
    hdr.className="topbar";
    hdr.innerHTML=`<h1>Tasks${project?" · "+esc(project):""}</h1><nav class="nav"><a href="../out/index.html">Overview</a><a href="../out/graph.html">Gantt &amp; timeline</a><a href="#" class="on" onclick="return false">Roadmap</a></nav><span class="sp"></span><span class="demobadge">MOCKUP &middot; synthetic fixture</span><span class="gen">Built ${esc(generated)}</span><button class="iconbtn" id="theme" type="button" aria-label="Toggle theme"></button>`;
    const btn=document.getElementById("theme");
    const isDark=()=>{ const t=document.documentElement.dataset.theme; return t?t==="dark":matchMedia("(prefers-color-scheme:dark)").matches; };
    const paint=()=>{ btn.innerHTML=isDark()?SUN:MOON; btn.title=isDark()?"Light theme":"Dark theme"; };
    btn.onclick=()=>{ const next=isDark()?"light":"dark"; document.documentElement.dataset.theme=next; try{ localStorage.setItem("dash-theme",next); }catch(e){} paint(); };
    paint();
  }

  // ---- data prep: attach tasks to stages, compute counts and evidence summaries ----
  function prep(DATA){
    const byId=Object.fromEntries(DATA.tasks.map(t=>[t.id,t]));
    DATA.stages.forEach(s=>{
      s.tasks=s.taskIds.map(id=>byId[id]).filter(Boolean);
      s.counts={}; ST_ORDER.forEach(k=>s.counts[k]=0);
      s.tasks.forEach(t=>s.counts[t.status]++);
      s.ev=evSummary(s);
      s.warn=s.declared==="Planned"&&s.tasks.length
        ?`Declared '${s.declaredRaw}' but the ledger lists ${s.tasks.length} task${s.tasks.length===1?"":"s"} — sources disagree; shown as recorded.`:"";
      s.blockers=s.tasks.filter(t=>!t.final&&(t.blockedBy.length||t.waitsOwner));
    });
    const unmapped=DATA.tasks.filter(t=>!DATA.stages.some(s=>s.taskIds.includes(t.id)));
    return {byId,unmapped};
  }
  function evSummary(stage){
    if(!stage.criteria||!stage.criteria.length) return {tracked:false};
    const s={tracked:true,total:stage.criteria.length,pass:0,fail:0,stale:0,pending:0,unknown:0};
    stage.criteria.forEach(c=>{const k=(c.evidence&&c.evidence.state)||"unknown"; s[k]=(s[k]||0)+1;});
    return s;
  }

  // ---- shared fact renderers: declared status / local task counts / evidence — three separate facts ----
  function countsHtml(tasks,total){
    const c={}; ST_ORDER.forEach(k=>c[k]=0); tasks.forEach(t=>c[t.status]++);
    const chips=ST_ORDER.filter(k=>c[k]).map(k=>`<span class="cchip"><i style="background:${col(k)}"></i>${k} ${c[k]}</span>`).join(" ");
    const shown=total!==undefined&&total!==tasks.length?`<b>${tasks.length} of ${total}</b> shown · `:"";
    return tasks.length?shown+chips:`<b>No local tasks</b>`;
  }
  function evChips(stage){
    const e=stage.ev;
    if(!e.tracked) return `<b>not tracked per criterion</b> ${mut("(unstructured exit criteria — coverage unknown)")}`;
    const parts=["pass","fail","stale","pending","unknown"].filter(k=>e[k]).map(k=>`<span class="evchip" style="background:var(${EV[k]})">${k} ${e[k]}</span>`).join(" ");
    return (parts||mut("none recorded"))+" "+mut(`(${e.total} declared criteria)`);
  }
  function factsHtml(stage,shownTasks){
    const rawNote=stage.declaredRaw&&stage.declaredRaw.toLowerCase()!==stage.declared.toLowerCase()
      ?" "+mut(`(plan: "Status: ${esc(stage.declaredRaw)}")`):"";
    return `<div class="facts">
      <div class="fact"><span class="fl">Declared status</span><span class="fv"><span class="tag decl" style="background:var(${DECL[stage.declared]||"--s-ready"})">${esc(stage.declared)}</span>${rawNote}${stage.recurring?` <span class="cchip">recurring: ${esc(stage.recurring.kind)}</span>`:""}</span></div>
      <div class="fact"><span class="fl">Local tasks</span><span class="fv">${countsHtml(shownTasks||stage.tasks,stage.tasks.length)}</span></div>
      <div class="fact"><span class="fl">Exit-criteria evidence</span><span class="fv">${evChips(stage)}</span></div>
    </div>`;
  }
  function blockersHtml(stage){
    if(!stage.blockers.length) return "";
    const parts=stage.blockers.map(t=>{const w=[]; if(t.blockedBy.length)w.push("waits on "+t.blockedBy.join(", ")); if(t.waitsOwner)w.push("waits on the owner"); return `<a data-go="${t.id}">${t.id}</a> ${mut("("+w.join("; ")+")")}`;});
    return `<div class="blk"><b>Active blockers:</b> ${parts.join(" · ")}</div>`;
  }
  function evidenceTable(stage){
    if(!stage.criteria) return "";
    const rows=stage.criteria.map(c=>{const e=c.evidence||{state:"unknown"};
      return `<tr><td><b>${esc(c.id)}</b></td><td>${esc(c.text)}</td>
        <td><span class="evchip" style="background:var(${EV[e.state]||"--s-canc"})">${esc(e.state)}</span>${e.external?'<span class="ev-ext" title="external reference — displayed as recorded, not verified locally">ext</span>':""}</td>
        <td>${esc(e.label||"")}${e.supersededBy?`<br>${mut(esc(e.supersededBy))}`:""}<br>${mut(esc(e.provenance||""))}${e.recorded?mut(" · recorded "+esc(e.recorded)):""}${e.artifact?mut(" · artifact "+esc(e.artifact)):""}</td></tr>`;}).join("");
    return `<details class="fold"><summary>Evidence detail · ${stage.criteria.length} criteria</summary><div class="tablewrap"><table class="tmini"><thead><tr><th>ID</th><th>Criterion</th><th>State</th><th>Recorded evidence</th></tr></thead><tbody>${rows}</tbody></table></div></details>`;
  }
  function extrasHtml(stage){
    let h="";
    const n=(stage.exitCriteria||"").split("\n").length;
    if(stage.exitCriteria) h+=`<details class="fold"><summary>Exit criteria — full text · ${n} line${n===1?"":"s"}</summary><pre class="rawtext">${esc(stage.exitCriteria)}</pre></details>`;
    h+=evidenceTable(stage);
    if(stage.recurring){
      const cys=stage.recurring.cycles.map(c=>`<div class="cy"><b>${esc(c.id)}</b> — ${esc(c.result)} ${mut("recorded "+esc(c.recorded)+(c.ref?" · "+esc(c.ref):""))}${c.note?"<br>"+mut(esc(c.note)):""}</div>`).join("");
      h+=`<div class="cycles"><b>Recurring: ${esc(stage.recurring.kind)}</b> ${mut("— "+esc(stage.recurring.note))}<br>${cys}</div>`;
    }
    if(stage.historicalRefs){
      h+=`<div class="blk"><b>Historical references:</b> ${stage.historicalRefs.map(r=>`${esc(r.label)} ${mut("— "+esc(r.note))}`).join("<br>")}</div>`;
    }
    return h;
  }
  function taskTable(tasks,total){
    if(!total) return "";
    const rows=tasks.map(t=>`<tr class="row" tabindex="0" data-go="${t.id}"><td><b>${t.id}</b></td><td>${esc(t.title)}</td><td>${esc(t.role)}</td><td>${tag(t.status)}</td><td class="pill">${esc(t.result)}</td><td class="pill">${esc(t.check)}</td><td class="pill">${esc(t.updated)}</td></tr>`).join("")
      ||`<tr><td colspan="7" class="empty">No tasks match the filters (${total} in stage)</td></tr>`;
    return `<details class="fold" open><summary>Tasks · ${tasks.length===total?total:tasks.length+" of "+total} shown</summary><div class="tablewrap"><table class="tmini"><thead><tr><th>ID</th><th>Title</th><th>Role</th><th>Status</th><th>Outcome</th><th>Check</th><th>Updated</th></tr></thead><tbody>${rows}</tbody></table></div></details>`;
  }

  // ---- condensed task card (drill-down target; production reuses C.taskCard) ----
  function taskCardLite(t,byId){
    const dd=(k,v)=>v?`<dt>${k}</dt><dd>${v}</dd>`:"";
    const link=id=>byId[id]?`<a data-go="${id}">${id}</a>`:esc(id);
    let verify="";
    if(t.role==="Developer"){
      verify=esc(t.check)+(t.checkedBy.length?"<br>"+t.checkedBy.map(c=>`${link(c.id)} — ${c.verdict||"no verdict"} ${mut("(verifies "+esc(c.sha)+(c.stale?" · STALE LINK":"")+"; tester task: "+esc(c.status)+")")}`).join("<br>"):"");
    }else if(t.verdict||t.verifies){
      verify=`This task is a check${t.verifies?" of "+link(t.verifies.task):""}${t.verdict?`; verdict: <b>${esc(t.verdict)}</b>`:""}`;
    }
    const att=t.attempts?t.attempts.map(a=>`#${a.n} ${esc(a.tool)}${a.model?" · "+esc(a.model):""} ${a.effective?mut("(effective: "+esc(a.effective)+")"):mut("(effective identity not recorded)")} · ${esc(a.start)} → ${a.finish?esc(a.finish):"—"} · ${esc(a.exit)}`).join("<br>")
      :mut("not recorded");
    return `<div class="tcard"><h2>Task ${t.id} ${mut("· mockup card")}</h2><dl>
      ${dd("Title",esc(t.title))}
      ${dd("Stage · role · agent",esc(t.stage+" · "+t.role+" · "+t.tool))}
      ${dd("Ledger status",tag(t.status))}
      ${dd("Outcome",esc(t.result)+(t.outcomeRaw?" "+mut(`(worker report — Outcome: ${esc(t.outcomeRaw)})`):t.outcomeSrc?"":mut(" (no worker report)")))}
      ${dd("Independent check",verify)}
      ${dd("Timing",mut("observed dates, not planned deadlines: ")+"created "+esc(t.created)+" · updated "+esc(t.updated))}
      ${dd("Depends on",t.deps.map(link).join(", "))}
      ${dd("Waits on",(t.blockedBy.length?t.blockedBy.map(link).join(", "):"")+(t.waitsOwner?(t.blockedBy.length?" · ":"")+"the owner":""))}
      ${dd("Attempts",att)}
      ${dd("Ledger commit / artifact",esc(t.commit||"—"))}
      ${dd("Notes",esc(t.notes))}
      ${dd("File","<code>"+esc(t.file)+"</code> "+mut("(synthetic path — shown as recorded)"))}
    </dl></div>`;
  }

  // ---- diagnostics panel ----
  function diagCard(DATA){
    const D=DATA.diagnostics;
    const src=D.sources.map(s=>`<tr><td>${esc(s.file)}</td><td>${esc(s.mtime)}</td><td>${esc(s.fingerprint)}</td><td>${esc(s.status)}</td></tr>`).join("");
    return `<h2>Diagnostics</h2>
      <h3>Source freshness</h3>
      <div class="tablewrap"><table class="tmini"><thead><tr><th>Source</th><th>Modified</th><th>Fingerprint</th><th>Read</th></tr></thead><tbody>${src}</tbody></table></div>
      <div class="mut" style="font-size:11.5px;margin-top:4px">${esc(D.freshnessNote)}</div>
      <h3>Warnings</h3><ul>${D.warnings.map(w=>`<li>${esc(w)}</li>`).join("")}</ul>
      <h3>Known gaps</h3><ul>${D.gaps.map(w=>`<li>${esc(w)}</li>`).join("")}</ul>`;
  }
  function provenanceCard(DATA){
    const P=DATA.provenance;
    return `<h2>Payload provenance</h2><div style="font-size:12px">
      ${Object.entries(P).map(([k,v])=>`<div><span class="mut">${esc(k)}:</span> ${esc(String(v))}</div>`).join("")}
    </div>`;
  }

  // ---- one filter set, wired through the real createFilterBar ----
  function mkFilters(T,onChange){
    const dims=[
      {k:"status",l:"Status",get:t=>[t.status],vals:()=>ST_ORDER},
      {k:"stage",l:"Stage",get:t=>[t.stage],vals:()=>sorted(T.map(t=>t.stage))},
      {k:"role",l:"Role",get:t=>[t.role],vals:()=>["Developer","Tester","Deployer"]},
      {k:"tool",l:"Agent",get:t=>[t.tool],vals:()=>sorted(T.map(t=>t.tool))},
      {k:"result",l:"Outcome",get:t=>[t.result],vals:()=>sorted(T.map(t=>t.result))},
      {k:"check",l:"Independent check",get:t=>[t.check],vals:()=>sorted(T.map(t=>t.check))}
    ];
    const sel={}; dims.forEach(d=>sel[d.k]=new Set());
    const flags={wait:false}; let query="",qBody=false;
    const hay=t=>(t.id+" "+t.title+" "+t.notes+" "+t.file+" "+t.commit).toLowerCase();
    function pass(t,skip){
      if(!dims.every(d=>d.k===skip||!sel[d.k].size||d.get(t).some(v=>sel[d.k].has(v)))) return false;
      if(flags.wait&&!(t.blockedBy.length||t.waitsOwner)) return false;
      if(query&&!query.split(/\s+/).every(w=>hay(t).includes(w))) return false;
      return true;
    }
    const fb=createFilterBar({
      bar:document.getElementById("fbar"),chosen:document.getElementById("fchosen"),sel,
      dims:dims.map(d=>({k:d.k,l:d.l,vals:d.vals,count:v=>T.filter(t=>d.get(t).includes(v)&&pass(t,d.k)).length})),
      flags:[{k:"wait",l:"Waits on something",get:()=>flags.wait,set:v=>{flags.wait=v}}],
      search:{placeholder:"Search: id, title, notes…",get:()=>query,set:v=>{query=v.trim().toLowerCase()}},
      body:{get:()=>qBody,set:v=>{qBody=v}},
      shown:()=>`Showing ${T.filter(t=>pass(t)).length} of ${T.length} tasks · stage list unaffected`,
      clear:()=>{dims.forEach(d=>sel[d.k].clear());flags.wait=false;query="";},
      onChange});
    return {fb,pass,filtered:()=>T.filter(t=>pass(t))};
  }

  // ---- task links inside rendered blocks ----
  function bindLinks(root,onGo){
    root.querySelectorAll("[data-go]").forEach(a=>{
      a.onclick=e=>{e.preventDefault();e.stopPropagation();onGo(a.dataset.go);};
      if(a.tagName==="TR")a.onkeydown=e=>{if(e.key==="Enter"){e.preventDefault();onGo(a.dataset.go);}};
    });
  }

  // ---- mockup self-check instrumentation (headless verification reads these) ----
  window.addEventListener("error",e=>{
    const d=document.getElementById("conlog")||(()=>{const x=document.createElement("div");x.id="conlog";document.body.appendChild(x);return x;})();
    d.dataset.err=((d.dataset.err||"")+e.message+" | ").slice(0,4000);
  });
  window.addEventListener("load",()=>{
    const d=document.documentElement; d.dataset.sw=d.scrollWidth; d.dataset.cw=d.clientWidth;
    const c=document.getElementById("conlog"); if(c&&!c.dataset.err)c.dataset.err="none";
  });

  return {ST,ST_ORDER,FINAL,DECL,EV,col,esc,sorted,tag,mut,initHeader,prep,evSummary,countsHtml,evChips,
          factsHtml,blockersHtml,evidenceTable,extrasHtml,taskTable,taskCardLite,diagCard,provenanceCard,
          mkFilters,bindLinks};
})();
