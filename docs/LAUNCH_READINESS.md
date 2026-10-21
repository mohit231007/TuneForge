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
- [x] live production screenshots captured in an Incognito browser
- [x] live Architecture page captured
- [ ] sample dataset flow demonstrated
- [x] public deployment contains no private training data or model weights

## Portfolio gates

- [ ] README hero tightened
- [ ] recruiter brief reviewed
- [ ] resume bullet selected
- [x] LinkedIn launch post updated with measured Experiment 001 results and live demo URL
- [x] live public deployment tested in Incognito/private browser
- [ ] interview talk-track practiced against real implementation

## Claim gate

Do not publish the launch claim until real experiment artifacts support every numeric statement.

Experiment 001 is backed by a verified real T4 evidence bundle: 0.1022908% trainable parameters, final loss 1.831209, and a 7.7659 MiB adapter. The public Vercel web/API deployment is live; only final human incognito/UI screenshot checks remain before broad promotion.


## Human production verification

Verified in an Incognito browser against the production URL:

- Overview renders the Verified Experiment 001 card
- Experiment builder renders with the production API URL
- Adapter registry renders correctly with an empty public workspace state
- Run / adapter comparison surfaces render
- Deterministic Evaluation form renders
- Architecture / system-design page renders
- navigation between the public product surfaces works
- no Vercel login wall is shown

The captured Evaluation screen confirms the live form is available, but does not itself prove a post-click rule-check result. Automated public-API tests cover the rule-evaluation endpoint separately.
