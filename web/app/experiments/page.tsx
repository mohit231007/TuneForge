"use client";

import {FormEvent, useEffect, useState} from "react";
import {api} from "@/lib/api";
import StatusPill from "@/components/StatusPill";

type Run={run_id:string;status:string;workspace_id:string;worker_id?:string;updated_at:string;message?:string};

export default function Experiments(){
  const [runs,setRuns]=useState<Run[]>([]);
  const [method,setMethod]=useState("none");
  const [model,setModel]=useState("TinyLlama/TinyLlama-1.1B-Chat-v1.0");
  const [dataset,setDataset]=useState("databricks/databricks-dolly-15k");
  const [samples,setSamples]=useState(1000);
  const [rank,setRank]=useState(8);
  const [alpha,setAlpha]=useState(16);
  const [batch,setBatch]=useState(4);
  const [grad,setGrad]=useState(4);
  const [lr,setLr]=useState(0.0002);
  const [launch,setLaunch]=useState(false);
  const [message,setMessage]=useState("");
  const [readOnly,setReadOnly]=useState(false);

  async function load(){try{setRuns(await api<Run[]>("/experiments"))}catch(e){setMessage(String(e))}}
  useEffect(()=>{load()},[]);

  async function submit(e:FormEvent){
    e.preventDefault();
    setMessage("Creating experiment…");
    const config={
      model_name:model,
      dataset_name:dataset,
      dataset:{source:"huggingface",path:null,instruction_field:"instruction",context_field:"context",response_field:"response"},
      quantization:{mode:method},
      seed:42,
      num_train_samples:samples,
      max_seq_length:512,
      lora:{r:rank,alpha,dropout:0.05,target_modules:["q_proj","v_proj"]},
      training:{learning_rate:lr,epochs:1,per_device_batch_size:batch,gradient_accumulation_steps:grad,weight_decay:0.01,lr_scheduler_type:"cosine",warmup_fraction:0.03,gradient_checkpointing:true,logging_steps:10},
      generation:{max_new_tokens:256,do_sample:false},
      output_dir:"studio-managed",
      evaluation_prompts:["Explain what a neural network is in 2-3 sentences.","What are three tips for better sleep?"],
    };
    try{
      const result=await api<Run>("/experiments",{method:"POST",body:JSON.stringify({config,launch})});
      setMessage(`${result.run_id} created with status ${result.status}.`);
      await load();
    }catch(err){setMessage(err instanceof Error?err.message:String(err))}
  }

  async function action(run:Run,type:"cancel"|"retry"){
    try{await api(`/experiments/${run.run_id}/${type}`,{method:"POST"});await load()}catch(e){setMessage(String(e))}
  }

  return <div>
    <div className="hero"><div><div className="eyebrow">Experiment builder</div><h1>Configure an adaptation run</h1><p>Start with reproducible defaults, then move from LoRA to 4-bit QLoRA without changing the experiment contract.</p></div></div>

    {readOnly&&<div className="success" style={{marginBottom:18}}>
      Public demo mode is read-only. You can inspect the experiment configuration here;
      self-host TuneForge with a CUDA worker to launch training.
    </div>}

    <form className="card panel" onSubmit={submit}>
      <div className="formGrid">
        <div className="field"><label>Adaptation method</label><select value={method} onChange={e=>setMethod(e.target.value)}><option value="none">LoRA</option><option value="4bit">QLoRA · 4-bit NF4</option></select></div>
        <div className="field"><label>Base model</label><input value={model} onChange={e=>setModel(e.target.value)}/></div>
        <div className="field"><label>Hugging Face dataset</label><input value={dataset} onChange={e=>setDataset(e.target.value)}/></div>
        <div className="field"><label>Training samples</label><input type="number" value={samples} onChange={e=>setSamples(Number(e.target.value))}/></div>
        <div className="field"><label>LoRA rank</label><input type="number" value={rank} onChange={e=>setRank(Number(e.target.value))}/></div>
        <div className="field"><label>LoRA alpha</label><input type="number" value={alpha} onChange={e=>setAlpha(Number(e.target.value))}/></div>
        <div className="field"><label>Per-device batch</label><input type="number" value={batch} onChange={e=>setBatch(Number(e.target.value))}/></div>
        <div className="field"><label>Gradient accumulation</label><input type="number" value={grad} onChange={e=>setGrad(Number(e.target.value))}/></div>
        <div className="field"><label>Learning rate</label><input type="number" step="0.000001" value={lr} onChange={e=>setLr(Number(e.target.value))}/></div>
        <div className="field"><label>Effective batch</label><input value={batch*grad} disabled/></div>
      </div>
      <div className="actions" style={{marginTop:18}}>
        <label className="muted"><input type="checkbox" checked={launch} onChange={e=>setLaunch(e.target.checked)}/> Queue immediately</label>
        <button className="button primary" type="submit" disabled={readOnly}>
          {readOnly?"Read-only demo":"Create experiment"}
        </button>
      </div>
      {message&&<p className="muted">{message}</p>}
    </form>

    <h2 className="sectionTitle">Runs</h2>
    <section className="card panel">
      {runs.length===0?<div className="empty">No runs in this workspace.</div>:<div className="tableWrap"><table className="table"><thead><tr><th>Run</th><th>Status</th><th>Worker</th><th>Updated</th><th></th></tr></thead><tbody>
        {runs.map(run=><tr key={run.run_id}><td>{run.run_id}</td><td><StatusPill status={run.status}/></td><td>{run.worker_id||"—"}</td><td>{new Date(run.updated_at).toLocaleString()}</td><td><div className="actions">{["ready","queued"].includes(run.status)&&<button className="button danger" onClick={()=>action(run,"cancel")}>Cancel</button>}{["failed","cancelled"].includes(run.status)&&<button className="button" onClick={()=>action(run,"retry")}>Retry</button>}</div></td></tr>)}
      </tbody></table></div>}
    </section>
  </div>
}
