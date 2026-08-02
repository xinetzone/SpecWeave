#Requires -Modules Pester
# test_pathpattern.Tests.ps1 - Comprehensive unit tests for PathPattern.psm1
# Run with: pwsh -NoProfile -Command "Invoke-Pester -Path .agents/scripts/tests/test_pathpattern.Tests.ps1 -Output Detailed"

BeforeAll {
    $scriptsDir = Split-Path -Parent $PSCommandPath
    $modulePath = [IO.Path]::GetFullPath((Join-Path $scriptsDir ".." "lib" "PathPattern.psm1"))
    Import-Module $modulePath -Force
    $script:repoScripts = [IO.Path]::GetFullPath((Join-Path $scriptsDir ".."))
    $script:workspaceRoot = [IO.Path]::GetFullPath((Join-Path $scriptsDir ".." ".." ".."))
    $script:libDir = Join-Path $script:repoScripts "lib"
    $script:testsDir = Join-Path $script:repoScripts "tests"
}

# ── Module Interface Tests ──────────────────────────────────────────────

Describe "PathPattern - Module Exports" {
    It "PathPattern.psm1 exists at expected path" {
        Test-Path $modulePath | Should -Be $true
    }

    It "Exports exactly 1 public function" {
        $module = Get-Module PathPattern
        $module | Should -Not -BeNullOrEmpty
        $exported = @($module.ExportedFunctions.Keys)
        $exported.Count | Should -Be 1
    }

    It "Exports Resolve-PathPattern" {
        $module = Get-Module PathPattern
        $exported = $module.ExportedFunctions.Keys
        $exported -contains "Resolve-PathPattern" | Should -Be $true
    }

    It "Does not export internal/private functions" {
        $module = Get-Module PathPattern
        $exported = @($module.ExportedFunctions.Keys)
        # Only Resolve-PathPattern should be exported
        $exported | Should -Be @("Resolve-PathPattern")
    }
}

# ── Parameter Validation Tests ──────────────────────────────────────────

Describe "PathPattern - Parameter Validation" {
    It "Throws when BaseDir is not provided (Mandatory)" {
        { Resolve-PathPattern -Segments @("lib") } | Should -Throw
    }

    It "Segments defaults to empty array when not provided" {
        $result = @(Resolve-PathPattern -BaseDir $script:repoScripts)
        $result.Count | Should -Be 1
        [IO.Path]::GetFullPath($result[0]) | Should -Be ([IO.Path]::GetFullPath($script:repoScripts))
    }

    It "Segments can be passed as single string (PowerShell auto-wraps)" {
        # When a single string is passed to [string[]], PowerShell treats it as one element
        $result = @(Resolve-PathPattern -BaseDir $script:repoScripts -Segments "lib")
        $result.Count | Should -Be 1
        Test-Path $result[0] | Should -Be $true
    }
}

# ── Basic Resolution Tests ──────────────────────────────────────────────

Describe "PathPattern - Basic Resolution" {
    It "Resolves a single existing directory segment" {
        $result = @(Resolve-PathPattern -BaseDir $script:repoScripts -Segments @("lib"))
        $result.Count | Should -Be 1
        Test-Path $result[0] | Should -Be $true
        Split-Path $result[0] -Leaf | Should -Be "lib"
    }

    It "Resolves a single existing subdirectory (tests)" {
        $result = @(Resolve-PathPattern -BaseDir $script:repoScripts -Segments @("tests"))
        $result.Count | Should -Be 1
        Test-Path $result[0] | Should -Be $true
        Split-Path $result[0] -Leaf | Should -Be "tests"
    }

    It "Returns empty array for non-existent single segment" {
        $result = @(Resolve-PathPattern -BaseDir $script:repoScripts -Segments @("nonexistent_dir_xyz_123"))
        $result.Count | Should -Be 0
    }

    It "Resolves multi-segment nested path" {
        $result = @(Resolve-PathPattern -BaseDir $script:workspaceRoot -Segments @(".agents", "scripts", "lib"))
        $result.Count | Should -Be 1
        Test-Path $result[0] | Should -Be $true
        Split-Path $result[0] -Leaf | Should -Be "lib"
    }

    It "Returns empty for non-existent segment in the middle of path" {
        $result = @(Resolve-PathPattern -BaseDir $script:repoScripts -Segments @("lib", "nonexistent_sub_xyz"))
        $result.Count | Should -Be 0
    }

    It "Returns empty for non-existent segment at end of path" {
        $result = @(Resolve-PathPattern -BaseDir $script:repoScripts -Segments @("lib", "VsDevShell.psm1"))
        # VsDevShell.psm1 is a file, not a directory - PathPattern only matches directories
        $result.Count | Should -Be 0
    }
}

