#Requires -Modules Pester
# test_build_scripts.Tests.ps1 - Unit tests for NativeBuild.psm1 and build scripts
# Run with: pwsh -NoProfile -Command "Invoke-Pester -Path .agents/scripts/tests/test_build_scripts.Tests.ps1 -Output Detailed"

BeforeAll {
    # Test file is at .agents/scripts/tests/ → scriptsDir = .agents/scripts/
    $scriptsDir = Split-Path -Parent $PSCommandPath
    $modulePath = [IO.Path]::GetFullPath((Join-Path $scriptsDir ".." "lib" "NativeBuild.psm1"))
    Import-Module $modulePath -Force
    $script:repoScripts = [IO.Path]::GetFullPath((Join-Path $scriptsDir ".."))
    $script:workspaceRoot = [IO.Path]::GetFullPath((Join-Path $scriptsDir ".." ".."))
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
            "Find-CondaEnvPython", "Find-VisualStudio", "Enter-MsvcDevShell"
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
