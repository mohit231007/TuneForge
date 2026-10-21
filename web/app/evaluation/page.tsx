"use client";

import {useState} from "react";
import {api} from "@/lib/api";

export default function Evaluation(){
  const [response,setResponse]=useState("Neural networks learn patterns from data and use layered transformations to produce predictions.");
  const [minWords,setMinWords]=useState(5);
  const [maxWords,setMaxWords]=useState(80);
  const [contains,setContains]=useState("patterns");
  const [notContains,setNotContains]=useState("");
  const [result,setResult]=useState<any>(null);
  const [error,setError]=useState("");

  async function run(){
    const rules:any={min_words:minWords,max_words:maxWords};
    if(contains.trim()) rules.contains=contains.split(",").map(x=>x.trim()).filter(Boolean);
    if(notContains.trim()) rules.not_contains=notContains.split(",").map(x=>x.trim()).filter(Boolean);

    try{
      const payload=await api<any>("/evaluation/rules",{
        method:"POST",
        body:JSON.stringify({response,rules}),
      });
      setResult(payload.result);setError("");
    }catch(e){setError(e instanceof Error?e.message:String(e))}
  }

  return <div>
    <div className="hero"><div><div className="eyebrow">Deterministic evaluation</div><h1>Turn response expectations into checks</h1><p>Use auditable rules for length, required terms, forbidden terms and regex constraints. This complements—but does not replace—semantic benchmarks and human evaluation.</p></div></div>

    <div className="grid2">
      <section className="card panel">
        <h2>Response under test</h2>
        <div className="field"><label>Generated response</label><textarea rows={10} value={response} onChange={e=>setResponse(e.target.value)}/></div>
      </section>

      <section className="card panel">
        <h2>Evaluation rules</h2>
        <div className="formGrid">
          <div className="field"><label>Minimum words</label><input type="number" value={minWords} onChange={e=>setMinWords(Number(e.target.value))}/></div>
          <div className="field"><label>Maximum words</label><input type="number" value={maxWords} onChange={e=>setMaxWords(Number(e.target.value))}/></div>
          <div className="field"><label>Must contain · comma separated</label><input value={contains} onChange={e=>setContains(e.target.value)}/></div>
          <div className="field"><label>Must not contain · comma separated</label><input value={notContains} onChange={e=>setNotContains(e.target.value)}/></div>
        </div>
        <button className="button primary" style={{marginTop:16}} onClick={run}>Run checks</button>
      </section>
    </div>

    {error&&<div className="error" style={{marginTop:18}}>{error}</div>}

    {result&&<section className="card panel" style={{marginTop:18}}>
      <div className="toolbar"><h2>Evaluation result</h2><span className={result.passed?"status status-completed":"status status-failed"}>{result.passed?"PASS":"FAIL"}</span></div>
      <p className="muted">{result.passed_count} of {result.check_count} checks passed.</p>
      <div className="tableWrap"><table className="table"><thead><tr><th>Check</th><th>Observed</th><th>Expected</th><th>Result</th></tr></thead><tbody>
        {result.checks.map((check:any)=><tr key={check.name}><td>{check.name}</td><td>{String(check.observed)}</td><td>{String(check.expected)}</td><td><span className={check.passed?"status status-completed":"status status-failed"}>{check.passed?"pass":"fail"}</span></td></tr>)}
      </tbody></table></div>
    </section>}
  </div>
}
