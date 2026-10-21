"use client";

import {useEffect,useState} from "react";
import {api} from "@/lib/api";

type Run={run_id:string;status:string};
type Adapter={adapter_id:string;lifecycle:string};

function KVs({data}:{data:any}){return <>{Object.entries(data||{}).map(([k,v])=><div className="kv" key={k}><span>{k.replaceAll("_"," ")}</span><span>{typeof v==="object"?JSON.stringify(v):String(v??"—")}</span></div>)}</>}

export default function Compare(){
  const [runs,setRuns]=useState<Run[]>([]);
  const [adapters,setAdapters]=useState<Adapter[]>([]);
  const [leftRun,setLeftRun]=useState("");
  const [rightRun,setRightRun]=useState("");
  const [runResult,setRunResult]=useState<any>(null);
  const [leftAdapter,setLeftAdapter]=useState("");
  const [rightAdapter,setRightAdapter]=useState("");
  const [adapterResult,setAdapterResult]=useState<any>(null);
  const [error,setError]=useState("");

  useEffect(()=>{Promise.all([api<Run[]>("/experiments"),api<Adapter[]>("/adapters")]).then(([r,a])=>{setRuns(r);setAdapters(a);if(r[0])setLeftRun(r[0].run_id);if(r[1])setRightRun(r[1].run_id);if(a[0])setLeftAdapter(a[0].adapter_id);if(a[1])setRightAdapter(a[1].adapter_id)}).catch(e=>setError(String(e)))},[]);

  async function compareRun(){try{setRunResult(await api(`/compare/runs?left=${encodeURIComponent(leftRun)}&right=${encodeURIComponent(rightRun)}`));setError("")}catch(e){setError(String(e))}}
  async function compareAdapter(){try{setAdapterResult(await api(`/compare/adapters?left=${encodeURIComponent(leftAdapter)}&right=${encodeURIComponent(rightAdapter)}`));setError("")}catch(e){setError(String(e))}}

  return <div>
    <div className="hero"><div><div className="eyebrow">Evidence over intuition</div><h1>Compare experiments and adapters</h1><p>Inspect configuration and artifact differences directly instead of relying on screenshots or memory.</p></div></div>
    {error&&<div className="error">{error}</div>}

    <section className="card panel">
      <h2>Run comparison</h2>
      <div className="actions">
        <select value={leftRun} onChange={e=>setLeftRun(e.target.value)}>{runs.map(r=><option key={r.run_id}>{r.run_id}</option>)}</select>
        <span className="muted">vs</span>
        <select value={rightRun} onChange={e=>setRightRun(e.target.value)}>{runs.map(r=><option key={r.run_id}>{r.run_id}</option>)}</select>
        <button className="button primary" onClick={compareRun} disabled={!leftRun||!rightRun}>Compare runs</button>
      </div>
      {runResult&&<div className="compareGrid" style={{marginTop:18}}><div className="card compareBox"><h3>{runResult.left_run_id}</h3><KVs data={runResult.left}/></div><div className="card compareBox"><h3>{runResult.right_run_id}</h3><KVs data={runResult.right}/></div></div>}
      {runResult&&<div className="code" style={{marginTop:14}}>Delta · right minus left{"\n"}{JSON.stringify(runResult.delta_right_minus_left,null,2)}</div>}
    </section>

    <section className="card panel" style={{marginTop:18}}>
      <h2>Adapter comparison</h2>
      <div className="actions">
        <select value={leftAdapter} onChange={e=>setLeftAdapter(e.target.value)}>{adapters.map(a=><option key={a.adapter_id}>{a.adapter_id}</option>)}</select>
        <span className="muted">vs</span>
        <select value={rightAdapter} onChange={e=>setRightAdapter(e.target.value)}>{adapters.map(a=><option key={a.adapter_id}>{a.adapter_id}</option>)}</select>
        <button className="button primary" onClick={compareAdapter} disabled={!leftAdapter||!rightAdapter}>Compare adapters</button>
      </div>
      {adapterResult&&<div className="compareGrid" style={{marginTop:18}}><div className="card compareBox"><KVs data={adapterResult.left}/></div><div className="card compareBox"><KVs data={adapterResult.right}/></div></div>}
    </section>
  </div>
}
