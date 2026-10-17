// ===== Shared code of both pages: constants, data prep, filter dimensions, header, task card =====
const C=(function(){
  const H=3600e3;
  const ST={"Cancelled":"--s-canc","Rejected":"--s-rej","Blocked":"--s-block","Ready":"--s-ready","In progress":"--s-work","In review":"--s-review","Done":"--s-done"};
  const ST_ORDER=Object.keys(ST), ORIGINS=["Owner","Orchestrator","Tester","Deployer"], FINAL=new Set(["Done","Rejected","Cancelled"]);
  const SIZES=["XL","L","M","S","docs","—"];
  const col=s=>`var(${ST[s]||"--s-ready"})`;
  const esc=s=>String(s==null?"":s).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
  const pad2=n=>String(n).padStart(2,"0");
  const fd=ms=>new Date(ms).toLocaleString("en-GB",{day:"2-digit",month:"2-digit",hour:"2-digit",minute:"2-digit"});
  const dm=ms=>{const d=new Date(ms);return pad2(d.getDate())+"."+pad2(d.getMonth()+1);};
  const dec=(x,n=1)=>x.toFixed(n);
  const fh=h=>h<1?Math.round(h*60)+" min":h<100?dec(h)+" h":dec(h/24)+" d";

  // ---- data: date parsing, edges, service fields ----
  function prep(DATA){
    const tasks=DATA.tasks, byId=Object.fromEntries(tasks.map(t=>[t.id,t]));
    tasks.forEach(t=>{ if(t.c===undefined){ t.c=Date.parse(t.createdAt); t.e=t.endAt?Date.parse(t.endAt):null; t.tl=t.timeline.map(([a,s])=>[Date.parse(a),s]); t.wk=(t.work||[]).map(Date.parse); t.bl=(t.body||"").toLowerCase(); } });
    const edges=DATA.edges.map(e=>({...e,a:e.t0?Date.parse(e.t0):null,b:e.t1?Date.parse(e.t1):null})).filter(e=>byId[e.from]&&byId[e.to]);
    const pings=DATA.pings.map(Date.parse).sort((x,y)=>x-y);
    const NOW=Math.max(Date.parse(DATA.now),pings[pings.length-1]);
    const TC=Math.min(...tasks.map(t=>t.c));
    // service fields for filters
    const chainN={}; tasks.forEach(t=>chainN[t.chain]=(chainN[t.chain]||0)+1);
    tasks.forEach(t=>{
      const dead=x=>["Rejected","Cancelled"].includes(byId[x].status), tags=[];
      if(edges.some(e=>e.kind==="dep"&&e.to===t.id&&e.b==null&&dead(e.from))) tags.push("depends on a rejected/cancelled task");
      if(edges.some(e=>e.kind==="dep"&&e.to===t.id&&e.b!=null)) tags.push("dependency was removed");
      if(edges.some(e=>e.kind==="succ"&&e.from===t.id)) tags.push("replaced by a successor");
      if(edges.some(e=>e.kind==="succ"&&e.to===t.id)) tags.push("replaces a predecessor");
      if(t.checkedBy&&t.checkedBy.length) tags.push("checked by a tester");
      if(chainN[t.chain]>1) tags.push("in a rework chain");
      if(t.blocks&&t.blocks.length) tags.push("blocks other tasks");
      t.relTags=tags; t.createdDay=dm(t.c); t.closedDay=t.e?dm(t.e):"not closed";
    });
    return {tasks,byId,edges,pings,NOW,TC};
  }
  // active time from commit pings (a gap longer than gapMin is not counted)
  function activeModel(pings,gapMin){
    const spans=[]; let a=pings[0], b=a;
    for(const p of pings.slice(1)){ if(p-b<=gapMin*60000) b=p; else { spans.push({a,b}); a=p; b=p; } }
    spans.push({a,b}); let c=0; spans.forEach(s=>{ s.cum=c; c+=(s.b-s.a)/H; }); const total=c;
    return t=>{ for(const s of spans){ if(t<=s.a) return s.cum; if(t<=s.b) return s.cum+(t-s.a)/H; } const l=spans[spans.length-1]; return total+Math.min((t-l.b)/H,gapMin/60); };
  }

  // ---- filter dimensions: identical on both pages ----
  const sorted=(vals)=>[...new Set(vals)].sort((x,y)=>String(x).localeCompare(String(y),"en",{numeric:true}));
  const dayKey=s=>{ const m=/^(\d\d)\.(\d\d)$/.exec(s); return m?(+m[2])*100+(+m[1]):9999; };
  function makeDims(tasks,statusOf){
    const one=(k,l,f,vals)=>({k,l,get:t=>[f(t)],vals:vals||(()=>sorted(tasks.map(f)))});
    return [
      one("status","Status",statusOf,()=>ST_ORDER),
      one("origin","Set by",t=>t.origin,()=>ORIGINS),
      one("stage","Stage",t=>t.stage),
      one("role","Role",t=>t.role,()=>["Developer","Tester","Deployer"]),
      one("tool","Agent",t=>t.tool),
      one("result","Outcome",t=>t.result),
      one("check","Independent check",t=>t.check),
      one("sizeCls","Size",t=>t.sizeCls,()=>SIZES),
      {k:"rel",l:"Links",get:t=>t.relTags.length?t.relTags:["no special links"],vals:()=>["depends on a rejected/cancelled task","dependency was removed","replaced by a successor","replaces a predecessor","checked by a tester","in a rework chain","blocks other tasks","no special links"]},
      one("created","Created",t=>t.createdDay,()=>sorted(tasks.map(t=>t.createdDay)).sort((x,y)=>dayKey(x)-dayKey(y))),
      one("closed","Closed",t=>t.closedDay,()=>sorted(tasks.map(t=>t.closedDay)).sort((x,y)=>dayKey(x)-dayKey(y)))
    ];
  }
  const matchDims=(t,dims,sel,skip)=>dims.every(d=>d.k===skip||!sel[d.k].size||d.get(t).some(v=>sel[d.k].has(v)));
  const flagMatch=(t,fl)=>(!fl.owner||t.waitsOwner)&&(!fl.blocked||(t.blockedBy.length&&!t.final));

  // ---- header and theme ----
  const SUN='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>';
  const MOON='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg>';
  function initHeader(active,generated,project,demo){
    let saved=null; try{ saved=localStorage.getItem("dash-theme"); }catch(e){}
    if(saved) document.documentElement.dataset.theme=saved;
    const hdr=document.getElementById("hdr");
    hdr.className="topbar";
    hdr.innerHTML=`<h1>Tasks${project?" · "+esc(project):""}</h1><nav class="nav"><a href="index.html"${active==="over"?' class="on"':""}>Overview</a><a href="graph.html"${active==="gantt"?' class="on"':""}>Gantt & timeline</a></nav><span class="sp"></span>${demo?'<span class="demobadge">DEMO DATA — not real project evidence</span>':""}<span class="gen">Built ${esc(generated)}</span><button class="iconbtn" id="theme" type="button" aria-label="Toggle theme"></button>`;
    const btn=document.getElementById("theme");
    const isDark=()=>{ const t=document.documentElement.dataset.theme; return t?t==="dark":matchMedia("(prefers-color-scheme:dark)").matches; };
    const paint=()=>{ btn.innerHTML=isDark()?SUN:MOON; btn.title=isDark()?"Light theme":"Dark theme"; };
    btn.onclick=()=>{ const next=isDark()?"light":"dark"; document.documentElement.dataset.theme=next; try{ localStorage.setItem("dash-theme",next); }catch(e){} paint(); };
    paint();
  }

  // ---- task card ----
  const rich=s=>esc(s).replace(/^([A-ZА-Я][^:\n]{1,42}:)(?=\s|$)/gm,"<b>$1</b>");
  function sizeShort(t){ const z=t.size; if(!z) return "no worker commits"; return t.sizeCls==="docs"?`docs only +${z.add} −${z.del}`:`${t.sizeCls} · code +${z.codeAdd} −${z.codeDel}`; }
  function sizeFull(t){ const z=t.size; if(!z) return '<span style="color:var(--mut)">'+(["Rejected","Cancelled"].includes(t.status)&&t.role==="Developer"?"branch deleted after "+(t.status==="Cancelled"?"cancellation":"rejection")+" — size cannot be recovered":"no worker commits ([T-NNN] in subject): testers, deploys and docs without code")+"</span>"; return `<b>${esc(t.sizeCls)}</b> · code: +${z.codeAdd} −${z.codeDel}, ${z.codeFiles} file(s)<br><span style="color:var(--mut)">with docs: +${z.add} −${z.del}, ${z.files} file(s) · commits: ${z.commits}<br>S &lt; 50, M &lt; 300, L &lt; 1000, XL ≥ 1000 lines of code</span>`; }
  function snippet(t,q){ if(!t.bl||!q) return ""; const w=q.toLowerCase().split(/\s+/).filter(Boolean)[0]; if(!w) return ""; const i=t.bl.indexOf(w); if(i<0) return ""; const body=t.body,a=Math.max(0,i-70),b=Math.min(body.length,i+w.length+110); return (a>0?"…":"")+esc(body.slice(a,i))+"<mark>"+esc(body.slice(i,i+w.length))+"</mark>"+esc(body.slice(i+w.length,b))+(b<body.length?"…":""); }
  // ctx: {byId, edges, NOW, dur(a,b), calDur(a,b), actDur(a,b), query, qBody}
  const MUT=s=>`<span style="color:var(--mut)">${s}</span>`;
  function taskCard(t,ctx){
    const link=id=>`<a href="#" data-go="${id}">${id}</a>`;
    const dd=(k,v)=>v?`<dt>${k}</dt><dd>${v}</dd>`:"";
    // original text, no paraphrase; empty fields are hidden
    const fold=(k,summary,txt)=>{ const s=(txt||"").trim(); if(!s) return ""; const n=s.split("\n").length; return `<dt>${k}</dt><dd><details class="fold"><summary>${summary} · ${n} line${n===1?"":"s"}</summary><pre class="rawtext">${esc(s)}</pre></details></dd>`; };
    const end=t.e!=null?t.e:ctx.NOW;
    const depsIn=ctx.edges.filter(e=>e.kind==="dep"&&e.to===t.id).sort((x,y)=>x.a-y.a);
    const depsOut=ctx.edges.filter(e=>e.kind==="dep"&&e.from===t.id);
    const succTo=ctx.edges.filter(e=>e.kind==="succ"&&e.from===t.id).map(e=>e.to), succFrom=ctx.edges.filter(e=>e.kind==="succ"&&e.to===t.id).map(e=>e.from);
    const checksOf=ctx.edges.filter(e=>e.kind==="check"&&e.from===t.id).map(e=>e.to);
    const hist=t.tl.map(([a,s],i)=>`<li><span class="tag" style="background:${col(s)}">${s}</span> ${fd(a)}${t.tl[i+1]?" · "+fh(ctx.dur(a,t.tl[i+1][0]))+" in this status":""}</li>`).join("");
    const deadNow=x=>["Rejected","Cancelled"].includes(ctx.byId[x].status);
    // three separate things: ledger status / worker outcome / independent check
    const outcome=t.outcomeSrc
      ? `${esc(t.result)} ${MUT(`(worker report — ${t.outcomeSrc}: ${esc(t.outcomeRaw)})`)}`+(t.result==="Completed by worker"?"<br>"+MUT("The worker reported the work done. This is not acceptance: the decision is the ledger status."):"")
      : MUT("no worker report (Result section is empty)");
    let verify="";
    if(t.role==="Developer"){
      const list=(t.checkedBy||[]).map(c=>`${link(c.id)} — ${c.verdict||"no verdict"} ${MUT("(verifies "+c.sha+(c.stale?" · STALE LINK":"")+"; tester task: "+c.status+")")}`);
      verify=esc(t.check)+(list.length?"<br>"+list.join("<br>"):"");
    } else if(t.verdict||checksOf.length){
      verify=`This task is a check${checksOf.length?" of "+checksOf.map(link).join(", "):""}${t.verdict?`; verdict: <b>${esc(t.verdict)}</b>`:""}`;
    }
    const rc=t.reportCommit;
    return `<div class="tcard"><h2>Task ${t.id}${t.sizeCls&&t.sizeCls!=="—"?`<span class="tag sz" title="${esc(sizeShort(t))}">${esc(t.sizeCls)}</span>`:""}</h2><dl>
      ${dd("Title",esc(t.title))}
      ${ctx.query&&ctx.qBody?dd("Found in text",snippet(t,ctx.query)):""}
      ${dd("Stage · role · agent",esc(t.stage+" · "+t.role+" · "+t.tool))}
      ${dd("Set by",esc(t.origin)+" "+MUT(`— ${esc(t.originWhy)} (estimate)`))}
      ${dd("Ledger status",`<span class="tag" style="background:${col(t.status)}">${t.status}</span>`)}
      ${dd("Outcome",outcome)}
      ${dd("Independent check",verify)}
      ${dd("Timing",`created ${fd(t.c)} → ${t.e!=null?"closed "+fd(t.e):"not closed"}; calendar ${fh(ctx.calDur(t.c,end))}, active ${fh(ctx.actDur(t.c,end))}`)}
      ${fold("Full assignment","Goal",t.goalFull)}
      ${fold("Worker report","Result",t.resultFull)}
      ${fold("Notes","Notes",t.notes)}
      ${dd("Depends on",depsIn.map(e=>`${link(e.from)} ${MUT(`(${ctx.byId[e.from].status}${deadNow(e.from)?", no longer active":""}) — from ${fd(e.a)}${e.b!=null?" to "+fd(e.b)+" · removed":""}`)}`).join("<br>"))}
      ${dd("Blocks",depsOut.map(e=>link(e.to)+(e.b!=null?" "+MUT("(removed)"):"")).join(", "))}
      ${dd("Replaces",succFrom.map(link).join(", "))}
      ${dd("Replaced by",succTo.length?succTo.map(link).join(", "):(["Rejected","Cancelled"].includes(t.status)?MUT("not recorded in the ledger"):""))}
      ${dd("Status history","<ul>"+hist+"</ul>")}
      ${dd("Commit / artifact in ledger",esc(t.commit))}
      ${rc?dd("Commit named in the worker report",`<code>${esc(rc.sha)}</code> ${MUT(`(report line "${esc(rc.label)}" ${esc(rc.line)}) · does not mean the commit is accepted into main`)}`):""}
      ${dd("Change size",sizeFull(t))}
      ${t.file?dd("File",`<a href="${esc(t.fileHref)}">${esc(t.file)}</a>`):""}
    </dl></div>`;
  }
  function bindCard(root,onGo){
    root.querySelectorAll("a[data-go]").forEach(a=>a.onclick=e=>{ e.preventDefault(); onGo(a.dataset.go); });
  }
  return {H,ST,ST_ORDER,ORIGINS,FINAL,SIZES,col,esc,fd,dm,dec,fh,prep,activeModel,makeDims,matchDims,flagMatch,initHeader,taskCard,bindCard,snippet,sizeShort,sizeFull};
})();
