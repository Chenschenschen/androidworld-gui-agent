# Environment setup

For everyday independent execution, start with `docs/RUNNING_TASKS.md` and
`run.ps1 -CheckOnly`. The installation commands below are for reproducing setup.

Latest learning result: ContactsAddContact official PASS, initial 0/final 1,
run `trial_ContactsAddContact_20261007T160201_407078Z`. Reproduce with
`& .venv/Scripts/python.exe -X utf8 run_task.py --task ContactsAddContact`.
`run_task.py` now checks the device's official app snapshot as well as the local
setup marker, repairing a missing snapshot through official setup. Contacts
setup warned that its literal `Don't allow` target was absent (the live dialog
used a curly apostrophe). The agent subsequently handled that dialog; no manual
setup intervention occurred. Read `AGENT_WALKTHROUGH.md` for the actual loop.

Completed on 7 October 2026 on Windows. This is an infrastructure check;
no agent benchmark result exists yet.

## The three components

1. **Ollama + GELab-Zero** will receive an observation and propose an action.
2. **Our Python program + Android World** will validate the action, execute it,
   read the next observation, and run the official task verifier.
3. **AndroidWorldAvd** is the test device where the apps and their data live.

A working emulator does not by itself provide the Python benchmark package.
That package is now installed in the project environment.

## Installed components

| Component | Location/version |
| --- | --- |
| Official source | `android_world/`, from https://github.com/google-research/android_world |
| Source commit | `2dfc5ca3dc590efe9c72ce768f2b04182f2f75c7` |
| Python runtime | `.tools/python/cpython-3.11.17-windows-x86_64-none/` |
| Project environment | `.venv/`, Python 3.11.17, no system site packages |
| Installed distribution | `android_world==0.1.0` |
| Android dependency | `android-env==1.2.3` |
| Emulator | `AndroidWorldAvd`, Pixel 6, API 33, `emulator-5554` |
| Emulator gRPC port | `8554` |
| Local model | `gelab-zero-4b-preview:latest`, model ID `6f883cb0e9da` |

Python 3.11 was chosen because the official requirements pin older packages,
including matplotlib 3.6.1, with Windows wheels for that Python version.
The runtime was installed inside the project using `uv`, with no PATH or
registry registration. Packages were installed through `.venv` Python.
The downloaded benchmark's cloud client packages are upstream dependencies;
installing them did not call a cloud model. Our agent will use Ollama locally.

The wheel build generated four protobuf Python files in the source checkout.
These are build outputs; tracked upstream source files were not edited.

## Reproduce on Windows

Run from the project directory. The following clone/bootstrap commands are for
a fresh checkout; the folders already exist on this machine. `uv`, Git, Ollama,
Android SDK, and the AVD must be available separately.

```powershell
git clone https://github.com/google-research/android_world.git android_world
git -C android_world checkout 2dfc5ca3dc590efe9c72ce768f2b04182f2f75c7
uv python install 3.11.17 --install-dir .tools\python --no-bin --no-registry --cache-dir .tools\uv-cache
& '.\.tools\python\cpython-3.11.17-windows-x86_64-none\python.exe' -m venv .venv
& '.\.venv\Scripts\python.exe' -m pip install -r requirements-lock.txt
& '.\.venv\Scripts\python.exe' -m pip check
```

`requirements-lock.txt` records the installed package versions and refers to
the local Android World checkout. The recorded commit pins that checkout.
The original installation used the official `android_world/requirements.txt`
followed by `pip install ./android_world`; both installation logs are preserved
in `.review/`.

Start the emulator with the user's command:

```powershell
& "$env:LOCALAPPDATA\Android\Sdk\emulator\emulator.exe" -avd AndroidWorldAvd -no-snapshot -grpc 8554
```

Once it has booted, run the check:

```powershell
& '.\.venv\Scripts\python.exe' check_setup.py
```

Activation is optional because these commands explicitly use `.venv` Python.
The check uses the standard Windows SDK ADB path, console port 5554, and gRPC
port 8554. It does not run the upstream default cloud-agent runner.

## What the check does

- Confirms the interpreter belongs to the project `.venv`.
- Keeps temporary environment files in `.tools/tmp/`.
- Checks our six task names in the official registry.
- Connects to the emulator and lets Android World install/start its
  accessibility helper.
- Saves a screenshot and a JSON setup report in a new `runs/setup_.../` folder.
- Closes the connection after reading the observation.

`check_setup.py` has one main function. Its loop checks each selected task name.
Its `try/finally` preserves evidence even when a connection check fails.
`android_compat.py` contains only the Windows APK file handoff adapter described
below. Neither file implements an agent.

## Windows compatibility issue

The first check failed while installing AndroidEnv's accessibility helper.
AndroidEnv 1.2.3 writes an APK to an open `NamedTemporaryFile` and then asks ADB
to open it. On Windows/Python 3.11, ADB could not open that file. The failure is
preserved in `runs/setup_20261007T130116_332715Z/report.json`.

`enable_windows_compat()` replaces only AndroidEnv's `_install_apk` method at
runtime for Windows/Python below 3.12. For byte payloads, it writes and closes
the APK in a temporary project folder, converts the request to a file-path
request, and delegates installation to the original method. The temporary
directory is cleaned after installation. Other requests pass through unchanged.

This uses a private dependency method, so recheck it if AndroidEnv is upgraded.
No installed dependency file or tracked Android World source file was edited.

## Verified evidence and remaining work

- `pip check`: no broken requirements.
- Official registry: 116 tasks; all six selected task names available.
- Successful observation: 1080 × 2400 RGB image, 25 UI elements.
- Evidence: `runs/setup_20261007T130234_730990Z/report.json` and `screen.png`.
- Accessibility helper installed on the emulator.

The subsequent connection stage installed/configured Contacts and exercised
official task initialization/verification and real local GUI inference. A small
recorded learning loop now exists; both Contacts trials and a valid Wi-Fi trial
failed. An already-satisfied Wi-Fi PASS is excluded. Paired interface
probes yielded invalid actions, so a baseline winner remains open. The user's
partial GPU offload experiment and exact trial reproduction commands are in
`FIRST_TASKS.md`. Remaining task apps and final repeated evaluations are pending.

The import check emitted a pydub warning because FFmpeg was not found. It did
not prevent registry loading or screenshot/accessibility capture. Audio tasks
are outside our selected scope; video recording/export must still be checked
before evaluations. The learning harness now records emulator MP4 clips; their
coverage and decoding must be checked separately from file existence.
