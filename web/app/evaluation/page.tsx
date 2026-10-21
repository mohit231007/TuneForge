"use client";

import {useState} from "react";

type Check = {
  name: string;
  passed: boolean;
  observed: string | number | boolean;
  expected: string | number | boolean;
};

type EvaluationResult = {
  passed: boolean;
  check_count: number;
  passed_count: number;
  checks: Check[];
};

function parseTerms(value: string): string[] {
  return value
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean)
    .slice(0, 10)
    .map((item) => item.slice(0, 100));
}

export default function Evaluation(){
  const [response,setResponse]=useState(
    "Neural networks learn patterns from data and use layered transformations to produce predictions."
  );
  const [minWords,setMinWords]=useState(5);
  const [maxWords,setMaxWords]=useState(80);
  const [contains,setContains]=useState("patterns");
  const [notContains,setNotContains]=useState("");
  const [result,setResult]=useState<EvaluationResult|null>(null);

  function run(){
    const boundedResponse=response.slice(0,8000);
    const words=boundedResponse.split(/\s+/).filter(Boolean);
    const checks:Check[]=[];

    checks.push({
      name:"min_words",
      passed:words.length>=Math.max(0,Math.min(minWords,2000)),
      observed:words.length,
      expected:Math.max(0,Math.min(minWords,2000)),
    });
    checks.push({
      name:"max_words",
      passed:words.length<=Math.max(0,Math.min(maxWords,2000)),
      observed:words.length,
      expected:Math.max(0,Math.min(maxWords,2000)),
    });

    for(const needle of parseTerms(contains)){
      const present=boundedResponse.toLowerCase().includes(needle.toLowerCase());
      checks.push({
        name:`contains:${needle}`,
        passed:present,
        observed:present,
        expected:true,
      });
    }

    for(const needle of parseTerms(notContains)){
      const absent=!boundedResponse.toLowerCase().includes(needle.toLowerCase());
      checks.push({
        name:`not_contains:${needle}`,
        passed:absent,
        observed:absent,
        expected:true,
      });
    }

    setResult({
      passed:checks.every((check)=>check.passed),
      check_count:checks.length,
      passed_count:checks.filter((check)=>check.passed).length,
      checks,
    });
  }

  return <div>
    <div className="hero"><div><div className="eyebrow">Deterministic evaluation</div><h1>Turn response expectations into checks</h1><p>Use auditable rules for length, required terms, and forbidden terms. The public demo evaluates these checks locally in your browser, so no generated response is sent to the public API.</p></div></div>

    <div className="grid2">
      <section className="card panel">
        <h2>Response under test</h2>
        <div className="field">
          <label>Generated response · max 8,000 characters</label>
          <textarea
            rows={10}
            maxLength={8000}
            value={response}
            onChange={e=>setResponse(e.target.value)}
          />
        </div>
      </section>

      <section className="card panel">
        <h2>Evaluation rules</h2>
        <div className="formGrid">
          <div className="field"><label>Minimum words</label><input type="number" min={0} max={2000} value={minWords} onChange={e=>setMinWords(Number(e.target.value))}/></div>
          <div className="field"><label>Maximum words</label><input type="number" min={0} max={2000} value={maxWords} onChange={e=>setMaxWords(Number(e.target.value))}/></div>
          <div className="field"><label>Must contain · max 10 comma-separated terms</label><input value={contains} onChange={e=>setContains(e.target.value)}/></div>
          <div className="field"><label>Must not contain · max 10 comma-separated terms</label><input value={notContains} onChange={e=>setNotContains(e.target.value)}/></div>
        </div>
        <button className="button primary" style={{marginTop:16}} onClick={run}>Run checks locally</button>
      </section>
    </div>

    {result&&<section className="card panel" style={{marginTop:18}}>
      <div className="toolbar"><h2>Evaluation result</h2><span className={result.passed?"status status-completed":"status status-failed"}>{result.passed?"PASS":"FAIL"}</span></div>
      <p className="muted">{result.passed_count} of {result.check_count} checks passed. No API request was required.</p>
      <div className="tableWrap"><table className="table"><thead><tr><th>Check</th><th>Observed</th><th>Expected</th><th>Result</th></tr></thead><tbody>
        {result.checks.map((check)=><tr key={check.name}><td>{check.name}</td><td>{String(check.observed)}</td><td>{String(check.expected)}</td><td><span className={check.passed?"status status-completed":"status status-failed"}>{check.passed?"pass":"fail"}</span></td></tr>)}
      </tbody></table></div>
    </section>}
  </div>
}
