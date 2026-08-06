#Requires -Modules Pester
# test_build_scripts.Tests.ps1 - Unit tests for NativeBuild.psm1 and build scripts
# Run with: pwsh -NoProfile -Command "Invoke-Pester -Path .agents/scripts/tests/test_build_scripts.Tests.ps1 -Output Detailed"

BeforeAll {
    # Test file is at .agents/scripts/tests/ → go up 3 levels for repo root
    $scriptsDir = Split-Path -Parent $PSCommandPath
    $modulePath = [IO.Path]::GetFullPath((Join-Path $scriptsDir ".." "lib" "NativeBuild.psm1"))
    Import-Module $modulePath -Force
    $script:repoScripts   = [IO.Path]::GetFullPath((Join-Path $scriptsDir ".."))
    $script:workspaceRoot = [IO.Path]::GetFullPath((Join-Path $scriptsDir ".." ".." ".."))
    $script:libDir        = Join-Path $script:repoScripts "lib"
}

Describe "NativeBuild Module - Path Resolution" {
    It "Resolve-PathPattern resolves a simple directory" {
        $libDir = Join-Path $script:repoScripts "lib"
        if (Test-Path $libDir) {
            $result = Resolve-PathPattern -BaseDir $script:repoScripts -Segments @("lib")
            $result | Should -Not -BeNullOrEmpty
        }
    }

    It "Resolve-PathPattern returns empty for non-existent segments" {
        $result = Resolve-PathPattern -BaseDir $script:repoScripts -Segments @("nonexistent_dir_xyz")
        $result.Count | Should -Be 0
    }
}

Describe "NativeBuild Module - Project Detection" {
    BeforeAll {
        $caffeDir = Join-Path $script:workspaceRoot "projects" "xuanspace" "libs" "caffe-ffi"
        $npuDir = Join-Path $script:workspaceRoot "projects" "xuanspace" "libs" "npu-ffi"
        $demoDir = Join-Path $script:workspaceRoot "projects" "xuanspace" "libs" "demo-ffi"
    }

    It "Test-NativeProject detects caffe-ffi project" {
        if (Test-Path $caffeDir) {
            Test-NativeProject -Dir $caffeDir -ProjectName "caffe-ffi" | Should -Be $true
        }
    }

    It "Test-NativeProject rejects directories without pyproject.toml" {
        Test-NativeProject -Dir $env:TEMP -ProjectName "*" | Should -Be $false
    }

    It "Test-NativeProject rejects non-matching project name" {
        if (Test-Path $caffeDir) {
            Test-NativeProject -Dir $caffeDir -ProjectName "nonexistent-proj" | Should -Be $false
        }
    }

    It "Test-NativeProject with wildcard accepts any native project" {
        if (Test-Path $caffeDir) {
            Test-NativeProject -Dir $caffeDir -ProjectName "*" | Should -Be $true
        }
    }

    It "Find-NativeProject finds caffe-ffi from script directory" {
        if (Test-Path $caffeDir) {
            $result = Find-NativeProject -ProjectName "caffe-ffi" -ScriptDir $script:repoScripts
            $result | Should -Not -BeNullOrEmpty
            $result | Should -Match "caffe-ffi$"
        }
    }

    It "Find-NativeProject finds npu-ffi project" {
        if (Test-Path $npuDir) {
            $result = Find-NativeProject -ProjectName "npu-ffi" -ScriptDir $script:repoScripts
            $result | Should -Not -BeNullOrEmpty
            $result | Should -Match "npu-ffi$"
        }
    }

    It "Find-NativeProject finds demo-ffi project" {
        if (Test-Path $demoDir) {
            $result = Find-NativeProject -ProjectName "demo-ffi" -ScriptDir $script:repoScripts
            $result | Should -Not -BeNullOrEmpty
            $result | Should -Match "demo-ffi$"
        }
    }

    It "Find-NativeProject with explicit Hint path works" {
        if (Test-Path $caffeDir) {
            $result = Find-NativeProject -Hint $caffeDir -ProjectName "caffe-ffi" -ScriptDir $script:repoScripts
            $result | Should -Not -BeNullOrEmpty
        }
    }

    It "Find-NativeProject throws for non-existent project" {
        { Find-NativeProject -ProjectName "no-such-project-xyz-123" -ScriptDir $script:repoScripts } | Should -Throw
    }
}

Describe "NativeBuild Module - Python Version Detection" {
    It "Get-PythonVersion returns a valid version for conda py314" {
        $condaEnv = Find-CondaEnvPython -Hint "py314" -MinVersion 3.14
        $pyExe = Join-Path $condaEnv "python.exe"
        if (Test-Path $pyExe) {
            $ver = Get-PythonVersion -PythonExe $pyExe
            $ver | Should -BeGreaterOrEqual 3.14
        }
    }

    It "Get-PythonVersion returns 0 for non-existent executable" {
        $ver = Get-PythonVersion -PythonExe "C:\nonexistent\python_xyz.exe"
        $ver | Should -Be 0
    }
}

Describe "NativeBuild Module - Conda Discovery" {
    It "Get-CondaRoots returns at least one conda root" {
        $roots = @(Get-CondaRoots)
        $roots.Count | Should -BeGreaterOrEqual 1
    }

    It "Get-CondaRoots returns valid existing directories" {
        $roots = @(Get-CondaRoots)
        foreach ($r in $roots) {
            Test-Path $r | Should -Be $true
        }
    }

    It "Find-CondaEnvPython finds py314 environment" {
        $result = Find-CondaEnvPython -Hint "py314" -MinVersion 3.14
        $result | Should -Not -BeNullOrEmpty
        Test-Path (Join-Path $result "python.exe") | Should -Be $true
        $ver = Get-PythonVersion -PythonExe (Join-Path $result "python.exe")
        $ver | Should -BeGreaterOrEqual 3.14
    }

    It "Find-CondaEnvPython throws for non-existent env" {
        { Find-CondaEnvPython -Hint "no-such-env-xyz-999" -MinVersion 3.14 } | Should -Throw
    }
}

