# PathPattern.psm1 - Generic path pattern resolution module
#
# Provides segment-by-segment wildcard directory resolution.
# Useful for build scripts, project discovery, and any scenario where
# you need to resolve paths with '*' wildcards against a base directory.
#
# Usage:
#   Import-Module "$PSScriptRoot/PathPattern.psm1"
#   $dirs = Resolve-PathPattern -BaseDir "C:\src" -Segments @("projects", "*", "libs")
#   # Returns all directories matching C:\src\projects\*\libs
#
# Design principles:
# - No project-specific coupling
# - Pure function: no side effects, deterministic output
# - '*' matches exactly one directory level (not recursive)
# - Returns empty array on no match (no errors thrown for missing paths)

Set-StrictMode -Version Latest

function Resolve-PathPattern {
    <#
    .SYNOPSIS
        Resolves a relative path pattern (with * wildcards) against a base directory.
    .DESCRIPTION
        Walks segment by segment from BaseDir; each segment is either a literal directory
        name or '*' which matches any single directory level at that position.
        Returns an array of full paths that match the pattern. Empty array if no matches.

        This is NOT recursive globbing — '*' matches exactly one level.
        For recursive matching, chain multiple '*' segments: @("*", "*", "target").
    .PARAMETER BaseDir
        The root directory to start resolution from. Must exist.
    .PARAMETER Segments
        Array of path segments relative to BaseDir. Use '*' to match any single directory.
        Empty/whitespace segments are skipped (treated as no-op).
        Examples:
          @("lib")                          → <BaseDir>/lib
          @("apps", "*")                    → all subdirectories of <BaseDir>/apps
          @("projects", "*", "libs", "foo") → <BaseDir>/projects/*/libs/foo
          @()                               → returns @(BaseDir)
    .OUTPUTS
        Array of full directory paths matching the pattern.
        Always returns an array (even for 0 or 1 results).
    .EXAMPLE
        PS> Resolve-PathPattern -BaseDir "D:\repo" -Segments @("apps")
        D:\repo\apps
    .EXAMPLE
        PS> Resolve-PathPattern -BaseDir "D:\repo" -Segments @("*", "libs", "caffe-ffi")
        D:\repo\projects\xuanspace\libs\caffe-ffi
    .EXAMPLE
        PS> # Find all subdirectories under lib/
        PS> Resolve-PathPattern -BaseDir $PSScriptRoot -Segments @("lib", "*")
    #>
    [CmdletBinding()]
    [OutputType([string[]])]
    param(
        [Parameter(Mandatory=$true)]
        [string]$BaseDir,

        [Parameter(Mandatory=$false)]
        [string[]]$Segments = @()
    )

    # Validate and resolve BaseDir to absolute path
    if (-not (Test-Path $BaseDir -PathType Container)) {
        return [string[]]@()
    }
    try {
        $baseResolved = (Resolve-Path $BaseDir -ErrorAction Stop).Path
    } catch {
        return [string[]]@()
    }

    $current = [string[]]@($baseResolved)

    foreach ($seg in $Segments) {
        # Skip empty/whitespace segments (treat as no-op)
        if ([string]::IsNullOrWhiteSpace($seg)) { continue }

        $next = [System.Collections.Generic.List[string]]::new()
        foreach ($dir in $current) {
            if ($seg -eq "*") {
                foreach ($d in (Get-ChildItem -Path $dir -Directory -ErrorAction SilentlyContinue)) {
                    $next.Add($d.FullName)
                }
            } else {
                $candidate = Join-Path $dir $seg
                if (Test-Path $candidate -PathType Container) {
                    try {
                        $next.Add((Resolve-Path $candidate -ErrorAction Stop).Path)
                    } catch {
                        # Path existed but Resolve-Path failed; skip
                    }
                }
            }
        }
        $current = $next.ToArray()
        if ($current.Count -eq 0) {
            return [string[]]@()
        }
    }
    return [string[]]$current
}

Export-ModuleMember -Function @(
    "Resolve-PathPattern"
)
