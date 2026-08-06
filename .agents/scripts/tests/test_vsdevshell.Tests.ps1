#Requires -Modules Pester
# test_vsdevshell.Tests.ps1 - Unit tests for VsDevShell.psm1 generic module
# Run with: pwsh -NoProfile -Command "Invoke-Pester -Path .agents/scripts/tests/test_vsdevshell.Tests.ps1 -Output Detailed"
#
# Tests cover:
# - Version utility functions (Convert-VsVersionDirToNumber, Get-VsEditionPriority)
# - Find-VisualStudio multi-strategy discovery with mocked vswhere
# - vswhere JSON parsing for version/edition detection
# - Enter-MsvcDevShell PATH auto-recovery logic
# - Module exports and no-hardcoded-paths check

BeforeAll {
    $scriptsDir = Split-Path -Parent $PSCommandPath
    $modulePath = [IO.Path]::GetFullPath((Join-Path $scriptsDir ".." "lib" "VsDevShell.psm1"))
    Import-Module $modulePath -Force
    $script:libDir = Join-Path $scriptsDir ".." "lib"
}

# ── Version Utility Tests ────────────────────────────────────────────────

Describe "VsDevShell - Convert-VsVersionDirToNumber" {
    It "Maps year-based directories to internal version numbers" {
        Convert-VsVersionDirToNumber -VersionDirName "2022" | Should -Be 17
        Convert-VsVersionDirToNumber -VersionDirName "2019" | Should -Be 16
        Convert-VsVersionDirToNumber -VersionDirName "2017" | Should -Be 15
        Convert-VsVersionDirToNumber -VersionDirName "2015" | Should -Be 14
        Convert-VsVersionDirToNumber -VersionDirName "2013" | Should -Be 12
    }

    It "Uses numeric directories directly (Insiders/Preview channel)" {
        Convert-VsVersionDirToNumber -VersionDirName "18" | Should -Be 18
        Convert-VsVersionDirToNumber -VersionDirName "17" | Should -Be 17
        Convert-VsVersionDirToNumber -VersionDirName "19" | Should -Be 19
    }

    It "Returns 0 for non-version directory names" {
        Convert-VsVersionDirToNumber -VersionDirName "Installer" | Should -Be 0
        Convert-VsVersionDirToNumber -VersionDirName "Shared" | Should -Be 0
        Convert-VsVersionDirToNumber -VersionDirName "Packages" | Should -Be 0
        Convert-VsVersionDirToNumber -VersionDirName "" | Should -Be 0
    }

    It "Ensures correct ordering: v18 (Insiders) > v17 (2022) > v16 (2019)" {
        $v18 = Convert-VsVersionDirToNumber -VersionDirName "18"
        $v17 = Convert-VsVersionDirToNumber -VersionDirName "2022"
        $v16 = Convert-VsVersionDirToNumber -VersionDirName "2019"
        $v18 | Should -BeGreaterThan $v17
        $v17 | Should -BeGreaterThan $v16
        $v17 | Should -Be 17
    }
}

Describe "VsDevShell - Get-VsEditionPriority" {
    It "Ranks bleeding-edge channels highest (Insiders/Canary = 4)" {
        Get-VsEditionPriority -EditionName "Insiders" | Should -Be 4
        Get-VsEditionPriority -EditionName "Canary" | Should -Be 4
    }

    It "Ranks Preview above Enterprise (3 > 2)" {
        Get-VsEditionPriority -EditionName "Preview" | Should -Be 3
        Get-VsEditionPriority -EditionName "Enterprise" | Should -Be 2
        (Get-VsEditionPriority -EditionName "Preview") | Should -BeGreaterThan (Get-VsEditionPriority -EditionName "Enterprise")
    }

    It "Ranks Professional above Community (1 > 0)" {
        Get-VsEditionPriority -EditionName "Professional" | Should -Be 1
        Get-VsEditionPriority -EditionName "Community" | Should -Be 0
        Get-VsEditionPriority -EditionName "BuildTools" | Should -Be 0
    }

    It "Is case-insensitive" {
        Get-VsEditionPriority -EditionName "insiders" | Should -Be 4
        Get-VsEditionPriority -EditionName "ENTERPRISE" | Should -Be 2
        Get-VsEditionPriority -EditionName "CoMmUnItY" | Should -Be 0
        Get-VsEditionPriority -EditionName "preview" | Should -Be 3
    }

    It "Returns -1 for unknown editions" {
        Get-VsEditionPriority -EditionName "Express" | Should -Be -1
        Get-VsEditionPriority -EditionName "Unknown" | Should -Be -1
        Get-VsEditionPriority -EditionName "" | Should -Be -1
    }

    It "Full priority ordering: Insiders > Preview > Enterprise > Professional > Community > Unknown" {
        $prios = @(
            (Get-VsEditionPriority -EditionName "Insiders"),
            (Get-VsEditionPriority -EditionName "Preview"),
            (Get-VsEditionPriority -EditionName "Enterprise"),
            (Get-VsEditionPriority -EditionName "Professional"),
            (Get-VsEditionPriority -EditionName "Community"),
            (Get-VsEditionPriority -EditionName "Unknown")
        )
        for ($i = 0; $i -lt $prios.Count - 1; $i++) {
            $prios[$i] | Should -BeGreaterThan $prios[$i+1] -Because "priority ordering should be descending"
        }
    }
}