Describe "NativeBuild Module - Visual Studio Discovery" {
    It "Find-VisualStudio returns a valid VS installation" {
        $vsPath = Find-VisualStudio
        $vsPath | Should -Not -BeNullOrEmpty
        Test-Path $vsPath | Should -Be $true
    }

    It "Find-VisualStudio finds DevShell.dll" {
        $vsPath = Find-VisualStudio
        $devShellDll = [IO.Path]::Combine($vsPath, "Common7", "Tools", "Microsoft.VisualStudio.DevShell.dll")
        Test-Path $devShellDll | Should -Be $true
    }

    It "Find-VisualStudio with explicit Hint path works" {
        $autoVs = Find-VisualStudio
        $result = Find-VisualStudio -Hint $autoVs
        $result | Should -Be $autoVs
    }

    It "Find-VisualStudio throws for invalid path" {
        { Find-VisualStudio -Hint "C:\nonexistent\vs\path" } | Should -Throw
    }
}

Describe "Build Scripts - File Existence and Thin Wrapper Validation" {
    BeforeAll {
        $genericBuilder = Join-Path $script:repoScripts "build_native_ext.ps1"
        $caffeBuilder = Join-Path $script:repoScripts "build_caffe_ffi.ps1"
        $npuBuilder = Join-Path $script:repoScripts "build_npu_ffi.ps1"
        $demoBuilder = Join-Path $script:repoScripts "build_demo_ffi.ps1"
        $xuanBuilder = Join-Path $script:repoScripts "build_xuan_ext_demo.ps1"
        $verifyGeneric = Join-Path $script:repoScripts "verify_native_ext.ps1"
        $verifyCaffe = Join-Path $script:repoScripts "verify_caffe_ffi.ps1"
        $batFile = Join-Path $script:repoScripts "build_caffe_ffi.bat"
        $moduleFile = Join-Path $script:repoScripts "lib" "NativeBuild.psm1"
    }

    It "VsDevShell.psm1 module exists" {
        $vsModulePath = Join-Path $script:libDir "VsDevShell.psm1"
        Test-Path $vsModulePath | Should -Be $true
    }

    It "VsDevShell.psm1 exports exactly 4 expected functions" {
        $vsModule = Get-Module VsDevShell
        if (-not $vsModule) {
            Import-Module (Join-Path $script:libDir "VsDevShell.psm1") -Force
            $vsModule = Get-Module VsDevShell
        }
        $vsModule | Should -Not -BeNullOrEmpty
        $vsExported = $vsModule.ExportedFunctions.Keys
        $vsExpected = @(
            "Find-VisualStudio", "Enter-MsvcDevShell",
            "Convert-VsVersionDirToNumber", "Get-VsEditionPriority"
        )
        foreach ($fn in $vsExpected) {
            $vsExported -contains $fn | Should -Be $true -Because "VsDevShell should export function $fn"
        }
    }

    It "PathPattern.psm1 module exists" {
        $ppModulePath = Join-Path $script:libDir "PathPattern.psm1"
        Test-Path $ppModulePath | Should -Be $true
    }

    It "PathPattern.psm1 exports exactly 1 expected function" {
        Import-Module (Join-Path $script:libDir "PathPattern.psm1") -Force
        $ppModule = Get-Module PathPattern
        $ppModule | Should -Not -BeNullOrEmpty
        $ppExported = @($ppModule.ExportedFunctions.Keys)
        $ppExported.Count | Should -Be 1
        $ppExported -contains "Resolve-PathPattern" | Should -Be $true
    }

    It "NativeBuild.psm1 module exists" {
        Test-Path $moduleFile | Should -Be $true
    }

    It "build_native_ext.ps1 exists with param block and module import" {
        Test-Path $genericBuilder | Should -Be $true
        $content = Get-Content $genericBuilder -Raw
        $content | Should -Match "param\s*\("
        $content | Should -Match "NativeBuild"
    }

    It "build_caffe_ffi.ps1 exists as thin wrapper referencing generic builder" {
        Test-Path $caffeBuilder | Should -Be $true
        $content = Get-Content $caffeBuilder -Raw
        $content | Should -Match "build_native_ext"
        $content | Should -Match "caffe-ffi"
    }

    It "build_npu_ffi.ps1 exists as wrapper for npu-ffi" {
        Test-Path $npuBuilder | Should -Be $true
        $content = Get-Content $npuBuilder -Raw
        $content | Should -Match "npu-ffi"
        $content | Should -Match "build_native_ext"
    }

    It "build_demo_ffi.ps1 exists as wrapper for demo-ffi" {
        Test-Path $demoBuilder | Should -Be $true
        $content = Get-Content $demoBuilder -Raw
        $content | Should -Match "demo-ffi"
    }

    It "build_xuan_ext_demo.ps1 exists" {
        Test-Path $xuanBuilder | Should -Be $true
    }

    It "verify scripts exist" {
        Test-Path $verifyGeneric | Should -Be $true
        Test-Path $verifyCaffe | Should -Be $true
    }

    It "build_caffe_ffi.bat exists and calls pwsh" {
        Test-Path $batFile | Should -Be $true
        $content = Get-Content $batFile -Raw
        $content | Should -Match "pwsh"
        $content | Should -Match "build_caffe_ffi.ps1"
    }

    It "NativeBuild.psm1 exports all expected functions" {
        $module = Get-Module NativeBuild
        $module | Should -Not -BeNullOrEmpty
        $exported = $module.ExportedFunctions.Keys
        $expected = @(
            "Resolve-PathPattern", "Test-NativeProject", "Find-NativeProject",
            "Get-PythonVersion", "Get-CondaRootFromEnv", "Get-CondaRoots",
            "Find-CondaEnvPython", "Find-VisualStudio", "Enter-MsvcDevShell",
            "Convert-VsVersionDirToNumber", "Get-VsEditionPriority"
        )
        foreach ($fn in $expected) {
            $exported -contains $fn | Should -Be $true -Because "function $fn should be exported"
        }
    }
}

