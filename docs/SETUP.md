# Install on Windows

This guide describes the hosted AutoGLM version. The original local-model setup
record is preserved in [HISTORICAL_SETUP.md](HISTORICAL_SETUP.md).
No local language model or Ollama installation is required.

## 1. Install prerequisites

Install Git, Python 3.11 and Android Studio. In Android Studio's SDK Manager,
install Android SDK Platform-Tools, Android Emulator and an Android 13 / API 33
system image. Keep the SDK at `%LOCALAPPDATA%\Android\Sdk`: this is the current
runner's supported path. Hardware virtualization must be enabled for the emulator.

The official Android World README specifies **Pixel 6**, **Tiramisu / API 33**
and the name **AndroidWorldAvd**. Create that AVD in Device Manager. This project
uses one device on console port 5554 (`emulator-5554`) and gRPC port 8554.
Close other emulators before starting it so the default device port is available.
Use the **Google APIs** x86_64 image, not a Google Play image: verifiers such as
Calendar read app databases, which needs `adb root`.

Command-line alternative without the Android Studio GUI (verified 8 October 2026
on Windows 10, no administrator rights; WHPX was already usable). Use
command-line tools **19.0** (`commandlinetools-win-13114758_latest.zip`): newer
builds replace `sdkmanager` with a different CLI. Unzip it to
`%LOCALAPPDATA%\Android\Sdk\cmdline-tools\latest`, set `JAVA_HOME` to a JDK 17,
list `platform-tools`, `emulator`, `platforms;android-33` and
`system-images;android-33;google_apis;x86_64` one per line in a text file, then:

```powershell
sdkmanager.bat --sdk_root="$env:LOCALAPPDATA\Android\Sdk" --licenses
sdkmanager.bat --sdk_root="$env:LOCALAPPDATA\Android\Sdk" --package_file=packages.txt
avdmanager.bat create avd -n AndroidWorldAvd -k "system-images;android-33;google_apis;x86_64" -d pixel_6
emulator.exe -accel-check
```

The package file avoids `cmd` splitting package names at `;`.

The source/pin is
[Android World at 2dfc5ca](https://github.com/google-research/android_world/tree/2dfc5ca3dc590efe9c72ce768f2b04182f2f75c7).
The tested environment is Windows, Python 3.11.17 and AndroidEnv 1.2.3.
Other platforms and dependency versions have not been validated by this project.

## 2. Clone and install

Use a short checkout path, such as `C:\src\androidworld-gui-agent`. Run these
commands from PowerShell; the dependency checkout is deliberately separate:

```powershell
git clone https://github.com/Chenschenschen/androidworld-gui-agent.git
Set-Location androidworld-gui-agent
git clone https://github.com/google-research/android_world.git android_world
git -C android_world checkout 2dfc5ca3dc590efe9c72ce768f2b04182f2f75c7
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
.\.venv\Scripts\python.exe -m pip check
```

If `py -3.11` is unavailable, supply your Python 3.11 executable explicitly.
For the exact recorded runtime, an optional `uv` installation provides 3.11.17:

```powershell
uv python install 3.11.17 --install-dir .tools\python --no-bin --no-registry --cache-dir .tools\uv-cache
& '.\.tools\python\cpython-3.11.17-windows-x86_64-none\python.exe' -m venv .venv
```

Use either venv creation route, then run the same project-Python pip commands.
Do not use `--system-site-packages`. Activation is optional: all commands invoke
`.venv` directly. The lock records installed versions and includes `./android_world`.
Android World's package build generates its protobuf bindings automatically.
Its upstream dependencies include other providers' client libraries; the current
agent calls only Z.ai through the standard library.

## 3. Configure the API

```powershell
Copy-Item .env.example .env
```

Edit `.env` with your own Z.ai key. Keep these model/endpoint values:

```dotenv
ZAI_API_KEY=your_zai_api_key
PHONE_AGENT_BASE_URL=https://api.z.ai/api/paas/v4
PHONE_AGENT_MODEL=autoglm-phone-multilingual
```

The key is loaded from project-root `.env`; no shell evaluation or expansion is
used. Both the model ID and endpoint are validated before a task. Your account
must have access to the hosted multilingual model. API inference may incur
charges and sends the test screenshots and exact task inputs to Z.ai.
See [AUTOGLM_API.md](AUTOGLM_API.md). `.env` is excluded from Git.

## 4. Start the test emulator

Launch from PowerShell rather than Android Studio's play button:

```powershell
& "$env:LOCALAPPDATA\Android\Sdk\emulator\emulator.exe" -avd AndroidWorldAvd -no-snapshot -grpc 8554 -camera-back emulated -camera-front emulated
```

Wait for the home screen. In a second terminal, from the project directory:

```powershell
& "$env:LOCALAPPDATA\Android\Sdk\platform-tools\adb.exe" devices
.\run.ps1 -CheckOnly
.\.venv\Scripts\python.exe -X utf8 -m unittest test_autoglm_adapter -v
```

ADB must show `emulator-5554` as `device`. CheckOnly validates imports, API
configuration, emulator boot and the gRPC port. It makes no API request or task
initialization. The 18 unit checks also make no API or device calls.

The software camera flags repair this project's measured virtual-scene loading
problem. They do not modify the AVD configuration permanently.

## 5. Run a task

```powershell
.\.venv\Scripts\python.exe -X utf8 run_task.py --task ContactsAddContact --seed 42
```

The runner uses official environment reset, task initialization and required app
setup/snapshots. A fresh emulator's first run may take longer because those apps
and snapshots are prepared. It records video before executing agent actions.
Leave the emulator untouched. Task initialization resets test data; use only
this dedicated emulator.

Read the printed evidence folder's `summary.json`: `agent_done` and `verifier`
are separate. `clean_agent_success` requires both, valid recording and no runtime
error. See [RUNNING_TASKS.md](RUNNING_TASKS.md) for all five tasks and log fields.
Timer and Clipboard currently have unresolved failures; launching them does not
establish success.

## Troubleshooting

| Symptom | Check |
| --- | --- |
| Missing `.venv` or import | Use Python 3.11, clone the pinned dependency, run project pip and `pip check`. |
| ADB missing | Verify the supported SDK path and install Platform-Tools. |
| Device or gRPC unavailable | Use the command above; verify device 5554, boot completion and port 8554. |
| Wrong model/key or HTTP error | Inspect `.env` and account access; never paste the key into logs/issues. |
| Recorder failure | Inspect `video_*.stderr.txt` and `summary.json`; it is an infrastructure error. |
| Every screenshot is black; run stops with `rendering_infrastructure_error`; emulator log repeats `glReadPixels ... error 0x506` | The host-GPU rendering backend cannot read pixels (observed on an Intel Iris Xe laptop). Restart the emulator with software rendering by appending `-gpu swiftshader_indirect` to the command above. All v30+ runs on that machine use this flag. |
| First app setup fails with `UIAutomator did not confirm writing this observation` | A cold-starting app briefly returns `ERROR: null root node`. Since v30, `android_compat.py` retries that dump up to three times (never reading an unconfirmed file). Rerun the task; no snapshot was saved by the failed setup. |
| Model repeats or falsely finishes | Read the saved trajectory and official outcome before changing or rerunning it. |

`android_compat.py` retains a narrow Windows/Python 3.11 temporary-APK handoff
adapter and checked unique XML capture. These use dependency internals, so test
them before upgrading AndroidEnv/Android World. Do not patch installed dependency
files manually. A full upstream default-agent runner is unnecessary for these
five task entry points and would select a different model workflow.
