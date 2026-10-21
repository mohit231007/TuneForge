"use client";

import {useEffect,useState} from "react";
import {api} from "@/lib/api";
import StatusPill from "@/components/StatusPill";

type Adapter={adapter_id:string;model_name:string;lifecycle:string;quantization_mode:string;size_bytes:number;created_at:string;parameters?:{trainable_percentage?:number};lora?:any};

const nextStates:Record<string,string[]>={
  candidate:["validated","archived"],
  validated:["production","archived"],
  production:["archived"],
  archived:[],
};

export default function Adapters(){
  const [items,setItems]=useState<Adapter[]>([]);
  const [message,setMessage]=useState("");
  async function load(){try{setItems(await api<Adapter[]>("/adapters"))}catch(e){setMessage(String(e))}}
  useEffect(()=>{load()},[]);

  async function transition(item:Adapter,target:string){
    try{
      await api(`/adapters/${item.adapter_id}/transition`,{method:"POST",body:JSON.stringify({target_state:target,reason:`Promoted via TuneForge Web to ${target}.`})});
      await load();
    }catch(e){setMessage(String(e))}
  }

  return <div>
    <div className="hero"><div><div className="eyebrow">Model artifact governance</div><h1>Adapter registry</h1><p>Track reusable LoRA/QLoRA artifacts and promote them deliberately through validation and production states.</p></div></div>
    {message&&<div className="error">{message}</div>}
    <div className="grid2">
      {items.map(item=><article className="card panel" key={item.adapter_id}>
        <div className="toolbar"><strong>{item.adapter_id}</strong><StatusPill status={item.lifecycle}/></div>
        <div className="kv"><span>Base model</span><span>{item.model_name}</span></div>
        <div className="kv"><span>Method</span><span>{item.quantization_mode==="4bit"?"QLoRA":"LoRA"}</span></div>
        <div className="kv"><span>Adapter size</span><span>{(item.size_bytes/1024/1024).toFixed(2)} MB</span></div>
        <div className="kv"><span>Trainable</span><span>{(item.parameters?.trainable_percentage??0).toFixed(4)}%</span></div>
        <div className="kv"><span>Created</span><span>{new Date(item.created_at).toLocaleDateString()}</span></div>
        <div className="actions" style={{marginTop:16}}>
          {(nextStates[item.lifecycle]||[]).map(state=><button key={state} className={state==="archived"?"button danger":"button primary"} onClick={()=>transition(item,state)}>{state==="validated"?"Validate":state==="production"?"Promote to production":"Archive"}</button>)}
        </div>
      </article>)}
    </div>
    {items.length===0&&<div className="card empty">No adapters have been registered in this workspace.</div>}
  </div>
}