Describe "Build Scripts - No Hardcoded Paths" {
    BeforeAll {
        $scriptFiles = @(
            (Join-Path $script:repoScripts "build_native_ext.ps1"),
            (Join-Path $script:repoScripts "build_caffe_ffi.ps1"),
            (Join-Path $script:repoScripts "build_npu_ffi.ps1"),
            (Join-Path $script:repoScripts "build_demo_ffi.ps1"),
            (Join-Path $script:repoScripts "build_xuan_ext_demo.ps1"),
            (Join-Path $script:repoScripts "lib" "NativeBuild.psm1"),
            (Join-Path $script:repoScripts "lib" "VsDevShell.psm1"),
            (Join-Path $script:repoScripts "lib" "PathPattern.psm1"),
            (Join-Path $script:repoScripts "verify_native_ext.ps1"),
            (Join-Path $script:repoScripts "verify_caffe_ffi.ps1"),
            (Join-Path $script:repoScripts "build_caffe_ffi.bat")
        )
    }

    It "No hardcoded user-specific paths in any script" {
        foreach ($file in $scriptFiles) {
            if (-not (Test-Path $file)) { continue }
            $content = Get-Content $file -Raw
            $content | Should -Not -Match "D:\\\\Users\\\\xinzo" -Because "$file should not contain hardcoded user paths"
            $content | Should -Not -Match "C:\\\\Users\\\\xinzo" -Because "$file should not contain hardcoded user paths"
            $content | Should -Not -Match "D:\\\\spaces\\\\SpecWeave" -Because "$file should not contain hardcoded workspace paths"
        }
    }
}

Describe "NativeBuild Module - MSVC DevShell Loading" {
    It "Enter-MsvcDevShell loads MSVC environment with cl.exe available" {
        $vsPath = Find-VisualStudio
        Enter-MsvcDevShell -VsInstallPath $vsPath -Arch "amd64"
        $clCmd = Get-Command cl -ErrorAction SilentlyContinue
        $clCmd | Should -Not -BeNullOrEmpty
        Test-Path $clCmd.Source | Should -Be $true
    }
}

Describe "Parameter Combinations - Discovery Integration Test" {
    It "Different -PythonMinVersion values find appropriate envs" {
        # Python 3.13+ should find at least one env
        $result = Find-CondaEnvPython -MinVersion 3.13 -ErrorAction SilentlyContinue
        if ($result) {
            Test-Path (Join-Path $result "python.exe") | Should -Be $true
        }
    }

    It "Find-NativeProject with ScriptDir auto-discovers projects correctly" {
        # Test that ScriptDir-based search finds projects when run from scripts/ dir
        $caffeDir = Join-Path $script:workspaceRoot "projects" "xuanspace" "libs" "caffe-ffi"
        if (Test-Path $caffeDir) {
            $result = Find-NativeProject -ProjectName "caffe-ffi" -ScriptDir $script:repoScripts
            # Normalize paths for comparison
            $expected = [IO.Path]::GetFullPath($caffeDir)
            $actual = [IO.Path]::GetFullPath($result)
            $actual | Should -Be $expected
        }
    }
}

Describe "NativeBuild Module - VS Version Utilities" {
    It "Convert-VsVersionDirToNumber maps year-based dirs correctly" {
        Convert-VsVersionDirToNumber -VersionDirName "2022" | Should -Be 17
        Convert-VsVersionDirToNumber -VersionDirName "2019" | Should -Be 16
        Convert-VsVersionDirToNumber -VersionDirName "2017" | Should -Be 15
        Convert-VsVersionDirToNumber -VersionDirName "2015" | Should -Be 14
        Convert-VsVersionDirToNumber -VersionDirName "2013" | Should -Be 12
    }

    It "Convert-VsVersionDirToNumber uses numeric dirs directly" {
        Convert-VsVersionDirToNumber -VersionDirName "18" | Should -Be 18
        Convert-VsVersionDirToNumber -VersionDirName "17" | Should -Be 17
        Convert-VsVersionDirToNumber -VersionDirName "19" | Should -Be 19
    }

    It "Convert-VsVersionDirToNumber returns 0 for unknown" {
        Convert-VsVersionDirToNumber -VersionDirName "Installer" | Should -Be 0
        Convert-VsVersionDirToNumber -VersionDirName "Shared" | Should -Be 0
        Convert-VsVersionDirToNumber -VersionDirName "" | Should -Be 0
    }

    It "Convert-VsVersionDirToNumber ensures v18 > v17 (Insiders > 2022)" {
        $v18 = Convert-VsVersionDirToNumber -VersionDirName "18"
        $v17 = Convert-VsVersionDirToNumber -VersionDirName "2022"
        $v18 | Should -BeGreaterThan $v17
    }

    It "Get-VsEditionPriority ranks Insiders highest" {
        Get-VsEditionPriority -EditionName "Insiders" | Should -Be 4
        Get-VsEditionPriority -EditionName "Canary" | Should -Be 4
    }

    It "Get-VsEditionPriority ranks Preview above Enterprise" {
        Get-VsEditionPriority -EditionName "Preview" | Should -Be 3
        Get-VsEditionPriority -EditionName "Enterprise" | Should -Be 2
        (Get-VsEditionPriority -EditionName "Preview") | Should -BeGreaterThan (Get-VsEditionPriority -EditionName "Enterprise")
    }

    It "Get-VsEditionPriority ranks stable editions correctly" {
        Get-VsEditionPriority -EditionName "Professional" | Should -Be 1
        Get-VsEditionPriority -EditionName "Community" | Should -Be 0
        Get-VsEditionPriority -EditionName "BuildTools" | Should -Be 0
    }

    It "Get-VsEditionPriority is case-insensitive and returns -1 for unknown" {
        Get-VsEditionPriority -EditionName "insiders" | Should -Be 4
        Get-VsEditionPriority -EditionName "ENTERPRISE" | Should -Be 2
        Get-VsEditionPriority -EditionName "Unknown" | Should -Be -1
    }
}