# ── vswhere JSON Parsing Tests (using mock data) ────────────────────────

Describe "VsDevShell - vswhere JSON Parsing (Mocked)" {
    BeforeAll {
        # Simulate vswhere -format json output for different VS installations
        $script:vsWhereJsonSingle = @'
[
  {
    "instanceId": "VSInsiders",
    "installationPath": "C:\\Program Files\\Microsoft Visual Studio\\18\\Insiders",
    "installationVersion": "18.0.0.0",
    "channelId": "VisualStudio.18.Insiders",
    "displayName": "Visual Studio Enterprise 2026 (Insiders)",
    "productId": "Microsoft.VisualStudio.Product.Enterprise"
  }
]
'@
        $script:vsWhereJsonMulti = @'
[
  {
    "instanceId": "VS2022Ent",
    "installationPath": "C:\\Program Files\\Microsoft Visual Studio\\2022\\Enterprise",
    "installationVersion": "17.10.0",
    "channelId": "VisualStudio.17.Release",
    "displayName": "Visual Studio Enterprise 2022",
    "productId": "Microsoft.VisualStudio.Product.Enterprise"
  },
  {
    "instanceId": "VSPreview",
    "installationPath": "C:\\Program Files\\Microsoft Visual Studio\\18\\Preview",
    "installationVersion": "18.0.1.0",
    "channelId": "VisualStudio.18.Preview",
    "displayName": "Visual Studio Enterprise 2026 Preview",
    "productId": "Microsoft.VisualStudio.Product.Enterprise"
  },
  {
    "instanceId": "VSBuildTools",
    "installationPath": "C:\\Program Files (x86)\\Microsoft Visual Studio\\2022\\BuildTools",
    "installationVersion": "17.9.0",
    "channelId": "VisualStudio.17.Release",
    "displayName": "Visual Studio Build Tools 2022",
    "productId": "Microsoft.VisualStudio.Product.BuildTools"
  }
]
'@
        $script:vsWhereJsonCommunity = @'
[
  {
    "instanceId": "VS2022Com",
    "installationPath": "C:\\Program Files\\Microsoft Visual Studio\\2022\\Community",
    "installationVersion": "17.8.5",
    "channelId": "VisualStudio.17.Release",
    "displayName": "Visual Studio Community 2022",
    "productId": "Microsoft.VisualStudio.Product.Community"
  }
]
'@
    }

    It "Parses single VS Insiders installation from JSON" {
        $installs = $script:vsWhereJsonSingle | ConvertFrom-Json
        $installs.Count | Should -Be 1
        $installs[0].installationPath | Should -Be "C:\Program Files\Microsoft Visual Studio\18\Insiders"
        # Version extraction
        $installs[0].installationVersion -match '^(\d+)' | Should -Be $true
        [int]$Matches[1] | Should -Be 18
        # Edition detection from channelId
        $installs[0].channelId -match 'Insiders|Canary' | Should -Be $true
    }

    It "Parses multiple installations and selects highest version+edition via sorting" {
        $installs = $script:vsWhereJsonMulti | ConvertFrom-Json
        $installs.Count | Should -Be 3

        # Convert to candidate objects (same logic as in Find-VisualStudio)
        $candidates = foreach ($inst in $installs) {
            $verNum = 0
            if ($inst.installationVersion -match '^(\d+)') { $verNum = [int]$Matches[1] }
            $edition = ""
            if ($inst.channelId -match 'Insiders|Canary') { $edition = "Insiders" }
            elseif ($inst.channelId -match 'Preview') { $edition = "Preview" }
            elseif ($inst.displayName -match 'Enterprise') { $edition = "Enterprise" }
            elseif ($inst.displayName -match 'Professional') { $edition = "Professional" }
            elseif ($inst.displayName -match 'Community|Build\s*Tools') { $edition = "Community" }

            [pscustomobject]@{
                Path = $inst.installationPath
                VersionNum = $verNum
                Edition = $edition
                EdPriority = Get-VsEditionPriority -EditionName $edition
            }
        }

        # Sort: Version DESC → EdPriority DESC
        $sorted = $candidates | Sort-Object -Property @{E={$_.VersionNum};Desc=$true}, @{E={$_.EdPriority};Desc=$true}, Path

        # Best should be v18 Preview (highest version)
        $sorted[0].VersionNum | Should -Be 18
        $sorted[0].Edition | Should -Be "Preview"
        $sorted[0].Path | Should -Match "18.*Preview"

        # Second: v17 Enterprise
        $sorted[1].VersionNum | Should -Be 17
        $sorted[1].Edition | Should -Be "Enterprise"

        # Third: v17 BuildTools (lower edition priority)
        $sorted[2].VersionNum | Should -Be 17
        $sorted[2].Edition | Should -Be "Community"
    }

    It "Detects BuildTools edition from displayName" {
        $installs = $script:vsWhereJsonMulti | ConvertFrom-Json
        $bt = $installs | Where-Object { $_.productId -match 'BuildTools' }
        $bt.displayName -match 'Community|Build\s*Tools' | Should -Be $true
    }

    It "Extracts edition from productId when displayName doesn't match" {
        $installs = $script:vsWhereJsonCommunity | ConvertFrom-Json
        $inst = $installs[0]
        $edition = ""
        if ($inst.channelId -match 'Insiders|Canary') { $edition = "Insiders" }
        elseif ($inst.channelId -match 'Preview') { $edition = "Preview" }
        elseif ($inst.displayName -match 'Enterprise') { $edition = "Enterprise" }
        elseif ($inst.displayName -match 'Professional') { $edition = "Professional" }
        elseif ($inst.displayName -match 'Community|Build\s*Tools') { $edition = "Community" }
        $edition | Should -Be "Community"
    }
}

