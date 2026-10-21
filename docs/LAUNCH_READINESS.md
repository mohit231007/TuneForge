# Launch Readiness

## Engineering gates

- [ ] PR stack merged in order
- [ ] Python Ruff green
- [ ] Python Pytest green
- [ ] Next.js build green
- [ ] Docker images build
- [ ] API health endpoint verified
- [ ] web → API CORS verified
- [ ] one worker successfully claims a queued job
- [ ] failed-job retry verified
- [ ] candidate → validated → production adapter transition verified

## Experiment 001 evidence gates

- [ ] real TinyLlama training run completed through TuneForge
- [ ] final training loss saved
- [ ] loss history saved
- [ ] adapter on-disk size saved
- [ ] exact trainable parameter percentage saved
- [ ] GPU and precision saved
- [ ] base responses saved
- [ ] adapted responses saved
- [ ] same prompts confirmed
- [ ] evaluation JSON/CSV committed only if appropriate and license-safe

## Public demo gates

- [ ] Next.js UI deployed
- [ ] API deployed
- [ ] demo workspace configured
- [ ] secrets not exposed to browser
- [ ] screenshots captured
- [ ] architecture image / diagram captured
- [ ] sample dataset flow demonstrated
- [ ] public deployment contains no private training data

## Portfolio gates

- [ ] README hero tightened
- [ ] recruiter brief reviewed
- [ ] resume bullet selected
- [ ] LinkedIn launch post updated with actual results
- [ ] repository link tested in incognito/private browser
- [ ] interview talk-track practiced against real implementation

## Claim gate

Do not publish the launch claim until real experiment artifacts support every numeric statement.

The ~0.1023% parameter-efficiency figure is already backed by the reference LoRA setup. Loss, adapter size, quality comparisons, and deployment claims must be populated from real TuneForge runs.
