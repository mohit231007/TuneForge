export default function Architecture(){
  return <div>
    <div className="hero"><div><div className="eyebrow">System design</div><h1>Built as a control plane, not a notebook wrapper</h1><p>The public UI, API, queue, GPU workers, artifacts and evaluation layers are separated so each can evolve independently.</p></div></div>
    <section className="card architecture">
      <pre>{`Recruiter / Engineer
        |
        v
Next.js Product UI
        |
        v
FastAPI Control Plane
  |       |        |
  |       |        +--> Workspace + optional API-key boundary
  |       +-----------> Run / Adapter comparison
  +-------------------> Job Queue
                           |
                           v
                     CUDA Worker
                           |
                           v
                   TuneForge Engine
                    /           \
                 LoRA           QLoRA
                    \           /
                     Adapter Artifact
                           |
                +----------+----------+
                |                     |
                v                     v
           Telemetry              Evaluation
                |                     |
                +----------+----------+
                           v
                    Adapter Registry
                           |
             candidate -> validated
                      -> production
                      -> archived`}</pre>
      <h2>What is deliberately real today</h2>
      <p className="muted">Configuration persistence, dataset mapping, LoRA/QLoRA loading, GPU-aware precision, queued execution, worker identity, telemetry, deterministic evaluation, adapter registry, and guarded lifecycle transitions.</p>
      <h2>What is deliberately not overclaimed</h2>
      <p className="muted">The filesystem queue is a reference backend, the API-key boundary is not enterprise IAM, running GPU cancellation still needs a worker control channel, and heuristic evaluation does not replace domain-specific human or benchmark evaluation.</p>
    </section>
  </div>
}