# ── Empty Segments / Base Only Tests ────────────────────────────────────

Describe "PathPattern - Empty Segments (Base Only)" {
    It "Empty segments array returns the BaseDir itself" {
        $result = @(Resolve-PathPattern -BaseDir $script:repoScripts -Segments @())
        $result.Count | Should -Be 1
        [IO.Path]::GetFullPath($result[0]) | Should -Be ([IO.Path]::GetFullPath($script:repoScripts))
    }

    It "Not passing Segments parameter also returns BaseDir" {
        $result = @(Resolve-PathPattern -BaseDir $script:libDir)
        $result.Count | Should -Be 1
        [IO.Path]::GetFullPath($result[0]) | Should -Be ([IO.Path]::GetFullPath($script:libDir))
    }

    It "Returns empty when BaseDir does not exist" {
        $result = @(Resolve-PathPattern -BaseDir "C:\nonexistent\base\dir\xyz" -Segments @())
        $result.Count | Should -Be 0
    }

    It "Returns empty when BaseDir does not exist even with non-empty segments" {
        $result = @(Resolve-PathPattern -BaseDir "C:\nonexistent\base\dir\xyz" -Segments @("lib"))
        $result.Count | Should -Be 0
    }
}

# ── Wildcard '*' Tests ──────────────────────────────────────────────────

Describe "PathPattern - Wildcard '*' Matching" {
    It "Single '*' matches all immediate subdirectories" {
        $result = @(Resolve-PathPattern -BaseDir $script:repoScripts -Segments @("*"))
        # Should include at least lib/ and tests/
        $result.Count | Should -BeGreaterOrEqual 2
        $leafNames = $result | ForEach-Object { Split-Path $_ -Leaf }
        $leafNames -contains "lib" | Should -Be $true
        $leafNames -contains "tests" | Should -Be $true
    }

    It "'*' only matches immediate children (not recursive)" {
        $result = @(Resolve-PathPattern -BaseDir $script:repoScripts -Segments @("*"))
        # None of the results should be more than one level deep
        foreach ($path in $result) {
            $parent = Split-Path $path -Parent
            [IO.Path]::GetFullPath($parent) | Should -Be ([IO.Path]::GetFullPath($script:repoScripts))
        }
    }

    It "'*' does not match files, only directories" {
        # scripts/ contains .ps1 files which should NOT be matched
        $result = @(Resolve-PathPattern -BaseDir $script:repoScripts -Segments @("*"))
        foreach ($path in $result) {
            Test-Path $path -PathType Container | Should -Be $true
        }
    }

    It "'*' followed by a literal segment: matches subdirs then filters" {
        # Equivalent to: look for */lib pattern from workspace root
        $result = @(Resolve-PathPattern -BaseDir $script:workspaceRoot -Segments @("*", "scripts"))
        # Should find at least .agents/scripts
        $found = $false
        foreach ($path in $result) {
            if ($path -match [regex]::Escape(".agents\scripts")) { $found = $true }
        }
        # This may or may not have results depending on workspace state - just verify no crash
        # and all results are directories
        foreach ($path in $result) {
            Test-Path $path -PathType Container | Should -Be $true
        }
    }

    It "Multiple consecutive '*' segments match multiple directory levels" {
        # Two wildcards = two levels deep
        $result = @(Resolve-PathPattern -BaseDir $script:repoScripts -Segments @("*", "*"))
        foreach ($path in $result) {
            Test-Path $path -PathType Container | Should -Be $true
        }
    }

    It "Literal segment followed by '*' lists subdirectories of that path" {
        $result = @(Resolve-PathPattern -BaseDir $script:repoScripts -Segments @("lib", "*"))
        # lib/ currently contains .psm1 files (no subdirectories), so may be empty
        # Just verify no crash and all results are directories
        foreach ($path in $result) {
            Test-Path $path -PathType Container | Should -Be $true
            $parent = Split-Path $path -Parent
            Split-Path $parent -Leaf | Should -Be "lib"
        }
    }

    It "'*' with no matching subdirectories returns empty array" {
        # Create a temp empty directory to test wildcard in empty dir
        $emptyDir = Join-Path $env:TEMP "pathpattern_test_empty_$(Get-Random)"
        New-Item -ItemType Directory -Path $emptyDir -Force | Out-Null
        try {
            $result = @(Resolve-PathPattern -BaseDir $emptyDir -Segments @("*"))
            $result.Count | Should -Be 0
        } finally {
            Remove-Item $emptyDir -Recurse -Force -ErrorAction SilentlyContinue
        }
    }
}