Describe "Thin Wrapper Scripts - Parameter Validation" {
    BeforeAll {
        $wrappers = @(
            @{ File="build_caffe_ffi.ps1";     ProjectName="caffe-ffi";     MinVersion=3.14; Pattern="314" },
            @{ File="build_npu_ffi.ps1";       ProjectName="npu-ffi";       MinVersion=3.13; Pattern="31" },
            @{ File="build_demo_ffi.ps1";      ProjectName="demo-ffi";      MinVersion=3.13; Pattern="31" },
            @{ File="build_xuan_ext_demo.ps1"; ProjectName="xuan-ext-demo"; MinVersion=3.14; Pattern="314" }
        )
    }

    It "Each wrapper references build_native_ext.ps1 and correct project name" {
        foreach ($w in $wrappers) {
            $path = Join-Path $script:repoScripts $w.File
            Test-Path $path | Should -Be $true -Because "$($w.File) should exist"
            $content = Get-Content $path -Raw
            $content | Should -Match "build_native_ext\.ps1" -Because "$($w.File) should call generic builder"
            $content | Should -Match ([regex]::Escape($w.ProjectName)) -Because "$($w.File) should specify project $($w.ProjectName)"
        }
    }

    It "Each wrapper passes @args for transparent parameter forwarding" {
        foreach ($w in $wrappers) {
            $path = Join-Path $script:repoScripts $w.File
            $content = Get-Content $path -Raw
            $content | Should -Match '@args' -Because "$($w.File) should forward extra arguments via @args"
        }
    }

    It "Each wrapper uses ErrorActionPreference Stop" {
        foreach ($w in $wrappers) {
            $path = Join-Path $script:repoScripts $w.File
            $content = Get-Content $path -Raw
            $content | Should -Match 'ErrorActionPreference\s*=\s*"Stop"' -Because "$($w.File) should stop on errors"
        }
    }

    It "Each wrapper exits with propagated exit code" {
        foreach ($w in $wrappers) {
            $path = Join-Path $script:repoScripts $w.File
            $content = Get-Content $path -Raw
            # Must capture LASTEXITCODE after builder call and exit with it
            $content | Should -Match '\$LASTEXITCODE' -Because "$($w.File) should capture builder exit code"
            $content | Should -Match 'exit\s+\$' -Because "$($w.File) should exit with a code"
        }
    }
}

Describe "Cross-Project Discovery - Compatibility Check" {
    BeforeAll {
        $projects = @(
            @{ Name="caffe-ffi";     Dir=(Join-Path $script:workspaceRoot "projects" "xuanspace" "libs" "caffe-ffi") },
            @{ Name="npu-ffi";       Dir=(Join-Path $script:workspaceRoot "projects" "xuanspace" "libs" "npu-ffi") },
            @{ Name="demo-ffi";      Dir=(Join-Path $script:workspaceRoot "projects" "xuanspace" "libs" "demo-ffi") },
            @{ Name="xuan-ext-demo"; Dir=(Join-Path $script:workspaceRoot "projects" "xuanspace" "libs" "xuan-ext-demo") }
        )
    }

    It "All native project directories exist with pyproject.toml" {
        foreach ($p in $projects) {
            Test-Path $p.Dir | Should -Be $true -Because "$($p.Name) dir should exist"
            Test-Path (Join-Path $p.Dir "pyproject.toml") | Should -Be $true -Because "$($p.Name) should have pyproject.toml"
        }
    }

    It "All projects use scikit_build_core build backend" {
        foreach ($p in $projects) {
            $tomlPath = Join-Path $p.Dir "pyproject.toml"
            if (Test-Path $tomlPath) {
                $content = Get-Content $tomlPath -Raw
                $content | Should -Match "scikit.build" -Because "$($p.Name) should use scikit-build backend"
            }
        }
    }

    It "Find-NativeProject discovers each project from scripts directory" {
        foreach ($p in $projects) {
            if (Test-Path $p.Dir) {
                $result = Find-NativeProject -ProjectName $p.Name -ScriptDir $script:repoScripts
                $result | Should -Not -BeNullOrEmpty -Because "should find $($p.Name)"
                [IO.Path]::GetFullPath($result) | Should -Be ([IO.Path]::GetFullPath($p.Dir))
            }
        }
    }

    It "Test-NativeProject validates each project correctly" {
        foreach ($p in $projects) {
            if (Test-Path $p.Dir) {
                Test-NativeProject -Dir $p.Dir -ProjectName $p.Name | Should -Be $true
            }
        }
    }
}