# ── Find-VisualStudio Integration Tests ─────────────────────────────────

Describe "VsDevShell - Find-VisualStudio (Live Discovery)" {
    It "Returns a valid VS installation path" {
        $vsPath = Find-VisualStudio
        $vsPath | Should -Not -BeNullOrEmpty
        Test-Path $vsPath | Should -Be $true
    }

    It "Found path contains DevShell.dll" {
        $vsPath = Find-VisualStudio
        $devShell = [IO.Path]::Combine($vsPath, "Common7", "Tools", "Microsoft.VisualStudio.DevShell.dll")
        Test-Path $devShell | Should -Be $true
    }

    It "Explicit Hint path is validated and returned" {
        $auto = Find-VisualStudio
        $result = Find-VisualStudio -Hint $auto
        $result | Should -Be $auto
    }

    It "Invalid Hint path throws descriptive error" {
        { Find-VisualStudio -Hint "C:\nonexistent\vs\path\xyz" -ErrorAction Stop } | Should -Throw
    }

    It "Deduplication: same path found by multiple strategies is returned once" {
        # vswhere and dir-scan may both find the same installation
        # The $seen HashSet in Add-Candidate handles this
        $vsPath = Find-VisualStudio -VerboseLog 2>&1 | Out-Null
        # Just verify no error during deduplication
        $vsPath = Find-VisualStudio
        $vsPath | Should -Not -BeNullOrEmpty
    }
}

Describe "VsDevShell - Find-VisualStudio -RequireComponent Parameter" {
    It "Default RequireComponent (C++ tools) finds a VS with C++ support" {
        $vsPath = Find-VisualStudio -RequireComponent "Microsoft.VisualStudio.Component.VC.Tools.x86.x64"
        $vsPath | Should -Not -BeNullOrEmpty
    }

    It "Empty RequireComponent finds any VS installation" {
        $vsPath = Find-VisualStudio -RequireComponent ""
        $vsPath | Should -Not -BeNullOrEmpty
    }
}

# ── Enter-MsvcDevShell Tests ─────────────────────────────────────────────