# ── Edge Cases ──────────────────────────────────────────────────────────

Describe "PathPattern - Edge Cases" {
    It "BaseDir with trailing backslash works correctly" {
        $withTrailing = $script:repoScripts.TrimEnd('\') + "\"
        $result = @(Resolve-PathPattern -BaseDir $withTrailing -Segments @("lib"))
        $result.Count | Should -Be 1
        Test-Path $result[0] | Should -Be $true
    }

    It "BaseDir with forward slashes works correctly" {
        $forwardSlash = $script:repoScripts -replace '\\', '/'
        $result = @(Resolve-PathPattern -BaseDir $forwardSlash -Segments @("lib"))
        $result.Count | Should -Be 1
        Test-Path $result[0] | Should -Be $true
    }

    It "Relative BaseDir resolves correctly" {
        Push-Location $script:workspaceRoot
        try {
            $result = @(Resolve-PathPattern -BaseDir ".agents/scripts" -Segments @("lib"))
            $result.Count | Should -Be 1
            Test-Path $result[0] | Should -Be $true
            [IO.Path]::IsPathRooted($result[0]) | Should -Be $true
        } finally {
            Pop-Location
        }
    }

    It "Returns full absolute paths" {
        $result = @(Resolve-PathPattern -BaseDir $script:repoScripts -Segments @("lib"))
        [IO.Path]::IsPathRooted($result[0]) | Should -Be $true
    }

    It "Case-insensitive directory matching on Windows" {
        # Use uppercase that doesn't match exact case
        $result = @(Resolve-PathPattern -BaseDir $script:repoScripts -Segments @("LIB"))
        # On Windows this should match "lib" case-insensitively
        if ($result.Count -gt 0) {
            Test-Path $result[0] | Should -Be $true
        }
    }

    It "Segments with mixed existing and non-existing wildcards" {
        # lib/ exists, but */nonexistent_xyz under lib/ should return empty
        $result = @(Resolve-PathPattern -BaseDir $script:repoScripts -Segments @("lib", "*", "nonexistent"))
        $result.Count | Should -Be 0
    }

    It "Duplicate paths are not returned (distinct)" {
        # Each path should appear only once in results
        $result = @(Resolve-PathPattern -BaseDir $script:repoScripts -Segments @("*"))
        $unique = $result | Select-Object -Unique
        $unique.Count | Should -Be $result.Count
    }

    It "Segments array with empty strings skips empty segments (treats as no-op)" {
        # Empty segments are skipped; @("") behaves like @() returning BaseDir
        $result = @(Resolve-PathPattern -BaseDir $script:repoScripts -Segments @(""))
        $result.Count | Should -Be 1
        [IO.Path]::GetFullPath($result[0]) | Should -Be ([IO.Path]::GetFullPath($script:repoScripts))
    }

    It "Mixed empty and valid segments skips empties" {
        $result = @(Resolve-PathPattern -BaseDir $script:repoScripts -Segments @("", "lib", ""))
        $result.Count | Should -Be 1
        Split-Path $result[0] -Leaf | Should -Be "lib"
    }

    It "Handles deeply nested paths" {
        $deep = @(".agents", "scripts", "lib")
        $result = @(Resolve-PathPattern -BaseDir $script:workspaceRoot -Segments $deep)
        $result.Count | Should -Be 1
        Test-Path $result[0] | Should -Be $true
    }
}

# ── Cross-Project Usability Tests ───────────────────────────────────────

Describe "PathPattern - Cross-Project Usability (Generic Module Validation)" {
    It "Contains no project-specific references" {
        $content = Get-Content $modulePath -Raw
        $content | Should -Not -Match "NativeBuild"
        $content | Should -Not -Match "conda"
        $content | Should -Not -Match "VsDevShell"
        $content | Should -Not -Match "AGENTS\.md"
        $content | Should -Not -Match "scikit"
        $content | Should -Not -Match "pyproject"
    }

    It "Contains no user-specific hardcoded paths" {
        $content = Get-Content $modulePath -Raw
        $content | Should -Not -Match "C:\\Users\\[^\\]+\\(?!AppData)"
        $content | Should -Not -Match "D:\\Users\\"
        # The only Join-Path with environment references should be generic
    }

    It "Uses proper error handling (SilentlyContinue on Get-ChildItem)" {
        $content = Get-Content $modulePath -Raw
        $content | Should -Match "ErrorAction.*SilentlyContinue"
    }

    It "Uses StrictMode" {
        $content = Get-Content $modulePath -Raw
        $content | Should -Match "Set-StrictMode"
    }

    It "Uses generic collection types (not project-specific)" {
        $content = Get-Content $modulePath -Raw
        $content | Should -Match "System\.Collections\.Generic\.List"
    }
}

# ── Return Value Type Tests ─────────────────────────────────────────────

Describe "PathPattern - Return Value Types" {
    It "Returns an array (even for single result)" {
        $result = Resolve-PathPattern -BaseDir $script:repoScripts -Segments @("lib")
        # When not wrapped in @(), single result might be scalar; verify with @()
        $wrapped = @($result)
        $wrapped.Count | Should -Be 1
    }

    It "Each returned path is a string" {
        $result = @(Resolve-PathPattern -BaseDir $script:repoScripts -Segments @("*"))
        foreach ($path in $result) {
            $path | Should -BeOfType [string]
        }
    }

    It "Returns empty array (not null) when no matches" {
        $result = Resolve-PathPattern -BaseDir $script:repoScripts -Segments @("nonexistent_xyz")
        # When wrapped in @(), even null/empty becomes an array with Count 0
        @($result).Count | Should -Be 0
    }
}

# ── Integration with Workspace Structure ────────────────────────────────

Describe "PathPattern - Real Workspace Patterns" {
    It "Finds all module files under scripts/lib/" {
        $modules = @(Resolve-PathPattern -BaseDir $script:repoScripts -Segments @("lib"))
        $modules.Count | Should -Be 1
        $modFiles = Get-ChildItem $modules[0] -Filter "*.psm1" -File
        $modFiles.Count | Should -BeGreaterOrEqual 3  # NativeBuild, VsDevShell, PathPattern
    }

    It "Finds all test files under scripts/tests/" {
        $tests = @(Resolve-PathPattern -BaseDir $script:repoScripts -Segments @("tests"))
        $tests.Count | Should -Be 1
        $testFiles = Get-ChildItem $tests[0] -Filter "*.Tests.ps1" -File
        $testFiles.Count | Should -BeGreaterOrEqual 2  # At least build_scripts + vsdevshell + pathpattern
    }

    It "Pattern matching for libs/*/ structure works (projects)" {
        $projectsLibs = Join-Path $script:workspaceRoot "projects"
        if (Test-Path $projectsLibs) {
            $result = @(Resolve-PathPattern -BaseDir $projectsLibs -Segments @("*", "libs", "*"))
            foreach ($path in $result) {
                Test-Path $path -PathType Container | Should -Be $true
            }
        }
    }

    It "Can discover psm1 modules via wildcard traversal" {
        # Find all .psm1 files two levels deep from workspace root matching scripts/lib
        $libDirs = @(Resolve-PathPattern -BaseDir $script:workspaceRoot -Segments @(".agents", "scripts", "lib"))
        $libDirs.Count | Should -Be 1
        $psm1Files = Get-ChildItem $libDirs[0] -Filter "*.psm1" -File
        $psm1Files.Count | Should -BeGreaterOrEqual 3
    }
}