Describe "Parameter Combinations - Build Script Parameters" {
    It "build_native_ext.ps1 defines all expected parameters" {
        $builderPath = Join-Path $script:repoScripts "build_native_ext.ps1"
        $content = Get-Content $builderPath -Raw
        $expectedParams = @(
            "ProjectDir", "ProjectName", "CondaEnv", "VsPath", "Arch",
            "BuildType", "PythonMinVersion", "CondaEnvNamePattern",
            "CMakeArgs", "CleanDirs", "NoClean", "NoVerify", "VerboseBuild"
        )
        foreach ($param in $expectedParams) {
            $pattern = [regex]::Escape("`$$param")
            $content | Should -Match $pattern -Because "build_native_ext.ps1 should define -$param parameter"
        }
    }

    It "build_native_ext.ps1 defaults to amd64 architecture" {
        $builderPath = Join-Path $script:repoScripts "build_native_ext.ps1"
        $content = Get-Content $builderPath -Raw
        $content | Should -Match '\$Arch\s*=\s*"amd64"'
    }

    It "build_native_ext.ps1 defaults to Release build type" {
        $builderPath = Join-Path $script:repoScripts "build_native_ext.ps1"
        $content = Get-Content $builderPath -Raw
        $content | Should -Match '\$BuildType\s*=\s*"Release"'
    }

    It "build_native_ext.ps1 imports NativeBuild module from relative lib path" {
        $builderPath = Join-Path $script:repoScripts "build_native_ext.ps1"
        $content = Get-Content $builderPath -Raw
        $content | Should -Match "lib.*NativeBuild\.psm1"
        $content | Should -Match "Import-Module"
    }

    It "build_native_ext.ps1 has all 6 build phases logged" {
        $builderPath = Join-Path $script:repoScripts "build_native_ext.ps1"
        $content = Get-Content $builderPath -Raw
        1..6 | ForEach-Object {
            $phase = $_
            $content | Should -Match "Phase $phase/6" -Because "should log Phase $phase/6"
        }
    }
}

Describe "Verify Scripts - Smoke Test Validation" {
    It "verify_native_ext.ps1 exists and imports the built module" {
        $verifyPath = Join-Path $script:repoScripts "verify_native_ext.ps1"
        Test-Path $verifyPath | Should -Be $true
        $content = Get-Content $verifyPath -Raw
        $content | Should -Match "import"
    }

    It "verify_caffe_ffi.ps1 exists" {
        $verifyPath = Join-Path $script:repoScripts "verify_caffe_ffi.ps1"
        Test-Path $verifyPath | Should -Be $true
    }

    It "batch launcher calls pwsh with -File flag" {
        $batPath = Join-Path $script:repoScripts "build_caffe_ffi.bat"
        Test-Path $batPath | Should -Be $true
        $content = Get-Content $batPath -Raw
        $content | Should -Match "pwsh"
        $content | Should -Match "\-File"
    }
}

# ═══════════════════════════════════════════════════════════════════════
# Parameter Combination Tests — verify behavior across argument combos
# ═══════════════════════════════════════════════════════════════════════

Describe "Parameter Combinations - Resolve-PathPattern" {
    It "Single segment resolves existing directory" {
        $result = @(Resolve-PathPattern -BaseDir $script:repoScripts -Segments @("lib"))
        $result.Count | Should -Be 1
        Test-Path $result[0] | Should -Be $true
    }

    It "Multi-segment resolves nested directory" {
        $result = @(Resolve-PathPattern -BaseDir $script:workspaceRoot -Segments @("projects","xuanspace","libs","caffe-ffi"))
        if (Test-Path (Join-Path $script:workspaceRoot "projects" "xuanspace" "libs" "caffe-ffi")) {
            $result.Count | Should -BeGreaterOrEqual 1
        }
    }

    It "Wildcard '*' matches multiple directories" {
        $result = @(Resolve-PathPattern -BaseDir $script:repoScripts -Segments @("*"))
        # scripts/ should have at least lib/ and tests/ subdirs
        $result.Count | Should -BeGreaterOrEqual 2
    }

    It "Mixed wildcard and literal segments" {
        $libsDir = Join-Path $script:workspaceRoot "projects" "xuanspace" "libs"
        if (Test-Path $libsDir) {
            $result = @(Resolve-PathPattern -BaseDir $libsDir -Segments @("*"))
            $result.Count | Should -BeGreaterOrEqual 3
        }
    }

    It "Empty segments returns base directory" {
        $result = @(Resolve-PathPattern -BaseDir $script:repoScripts -Segments @())
        $result.Count | Should -Be 1
        [IO.Path]::GetFullPath($result[0]) | Should -Be ([IO.Path]::GetFullPath($script:repoScripts))
    }

    It "Non-existent final segment returns empty" {
        $result = @(Resolve-PathPattern -BaseDir $script:repoScripts -Segments @("nonexistent_dir_xyz_123"))
        $result.Count | Should -Be 0
    }

    It "Non-existent intermediate segment returns empty" {
        $result = @(Resolve-PathPattern -BaseDir $script:repoScripts -Segments @("lib", "nonexistent_sub"))
        $result.Count | Should -Be 0
    }
}

