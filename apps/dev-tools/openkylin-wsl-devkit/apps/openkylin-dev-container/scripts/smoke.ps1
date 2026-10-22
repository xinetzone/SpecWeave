#Requires -Version 5.1
<#
.SYNOPSIS
  Smoke-test the openKylin dev container image.

.DESCRIPTION
  Runs static probes inside the image (sshd -t, jupyter, supervisord, locale,
  timezone, devuser uid, subuid, rootless podman) with --entrypoint /bin/bash,
  then boots the full service stack and waits for the HEALTHCHECK, then checks
  sshd/jupyter processes and ports. Every run uses --pull=never (local image
  only; no implicit registry pulls) and the shared container contract flags
  (--device /dev/fuse, --security-opt label=disable, --cgroupns=host).

.PARAMETER Image
  Image reference. Default: localhost/openkylin-dev:3.0

.EXAMPLE
  ./scripts/smoke.ps1
#>
param(
    [string]$Image = "localhost/openkylin-dev:3.0"
)

$ErrorActionPreference = "Stop"

function Fail([string]$msg, [int]$code = 1) {
    Write-Host "[SMOKE] FAIL: $msg" -ForegroundColor Red
    exit $code
}

$podman = Get-Command podman -ErrorAction SilentlyContinue
if (-not $podman) { Fail "podman not found on PATH." 2 }

& podman image exists $Image 2>$null
if ($LASTEXITCODE -ne 0) { Fail "image '$Image' not present locally — run scripts/build.ps1 first." 2 }

$run = @("run", "--rm", "--pull=never", "--device", "/dev/fuse",
         "--security-opt", "label=disable", "--cgroupns=host")

$probe = @'
set -euo pipefail
fail() { echo "PROBE_FAIL: $1"; exit 1; }
echo "P1 sshd -t";       sshd -t || fail "sshd -t"
echo "P2 jupyter";       python3 -m jupyter --version >/dev/null 2>&1 || fail "jupyter"
echo "P3 supervisord";   supervisord --version || fail "supervisord"
echo "P4 locale";        locale -a | grep -qiE "zh_CN\.(utf-?8)" || fail "locale zh_CN.UTF-8"
echo "P5 timezone";      [ "$(cat /etc/timezone)" = "Asia/Shanghai" ] || fail "timezone"
echo "P6 devuser-uid";   [ "$(id -u devuser)" = "1000" ] || fail "devuser uid"
echo "P7 subuid";        grep -q "^devuser:" /etc/subuid || fail "subuid"
echo "P8 podman-bins";   command -v podman >/dev/null && command -v newuidmap >/dev/null && command -v fuse-overlayfs >/dev/null || fail "podman binaries"
echo "P8b rootless-live"; RL="$(su - devuser -c "podman info --format '{{.Host.Security.Rootless}}'" 2>&1 || true)"; if [ "$RL" = "true" ]; then echo "  live rootless=true"; elif echo "$RL" | grep -q "Operation not permitted"; then echo "  ENV-LIMIT: nested userns EPERM (rootless outer host); image readiness verified, live rootless needs rootful host"; else fail "podman rootless: $RL"; fi
echo "ALL_PROBES_OK"
'@

Write-Host "[SMOKE] static probes on $Image"
# Pass the probe via base64: Windows PowerShell 5.1 native-argument passing
# mangles multi-line strings with embedded quotes; base64 is one clean token.
$probeB64 = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($probe))
$cmd = "echo $probeB64 | base64 -d | bash"
$out = & podman @run --entrypoint /bin/bash $Image -lc $cmd 2>&1
if ($LASTEXITCODE -ne 0) {
    $out | ForEach-Object { Write-Host "  $_" -ForegroundColor Yellow }
    Fail "static probes failed (exit=$LASTEXITCODE)"
}
$out | ForEach-Object { Write-Host "  $_" }
Write-Host "[SMOKE] static probes OK"

Write-Host "[SMOKE] full boot (waiting for HEALTHCHECK)"
$ctrOut = & podman run -d --pull=never --device /dev/fuse `
    --security-opt label=disable --cgroupns=host $Image 2>&1
if ($LASTEXITCODE -ne 0) { Fail "cannot start container: $ctrOut" }
$ctr = (($ctrOut | Select-Object -Last 1).ToString()).Trim()

try {
    $ready = $false
    for ($i = 0; $i -lt 20; $i++) {
        Start-Sleep -Seconds 3
        $state = (& podman inspect -f "{{.State.Health.Status}}" $ctr 2>$null).ToString().Trim()
        if ($LASTEXITCODE -eq 0 -and $state -eq "healthy") { $ready = $true; break }
        $running = (& podman inspect -f "{{.State.Running}}" $ctr 2>$null).ToString().Trim()
        if ($running -ne "true") { break }
    }
    if (-not $ready) {
        & podman logs $ctr 2>&1 | Select-Object -Last 30 | ForEach-Object { Write-Host "  $_" -ForegroundColor Yellow }
        Fail "container not healthy within timeout"
    }
    Write-Host "[SMOKE] full boot healthy (sshd + jupyter via healthcheck)"

    $svc = & podman exec $ctr bash -lc 'pgrep -x sshd >/dev/null && echo SSH_OK; pgrep -f "jupyter" >/dev/null && echo JUPYTER_OK; ss -ltn 2>/dev/null | grep -E ":22 |:8888 " && echo PORTS_OK' 2>&1
    if ($LASTEXITCODE -ne 0) { Fail "service probes failed: $svc" }
    $svc | ForEach-Object { Write-Host "  $_" }
    if (($svc -join " ") -notmatch "SSH_OK.*JUPYTER_OK.*PORTS_OK") {
        Fail "service probes incomplete"
    }
}
finally {
    & podman rm -f $ctr 2>$null | Out-Null
}

Write-Host "[SMOKE] OK: all probes passed on $Image"
exit 0
