#Requires -Version 5.1
<#
.SYNOPSIS
  Build the openKylin full-featured dev container image using the native
  Windows Podman (Podman Machine).

.DESCRIPTION
  Detects podman availability and backend reachability, verifies the base
  image exists locally (no implicit pull unless -PullBase), then builds
  localhost/openkylin-dev:<Tag> from the project root (parent of scripts/).

.PARAMETER Tag
  Image tag. Default: 3.0 (image name localhost/openkylin-dev:<Tag>)

.PARAMETER NoCache
  Pass --no-cache to podman build.

.PARAMETER PullBase
  Explicitly pull the base image before building (default: fail with guidance).

.PARAMETER BaseImage
  Base image reference. Default: localhost/openkylin:3.0 (locally imported
  openKylin 3.0 WSL rootfs — local-only, not on any registry, so do NOT use
  -PullBase with it). The official registry 'latest' resolves to 2.0 SP1 LTS,
  not 3.0, hence the local import is the genuine 3.0 base.

.EXAMPLE
  ./scripts/build.ps1
  ./scripts/build.ps1 -Tag 3.0 -PullBase
#>
param(
    [string]$Tag = "3.0",
    [switch]$NoCache,
    [switch]$PullBase,
    [string]$BaseImage = "localhost/openkylin:3.0"
)

$ErrorActionPreference = "Stop"

function Fail([string]$msg, [int]$code = 1) {
    Write-Host "[BUILD] FAIL: $msg" -ForegroundColor Red
    exit $code
}

$podman = Get-Command podman -ErrorAction SilentlyContinue
if (-not $podman) {
    Fail "podman not found on PATH. Install Podman Desktop / podman.exe first." 2
}
Write-Host "[BUILD] podman: $($podman.Source)"

# Backend reachability (native Windows Podman Machine path)
$arch = & podman info --format "{{.Host.Arch}}" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "[BUILD] podman info failed — is the Podman Machine running?"
    Write-Host "  $arch"
    Fail "Podman backend not reachable (try 'podman machine start')." 2
}
Write-Host "[BUILD] Podman backend reachable (arch=$arch)"

# Base image availability
& podman image exists $BaseImage 2>$null
if ($LASTEXITCODE -ne 0) {
    if ($PullBase) {
        Write-Host "[BUILD] pulling base image: $BaseImage"
        & podman pull $BaseImage
        if ($LASTEXITCODE -ne 0) { Fail "base image pull failed: $BaseImage" }
    } else {
        Fail ("base image '$BaseImage' not present locally. Pull it first, e.g.:" +
              "  podman pull quay.io/openkylin/openkylin:latest" +
              "  podman tag quay.io/openkylin/openkylin:latest openkylin/openkylin:latest" +
              " or re-run with -PullBase.") 2
    }
}

$ctx = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$image = "localhost/openkylin-dev:$Tag"
Write-Host "[BUILD] building $image from $ctx"

# Force docker image format: buildah inherits OCI format from the imported
# base image, and OCI silently drops SHELL/HEALTHCHECK instructions (observed
# on openKylin WSL-import base). Docker format honors both.
$args = @("build", "--format", "docker", "-t", $image, $ctx)
if ($NoCache) { $args = @("build", "--no-cache", "--format", "docker", "-t", $image, $ctx) }
& podman @args
if ($LASTEXITCODE -ne 0) { Fail "podman build failed (exit=$LASTEXITCODE)" }

Write-Host "[BUILD] OK: $image"
exit 0