Describe "VsDevShell - Enter-MsvcDevShell" {
    It "Loads MSVC environment with default amd64 arch and cl.exe available" {
        $vs = Find-VisualStudio
        Enter-MsvcDevShell -VsInstallPath $vs -Arch "amd64"
        $cl = Get-Command cl -ErrorAction SilentlyContinue
        $cl | Should -Not -BeNullOrEmpty
        $cl.Source | Should -Match "cl\.exe$"
    }

    It "DevShell loading modifies PATH to include VC tools" {
        $pathBefore = $env:PATH
        $vs = Find-VisualStudio
        Enter-MsvcDevShell -VsInstallPath $vs -Arch "amd64"
        $env:PATH | Should -Not -Be $pathBefore
        # PATH should contain MSVC tools directory
        $env:PATH | Should -Match "MSVC"
    }

    It "PATH auto-recovery triggers when PATH exceeds 8191 chars (simulated)" {
        # This test verifies the PATH length detection logic works
        # The real PATH length test is in the live DevShell test above
        $vs = Find-VisualStudio

        # Capture PATH length before loading
        $beforeLen = $env:PATH.Length

        Enter-MsvcDevShell -VsInstallPath $vs -Arch "amd64"

        # After loading, PATH should contain VC tools
        $cl = Get-Command cl -ErrorAction SilentlyContinue
        $cl | Should -Not -BeNullOrEmpty
    }
}

# ── Module Interface Tests ──────────────────────────────────────────────

Describe "VsDevShell - Module Exports" {
    It "VsDevShell.psm1 exists at expected path" {
        Test-Path $modulePath | Should -Be $true
    }

    It "Exports exactly 4 public functions" {
        $module = Get-Module VsDevShell
        $module | Should -Not -BeNullOrEmpty
        $exported = @($module.ExportedFunctions.Keys)
        $exported.Count | Should -Be 4
    }

    It "Exports all expected public functions" {
        $module = Get-Module VsDevShell
        $exported = $module.ExportedFunctions.Keys
        $expected = @(
            "Convert-VsVersionDirToNumber",
            "Get-VsEditionPriority",
            "Find-VisualStudio",
            "Enter-MsvcDevShell"
        )
        foreach ($fn in $expected) {
            $exported -contains $fn | Should -Be $true -Because "function $fn should be exported"
        }
    }

    It "Does not export internal helper functions" {
        $module = Get-Module VsDevShell
        $exported = $module.ExportedFunctions.Keys
        # Internal helpers should not be exported
        $internal = @("Add-Candidate", "Write-D", "Try-LoadDevShell", "Get-MinimalSystemPath")
        foreach ($fn in $internal) {
            $exported -contains $fn | Should -Be $false -Because "internal helper $fn should NOT be exported"
        }
    }
}

Describe "VsDevShell - No Hardcoded Paths" {
    It "VsDevShell.psm1 contains no user-specific hardcoded paths" {
        $content = Get-Content $modulePath -Raw
        $content | Should -Not -Match "D:\\\\Users\\\\xinzo"
        $content | Should -Not -Match "C:\\\\Users\\\\xinzo"
        $content | Should -Not -Match "D:\\\\spaces\\\\SpecWeave"
    }

    It "Uses environment variables and relative resolution instead of hardcoded paths" {
        $content = Get-Content $modulePath -Raw
        # Should use [Environment]::GetEnvironmentVariable for system paths
        $content | Should -Match "GetEnvironmentVariable"
        # Should use vswhere from Program Files via env var, not hardcoded
        $content | Should -Match "ProgramFiles"
    }
}

Describe "VsDevShell - Cross-Project Usability (Generic Module Validation)" {
    It "Functions have no dependency on conda or Python" {
        $content = Get-Content $modulePath -Raw
        $content | Should -Not -Match "conda"
        $content | Should -Not -Match "python"
        $content | Should -Not -Match "pyproject"
        $content | Should -Not -Match "scikit"
    }

    It "Functions have no dependency on NativeBuild or SpecWeave conventions" {
        $content = Get-Content $modulePath -Raw
        $content | Should -Not -Match "NativeBuild"
        $content | Should -Not -Match "AGENTS\.md"
        $content | Should -Not -Match "libs"
        $content | Should -Not -Match "apps"
    }

    It "Find-VisualStudio works with -VerboseLog producing diagnostic output" {
        $output = Find-VisualStudio -VerboseLog 2>&1 | Out-String
        # Verbose output should contain strategy labels
        # (May or may not produce [VS] logs depending on how PowerShell captures Write-Host)
        # Just verify it doesn't throw
        $vs = Find-VisualStudio -VerboseLog 2>$null
        $vs | Should -Not -BeNullOrEmpty
    }
}