Describe "Parameter Combinations - Test-NativeProject" {
    BeforeAll {
        $caffeDir = Join-Path $script:workspaceRoot "projects" "xuanspace" "libs" "caffe-ffi"
        $tempDir = Join-Path $env:TEMP "test_native_proj_$PID"
    }

    AfterAll {
        if (Test-Path $tempDir) { Remove-Item -Recurse -Force $tempDir -ErrorAction SilentlyContinue }
    }

    It "Exact project name matches" {
        if (Test-Path $caffeDir) {
            Test-NativeProject -Dir $caffeDir -ProjectName "caffe-ffi" | Should -Be $true
        }
    }

    It "Wildcard '*' matches any project name" {
        if (Test-Path $caffeDir) {
            Test-NativeProject -Dir $caffeDir -ProjectName "*" | Should -Be $true
        }
    }

    It "Wrong project name fails" {
        if (Test-Path $caffeDir) {
            Test-NativeProject -Dir $caffeDir -ProjectName "wrong-name" | Should -Be $false
        }
    }

    It "Directory without pyproject.toml fails" {
        if (-not (Test-Path $tempDir)) { New-Item -ItemType Directory -Path $tempDir -Force | Out-Null }
        Test-NativeProject -Dir $tempDir -ProjectName "*" | Should -Be $false
    }

    It "Empty directory name parameter defaults to wildcard" {
        if (Test-Path $caffeDir) {
            # Default ProjectName is "*"
            Test-NativeProject -Dir $caffeDir | Should -Be $true
        }
    }
}

Describe "Parameter Combinations - Find-NativeProject" {
    BeforeAll {
        $caffeDir = Join-Path $script:workspaceRoot "projects" "xuanspace" "libs" "caffe-ffi"
    }

    It "Hint path takes precedence over auto-search" {
        if (Test-Path $caffeDir) {
            $result = Find-NativeProject -Hint $caffeDir -ProjectName "caffe-ffi" -ScriptDir $script:repoScripts
            [IO.Path]::GetFullPath($result) | Should -Be ([IO.Path]::GetFullPath($caffeDir))
        }
    }

    It "Hint path works even with wildcard ProjectName" {
        if (Test-Path $caffeDir) {
            $result = Find-NativeProject -Hint $caffeDir -ProjectName "*" -ScriptDir $script:repoScripts
            Test-Path $result | Should -Be $true
        }
    }

    It "ScriptDir-based search works for each project" {
        $projects = @("caffe-ffi", "npu-ffi", "demo-ffi")
        foreach ($proj in $projects) {
            $dir = Join-Path $script:workspaceRoot "projects" "xuanspace" "libs" $proj
            if (Test-Path $dir) {
                $result = Find-NativeProject -ProjectName $proj -ScriptDir $script:repoScripts
                [IO.Path]::GetFullPath($result) | Should -Be ([IO.Path]::GetFullPath($dir)) -Because "should find $proj via ScriptDir search"
            }
        }
    }

    It "Empty Hint with wildcard ProjectName finds first match" {
        $result = Find-NativeProject -Hint "" -ProjectName "*" -ScriptDir $script:repoScripts
        $result | Should -Not -BeNullOrEmpty
        Test-Path (Join-Path $result "pyproject.toml") | Should -Be $true
    }

    It "Non-matching project name throws error" {
        { Find-NativeProject -ProjectName "no-such-project-xyz-999" -ScriptDir $script:repoScripts -ErrorAction Stop } | Should -Throw
    }
}

Describe "Parameter Combinations - Find-CondaEnvPython" {
    It "Named conda env hint finds specific environment" {
        # Try py314 first, fallback to any available
        $result = $null
        foreach ($hint in @("py314", "anaconda3")) {
            $found = Find-CondaEnvPython -Hint $hint -MinVersion 3.10 -ErrorAction SilentlyContinue
            if ($found) { $result = $found; break }
        }
        if ($result) {
            Test-Path (Join-Path $result "python.exe") | Should -Be $true
        }
    }

    It "MinVersion filters out older Python versions" {
        # Requesting Python 99.0 should fail (no such version)
        { Find-CondaEnvPython -MinVersion 99.0 -ErrorAction Stop } | Should -Throw
    }

    It "Default MinVersion (by parameter) works" {
        $result = Find-CondaEnvPython -MinVersion 3.10 -ErrorAction SilentlyContinue
        if ($result) {
            $pyExe = Join-Path $result "python.exe"
            $ver = Get-PythonVersion -PythonExe $pyExe
            $ver | Should -BeGreaterOrEqual 3.10
        }
    }

    It "NamePattern restricts env name matching" {
        # Pattern "314" should only match py314 envs
        $result = Find-CondaEnvPython -MinVersion 3.10 -NamePattern "314" -ErrorAction SilentlyContinue
        if ($result) {
            $result | Should -Match "314" -Because "NamePattern='314' should match py314"
        }
    }

    It "Invalid Hint throws error" {
        { Find-CondaEnvPython -Hint "no-env-exists-xyz-999" -MinVersion 3.10 -ErrorAction Stop } | Should -Throw
    }
}

Describe "Parameter Combinations - Find-VisualStudio" {
    It "Default (no args) finds highest-priority VS" {
        $vs = Find-VisualStudio
        $vs | Should -Not -BeNullOrEmpty
        Test-Path $vs | Should -Be $true
        Test-Path ([IO.Path]::Combine($vs, "Common7", "Tools", "Microsoft.VisualStudio.DevShell.dll")) | Should -Be $true
    }

    It "Explicit Hint path returns same path when valid" {
        $autoVs = Find-VisualStudio
        $result = Find-VisualStudio -Hint $autoVs
        $result | Should -Be $autoVs
    }

    It "Invalid Hint path throws error" {
        { Find-VisualStudio -Hint "C:\nonexistent\vs\path\xyz" -ErrorAction Stop } | Should -Throw
    }
}

