# Start one learning task with the project's Python, or check readiness only.
param(
    [ValidateSet('ContactsAddContact', 'SystemWifiTurnOn', 'CameraTakePhoto', 'ClockTimerEntry', 'SystemCopyToClipboard')]
    [string]$Task = 'ContactsAddContact',
    [int]$Seed = 42,
    [ValidateSet('tree_first', 'tree', 'screenshot')]
    [string]$Observation,
    [switch]$CheckOnly
)

$ErrorActionPreference = 'Stop'
$projectPython = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
$taskScript = Join-Path $PSScriptRoot 'run_task.py'
$sdkAdb = Join-Path $env:LOCALAPPDATA 'Android\Sdk\platform-tools\adb.exe'
if (-not (Test-Path -LiteralPath $projectPython)) {
    throw 'Project .venv is missing. Follow docs/SETUP.md before running tasks.'
}
if (-not (Test-Path -LiteralPath $sdkAdb)) {
    throw 'Android SDK ADB is missing from LOCALAPPDATA\Android\Sdk\platform-tools.'
}
$settings = Get-Content -LiteralPath (Join-Path $PSScriptRoot 'agent_config.json') -Raw | ConvertFrom-Json
$deviceState = & $sdkAdb -s emulator-5554 get-state 2>$null
if ($LASTEXITCODE -ne 0 -or $deviceState -ne 'device') {
    throw 'emulator-5554 is unavailable. Start AndroidWorldAvd with -no-snapshot -grpc 8554. See docs/RUNNING_TASKS.md.'
}
$bootState = & $sdkAdb -s emulator-5554 shell getprop sys.boot_completed
if ($LASTEXITCODE -ne 0 -or "$bootState".Trim() -ne '1') {
    throw 'The emulator is still booting. Wait for its home screen, then retry.'
}
# A reachable port is a readiness check; the Python environment verifies gRPC.
$grpcClient = [System.Net.Sockets.TcpClient]::new()
try {
    $connect = $grpcClient.ConnectAsync('127.0.0.1', 8554)
    if (-not $connect.Wait(3000)) { throw 'Connection timed out.' }
} catch {
    throw 'Emulator gRPC port 8554 is unavailable. Start the emulator with -grpc 8554.'
} finally {
    $grpcClient.Dispose()
}

Push-Location -LiteralPath $PSScriptRoot
try {
    & $projectPython -X utf8 -c "from android_world.env import env_launcher; from autoglm_agent import api_settings; endpoint, model, _ = api_settings(); print('Project Python, AutoGLM config and imports: OK')"
    if ($LASTEXITCODE -ne 0) { throw 'Project Python imports failed. Check docs/SETUP.md.' }
    Write-Host "Ready: $Task, task seed $Seed, Z.ai model $($settings.model)."
    if ($CheckOnly) {
        Write-Host 'Readiness check only: no task initialized or GUI action executed.'
        return
    }
    $taskArguments = @('-X', 'utf8', $taskScript, '--task', $Task, '--seed', "$Seed")
    if ($Observation) { $taskArguments += @('--observation', $Observation) }
    & $projectPython @taskArguments
    if ($LASTEXITCODE -ne 0) { throw 'Task process failed. Read its printed evidence folder and summary.json.' }
    Write-Host 'Trial finished. Read summary.json: clean_agent_success requires official PASS and model finish; this launcher message is not a success claim.'
} finally {
    Pop-Location
}
