"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import MetricCard from "@/components/MetricCard";
import StatusPill from "@/components/StatusPill";

type Run = {run_id:string;status:string;worker_id?:string;updated_at:string;message?:string};
type Adapter = {adapter_id:string;model_name:string;lifecycle?:string;quantization_mode?:string;size_bytes?:number;parameters?:{trainable_percentage?:number}};

export default function Overview(){
  const [runs,setRuns]=useState<Run[]>([]);
  const [adapters,setAdapters]=useState<Adapter[]>([]);
  const [queue,setQueue]=useState<any>({});
  const [error,setError]=useState("");

  async function load(){
    try{
      const [r,a,q]=await Promise.all([
        api<Run[]>("/experiments"),
        api<Adapter[]>("/adapters"),
        api<any>("/queue"),
      ]);
      setRuns(r);setAdapters(a);setQueue(q);setError("");
    }catch(e){setError(e instanceof Error?e.message:String(e))}
  }

  useEffect(()=>{load()},[]);

  const production=adapters.filter(a=>a.lifecycle==="production").length;

  return <div>
    <div className="hero">
      <div>
        <div className="eyebrow">LLM engineering control plane</div>
        <h1>Fine-tune less. Measure more. Ship adapters deliberately.</h1>
        <p>TuneForge turns LoRA and QLoRA experiments into observable, reproducible model-engineering workflows—from dataset and GPU execution to evaluation and adapter promotion.</p>
      </div>
      <button className="button" onClick={load}>Refresh</button>
    </div>

    {error&&<div className="error">{error}</div>}

    <div className="metrics">
      <MetricCard label="Experiments" value={runs.length} note="workspace scoped"/>
      <MetricCard label="Queued jobs" value={queue.pending??0} note="local queue backend"/>
      <MetricCard label="Registered adapters" value={adapters.length} note="versioned artifacts"/>
      <MetricCard label="Production adapters" value={production} note="explicitly promoted"/>
    </div>

    <div className="grid2">
      <section className="card panel">
        <h2>Recent experiments</h2>
        {runs.length===0?<div className="empty">No experiment runs yet.</div>:
        <div className="tableWrap"><table className="table"><thead><tr><th>Run</th><th>Status</th><th>Worker</th></tr></thead><tbody>
          {runs.slice(0,6).map(run=><tr key={run.run_id}><td>{run.run_id}</td><td><StatusPill status={run.status}/></td><td>{run.worker_id||"—"}</td></tr>)}
        </tbody></table></div>}
      </section>

      <section className="card panel">
        <h2>Adapter registry</h2>
        {adapters.length===0?<div className="empty">No adapters registered yet.</div>:
        <div className="tableWrap"><table className="table"><thead><tr><th>Adapter</th><th>Method</th><th>Lifecycle</th></tr></thead><tbody>
          {adapters.slice(0,6).map(item=><tr key={item.adapter_id}><td>{item.adapter_id}</td><td>{item.quantization_mode==="4bit"?"QLoRA":"LoRA"}</td><td><StatusPill status={item.lifecycle||"candidate"}/></td></tr>)}
        </tbody></table></div>}
      </section>
    </div>

    <h2 className="sectionTitle">Why this is different from a notebook</h2>
    <div className="grid3">
      <div className="card panel"><h3>Observable training</h3><p className="muted">Loss, learning rate, GPU allocation, logs and worker identity stay attached to each run.</p></div>
      <div className="card panel"><h3>Comparable experiments</h3><p className="muted">Use identical prompts and measurable outputs, then compare run metadata rather than relying on memory.</p></div>
      <div className="card panel"><h3>Governed adapters</h3><p className="muted">Adapters move from candidate to validated to production instead of every checkpoint being treated as deployable.</p></div>
    </div>
  </div>
}