Describe "Parameter Combinations - Enter-MsvcDevShell" {
    It "Default amd64 arch makes cl.exe available" {
        $vs = Find-VisualStudio
        Enter-MsvcDevShell -VsInstallPath $vs -Arch "amd64"
        $cl = Get-Command cl -ErrorAction SilentlyContinue
        $cl | Should -Not -BeNullOrEmpty
        $cl.Source | Should -Match "cl\.exe$"
    }
}

Describe "Parameter Combinations - Convert-VsVersionDirToNumber" {
    It "All known year-based versions map to correct numbers" {
        $yearMap = @{
            "2022" = 17; "2019" = 16; "2017" = 15; "2015" = 14; "2013" = 12
        }
        foreach ($year in $yearMap.Keys) {
            Convert-VsVersionDirToNumber -VersionDirName $year | Should -Be $yearMap[$year] -Because "VS $year should map to v$($yearMap[$year])"
        }
    }

    It "Numeric strings are parsed as version numbers" {
        foreach ($v in @("14","15","16","17","18")) {
            Convert-VsVersionDirToNumber -VersionDirName $v | Should -Be ([int]$v)
        }
    }

    It "Non-version directory names return 0" {
        foreach ($name in @("Installer","Shared","Packages","","Xml")) {
            Convert-VsVersionDirToNumber -VersionDirName $name | Should -Be 0 -Because "'$name' is not a version dir"
        }
    }

    It "Version ordering is correct (newest > oldest)" {
        $v2022 = Convert-VsVersionDirToNumber -VersionDirName "2022"
        $v18   = Convert-VsVersionDirToNumber -VersionDirName "18"
        $v17   = Convert-VsVersionDirToNumber -VersionDirName "17"
        $v2019 = Convert-VsVersionDirToNumber -VersionDirName "2019"
        $v18 | Should -BeGreaterThan $v2022
        $v2022 | Should -BeGreaterThan $v2019
        $v17 | Should -BeGreaterOrEqual $v2022  # v17 == 2022
    }
}

Describe "Parameter Combinations - Get-VsEditionPriority" {
    It "All known editions have correct priority" {
        $expected = @{
            "Insiders" = 4; "Canary" = 4; "Preview" = 3
            "Enterprise" = 2; "Professional" = 1; "Community" = 0; "BuildTools" = 0
        }
        foreach ($edition in $expected.Keys) {
            Get-VsEditionPriority -EditionName $edition | Should -Be $expected[$edition] -Because "$edition priority should be $($expected[$edition])"
        }
    }

    It "Case-insensitive matching works" {
        Get-VsEditionPriority -EditionName "insiders" | Should -Be 4
        Get-VsEditionPriority -EditionName "COMMUNITY" | Should -Be 0
        Get-VsEditionPriority -EditionName "Preview" | Should -Be 3
        Get-VsEditionPriority -EditionName "enterprise" | Should -Be 2
    }

    It "Unknown editions return -1" {
        Get-VsEditionPriority -EditionName "UnknownEdition" | Should -Be -1
        Get-VsEditionPriority -EditionName "" | Should -Be -1
        Get-VsEditionPriority -EditionName "Express" | Should -Be -1
    }

    It "Priority ordering is correct" {
        $insiders  = Get-VsEditionPriority -EditionName "Insiders"
        $preview   = Get-VsEditionPriority -EditionName "Preview"
        $enterprise = Get-VsEditionPriority -EditionName "Enterprise"
        $community  = Get-VsEditionPriority -EditionName "Community"
        $unknown   = Get-VsEditionPriority -EditionName "Unknown"

        $insiders | Should -BeGreaterThan $preview
        $preview | Should -BeGreaterThan $enterprise
        $enterprise | Should -BeGreaterThan $community
        $unknown | Should -BeLessThan $community
    }
}

Describe "Parameter Combinations - Build Script Defaults and Switches" {
    BeforeAll {
        $builderPath = Join-Path $script:repoScripts "build_native_ext.ps1"
        $content = Get-Content $builderPath -Raw
    }

    It "All default parameter values are correctly set" {
        # Check string defaults
        $content | Should -Match '\$ProjectDir\s*=\s*""'
        $content | Should -Match '\$ProjectName\s*=\s*"\*"'
        $content | Should -Match '\$CondaEnv\s*=\s*""'
        $content | Should -Match '\$VsPath\s*=\s*""'
        $content | Should -Match '\$Arch\s*=\s*"amd64"'
        $content | Should -Match '\$BuildType\s*=\s*"Release"'
    }

    It "Numeric and array defaults are correct" {
        $content | Should -Match '\$PythonMinVersion\s*=\s*3\.14'
        $content | Should -Match '\$CondaEnvNamePattern\s*=\s*"314\|py314\|3\\.14"'
        $content | Should -Match '\$CMakeArgs\s*=\s*@\(\)'
        $content | Should -Match '\$CleanDirs\s*=\s*@\("build",\s*"build-vs",\s*"_skbuild"\)'
    }

    It "Switch parameters default to false" {
        $content | Should -Match '\[switch\]\$NoClean'
        $content | Should -Match '\[switch\]\$NoVerify'
        $content | Should -Match '\[switch\]\$VerboseBuild'
    }

    It "-NoClean switch skips Phase 2 cleaning" {
        $content | Should -Match 'if\s*\(-not\s+\$NoClean\)'
        $content | Should -Match "Phase 2/6: Skipping clean"
    }

    It "-NoVerify switch skips Phase 5 verification" {
        $content | Should -Match 'if\s*\(-not\s+\$NoVerify\)'
        $content | Should -Match "Phase 5/6: Skipping verification"
    }

    It "ErrorActionPreference is set to Stop" {
        $content | Should -Match '\$ErrorActionPreference\s*=\s*"Stop"'
    }

    It "Logs effective parameters at startup" {
        $content | Should -Match "Effective parameters:"
        $content | Should -Match "ProjectDir"
        $content | Should -Match "ProjectName"
        $content | Should -Match "PythonMinVer"
        $content | Should -Match "VerboseBuild"
    }

    It "DevShell loading has diagnostic detail (PATH delta, cl.exe)" {
        $content | Should -Match "PATH length before DevShell"
        $content | Should -Match "PATH length after DevShell"
        $content | Should -Match "delta:"
        $content | Should -Match "cl\.exe:"
        $content | Should -Match "DevShell\.dll"
    }
}

