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

- [x] real TinyLlama training run completed through TuneForge
- [x] final training loss saved
- [x] loss history saved
- [x] adapter on-disk size saved
- [x] exact trainable parameter percentage saved
- [x] GPU and precision saved
- [x] base responses saved
- [x] adapted responses saved
- [x] same prompts confirmed
- [x] evidence summary committed; raw evaluation artifacts retained in the verified evidence bundle rather than committed by default

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

Experiment 001 is now backed by a verified real T4 evidence bundle: 0.1022908% trainable parameters, final loss 1.831209, and a 7.7659 MiB adapter. Deployment and public-URL claims remain gated until the demo is actually deployed.
