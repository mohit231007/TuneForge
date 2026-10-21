# Launch Readiness

## Engineering gates

- [x] PR stack merged in order
- [x] Python Ruff green
- [x] Python Pytest green
- [x] Next.js build green
- [ ] Docker images build
- [ ] API health endpoint verified
- [x] web → API CORS configured to the exact production frontend origin
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

- [x] Next.js UI deployed — https://tuneforge-algosphere1.vercel.app
- [x] API deployed — https://tuneforge-public-api.vercel.app
- [x] demo workspace defaults to the public read-only workspace
- [x] no secret-bearing client environment variables; only the public API URL is compiled into the web app
- [ ] screenshots captured
- [ ] architecture image / diagram captured
- [ ] sample dataset flow demonstrated
- [x] public deployment contains no private training data or model weights

## Portfolio gates

- [ ] README hero tightened
- [ ] recruiter brief reviewed
- [ ] resume bullet selected
- [x] LinkedIn launch post updated with measured Experiment 001 results and live demo URL
- [ ] repository link tested in incognito/private browser
- [ ] interview talk-track practiced against real implementation

## Claim gate

Do not publish the launch claim until real experiment artifacts support every numeric statement.

Experiment 001 is backed by a verified real T4 evidence bundle: 0.1022908% trainable parameters, final loss 1.831209, and a 7.7659 MiB adapter. The public Vercel web/API deployment is live; only final human incognito/UI screenshot checks remain before broad promotion.