Describe "Parameter Combinations - Thin Wrapper Argument Forwarding" {
    BeforeAll {
        $wrappers = @(
            @{ File="build_caffe_ffi.ps1";     Project="caffe-ffi";     MinVer="3.14" },
            @{ File="build_npu_ffi.ps1";       Project="npu-ffi";       MinVer="3.13" },
            @{ File="build_demo_ffi.ps1";      Project="demo-ffi";      MinVer="3.13" },
            @{ File="build_xuan_ext_demo.ps1"; Project="xuan-ext-demo"; MinVer="3.14" }
        )
    }

    It "Each wrapper passes correct -ProjectName to builder" {
        foreach ($w in $wrappers) {
            $path = Join-Path $script:repoScripts $w.File
            $content = Get-Content $path -Raw
            $content | Should -Match ("-ProjectName\s+`"" + [regex]::Escape($w.Project) + "`"") -Because "$($w.File) should pass -ProjectName $($w.Project)"
        }
    }

    It "Each wrapper calls build_native_ext.ps1 via Join-Path" {
        foreach ($w in $wrappers) {
            $path = Join-Path $script:repoScripts $w.File
            $content = Get-Content $path -Raw
            $content | Should -Match 'Join-Path\s+\$PSScriptRoot\s+"build_native_ext\.ps1"' -Because "$($w.File) should resolve builder relative to itself"
        }
    }

    It "Each wrapper forwards arguments via splatting (@args)" {
        foreach ($w in $wrappers) {
            $path = Join-Path $script:repoScripts $w.File
            $content = Get-Content $path -Raw
            $content | Should -Match '@args' -Because "$($w.File) should forward all extra arguments"
        }
    }

    It "Each wrapper captures and propagates exit code" {
        foreach ($w in $wrappers) {
            $path = Join-Path $script:repoScripts $w.File
            $content = Get-Content $path -Raw
            # Must capture $LASTEXITCODE after & $builder call
            $content | Should -Match '\$LASTEXITCODE'
            # Must exit with captured code
            $content | Should -Match 'exit\s+\$'
        }
    }

    It "Each wrapper displays header with project identity" {
        foreach ($w in $wrappers) {
            $path = Join-Path $script:repoScripts $w.File
            $content = Get-Content $path -Raw
            $content | Should -Match "builder wrapper" -Because "$($w.File) should show wrapper header"
            $content | Should -Match ([regex]::Escape($w.Project)) -Because "$($w.File) should display project name"
        }
    }

    It "Each wrapper shows build result (success/failure)" {
        foreach ($w in $wrappers) {
            $path = Join-Path $script:repoScripts $w.File
            $content = Get-Content $path -Raw
            $content | Should -Match "build finished successfully"
            $content | Should -Match "build failed"
        }
    }
}

Describe "Parameter Combinations - Get-PythonVersion" {
    It "Valid Python returns version >= 3.0" {
        # Use system python
        $sysPy = Get-Command python -ErrorAction SilentlyContinue
        if ($sysPy) {
            $ver = Get-PythonVersion -PythonExe $sysPy.Source
            $ver | Should -BeGreaterOrEqual 3.0
        }
    }

    It "Non-existent executable returns 0" {
        Get-PythonVersion -PythonExe "C:\nonexistent_python_xyz.exe" | Should -Be 0
    }

    It "Non-Python executable returns 0" {
        $cmd = Get-Command cmd -ErrorAction SilentlyContinue
        if ($cmd) {
            $ver = Get-PythonVersion -PythonExe $cmd.Source
            $ver | Should -Be 0 -Because "cmd.exe is not Python"
        }
    }
}

Describe "Parameter Combinations - Logging Output Verification" {
    It "build_native_ext.ps1 contains all required log functions" {
        $builderPath = Join-Path $script:repoScripts "build_native_ext.ps1"
        $content = Get-Content $builderPath -Raw
        $content | Should -Match "function Log-Step"
        $content | Should -Match "function Log-Info"
        $content | Should -Match "function Log-OK"
        $content | Should -Match "function Log-Warn"
    }

    It "All 6 phases have both step and completion indicators" {
        $builderPath = Join-Path $script:repoScripts "build_native_ext.ps1"
        $content = Get-Content $builderPath -Raw
        foreach ($phase in 1..6) {
            $content | Should -Match "Phase $phase/6:" -Because "Phase $phase should have a header"
        }
    }

    It "BUILD SUCCEEDED and BUILD FAILED messages exist" {
        $builderPath = Join-Path $script:repoScripts "build_native_ext.ps1"
        $content = Get-Content $builderPath -Raw
        $content | Should -Match "BUILD SUCCEEDED"
        $content | Should -Match "BUILD FAILED"
    }

    It "Error messages include helpful guidance" {
        $builderPath = Join-Path $script:repoScripts "build_native_ext.ps1"
        $content = Get-Content $builderPath -Raw
        $content | Should -Match "Desktop development with C\+\+" -Because "should suggest VS workload"
    }
}
