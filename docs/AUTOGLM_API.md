# AutoGLM through Z.ai — 7 October 2026

The user selected `AutoGLM-Phone-9B-Multilingual` through Z.ai to replace local
GELab-Zero. The default runner is migrated. Its initial corrected Wi-Fi trial
passed the official verifier but had a stopping error, now tracked through the
versioned repairs in [AUTOGLM_COMPLETION_REPAIR.md](AUTOGLM_COMPLETION_REPAIR.md).
Read
[AUTOGLM_FIRST_TRIAL.md](AUTOGLM_FIRST_TRIAL.md) for both recorded attempts.

## Select the model

The official [Open-AutoGLM README](https://github.com/zai-org/Open-AutoGLM/blob/main/README_en.md)
gives the following Z.ai settings. Select the model by setting the request's
`model` field; the hosted API name differs from the downloadable weights' name.

```dotenv
PHONE_AGENT_BASE_URL=https://api.z.ai/api/paas/v4
PHONE_AGENT_MODEL=autoglm-phone-multilingual
```

POST to `https://api.z.ai/api/paas/v4/chat/completions` with
`Authorization: Bearer <key>` and a JSON body containing
`"model": "autoglm-phone-multilingual"` and `messages`.
Use the general API endpoint listed above. Z.ai documents a separate endpoint
for its Coding Plan; that is not the endpoint prescribed by the AutoGLM README.
See [Z.ai authentication and endpoints](https://docs.z.ai/api-reference/introduction).

The project's `.env` already contains the correct base URL and model, plus a
nonempty `ZAI_API_KEY`. The connectivity probe read that key explicitly. The
[upstream CLI](https://github.com/zai-org/Open-AutoGLM/blob/main/main.py) instead
reads `PHONE_AGENT_API_KEY` from process environment variables, or accepts
`--apikey`. Its entry point does not load a project `.env` automatically.
Our integration explicitly loads `.env` and maps `ZAI_API_KEY` to the request
header. Keep keys out of commands, trajectory requests, version snapshots and
console output. `.env` is already listed in the project's `.gitignore`.

## Recorded access check

The first bounded text request failed at sandbox DNS resolution:
[original result](../runs/autoglm_api_probe_20261007T194838_917491Z/result.json).
A separate network-enabled request then received HTTP 200:
[request](../runs/autoglm_api_probe_20261007T194904_649147Z/request.json),
[result](../runs/autoglm_api_probe_20261007T194904_649147Z/result.json).

The successful request used project Python 3.11.17, standard-library HTTP,
temperature 0, non-streaming output, a 45-second timeout and a 64-token output
cap. The response reported `model: autoglm-phone-multilingual`, 22 prompt tokens
and 64 completion tokens, with `finish_reason: length`; elapsed HTTP time was
1.219 seconds. No emulator observation was sent and no GUI action executed.

The text-only reply described a camera screen despite receiving no image. This
probe establishes authenticated model access, not visual grounding, action
compatibility, GUI success or representative inference speed. No official task
verifier ran. Preserve both the network failure and successful access record.

## Implemented runtime migration

`run_task.py` and `run.ps1` now use `AutoGLMAgent` in `autoglm_agent.py`, with
`agent_config.json` selecting `autoglm_api_v2_visual_capture`. The evaluation
scheduler fingerprints the new agent and prompt. The legacy `gelab_agent.py`
remains historical; it is no longer imported by the task runner. Ollama is not
required and its app/server were stopped at the user's request.

The upstream [model client](https://github.com/zai-org/Open-AutoGLM/blob/main/phone_agent/model/client.py)
sends screenshots as `image_url` content alongside task text. Its
[English prompt](https://github.com/zai-org/Open-AutoGLM/blob/main/phone_agent/config/prompts_en.py)
uses one pseudo-call such as `do(action="Tap", element=[x,y])` or
`finish(message="...")`. This differs from our GELab JSON/tree contract.

API transport, screenshot input and checked native action conversion are
implemented, retaining Android World's executor, bounded loop, videos,
trajectory logging and official verifier. A saved-screen probe parsed correctly.
The first recorded attempt failed before a model call because XML capture could
not obtain idle state; the corrected version uses the official screenshot-only
backend, bounded visual settling and image freshness checks. One Wi-Fi trial
then passed, but repeated toggles and a step-budget stop remain a model error.
All GELab runs remain historical evidence. Further tasks, stopping reliability
and repeated evaluations remain open. A model-plus-interface comparison must
be labelled as such. See RUNNING_TASKS.md for actual standalone commands.
