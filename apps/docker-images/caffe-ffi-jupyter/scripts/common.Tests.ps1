#requires -Modules @{ModuleName='Pester'; ModuleVersion='5.0'}
<#
.SYNOPSIS
    common.ps1 共享工具库 Pester 测试套件
.DESCRIPTION
    覆盖 Convert-WindowsPathToWsl、Test-WslAvailable、Get-WslDefaultDistro、
    Docker 检查函数、Python 版本检查、脚本目录解析、文件哈希等核心功能。
.NOTES
    运行方式：
      pwsh -NoProfile -Command "Invoke-Pester -Path '<path>/common.Tests.ps1' -Output Detailed"
#>

BeforeAll {
    $script:CommonPs1 = Join-Path $PSScriptRoot 'lib/common.ps1'
    . $script:CommonPs1

    # 运行时解析 Python 路径（用于 It 块内部）
    $pyCmd = Get-Command python -ErrorAction SilentlyContinue
    $script:HasPython = [bool]$pyCmd
    if ($script:HasPython) {
        $script:PyExe = if ($pyCmd.Source) { $pyCmd.Source } else { $pyCmd.Path }
    }

    # WSL 运行时检测
    $script:HasWslExe = [bool](Get-Command wsl.exe -ErrorAction SilentlyContinue)
    $script:HasWsl = if ($script:HasWslExe) { Test-WslAvailable } else { $false }
}

Describe 'common.ps1 加载验证' {
    It '所有核心函数应已定义' {
        $expected = @(
            'Test-WslAvailable',
            'Get-WslDefaultDistro',
            'Convert-WindowsPathToWsl',
            'Test-DockerAvailable',
            'Test-DockerContainerRunning',
            'Test-DockerImageExists',
            'Test-PythonVersion',
            'Get-PythonVersion',
            'Get-ScriptDirectory',
            'Get-ProjectRoot',
            'Invoke-WslCommand',
            'Get-FileHashString'
        )
        foreach ($fn in $expected) {
            Get-Command $fn -ErrorAction SilentlyContinue | Should -Not -BeNullOrEmpty -Because "函数 $fn 应该被导出"
        }
    }

    It '日志函数应已通过自动加载可用' {
        Get-Command 'Log-Info' -ErrorAction SilentlyContinue | Should -Not -BeNullOrEmpty
        Get-Command 'Log-Ok' -ErrorAction SilentlyContinue | Should -Not -BeNullOrEmpty
        Get-Command 'Log-Warn' -ErrorAction SilentlyContinue | Should -Not -BeNullOrEmpty
        Get-Command 'Log-Error' -ErrorAction SilentlyContinue | Should -Not -BeNullOrEmpty
    }

    It '版本检查函数应已通过自动加载可用' {
        Get-Command 'Test-Pwsh7Version' -ErrorAction SilentlyContinue | Should -Not -BeNullOrEmpty
    }
}

Describe 'Convert-WindowsPathToWsl' {
    Context '绝对路径转换' {
        It '应将 C:\ 盘路径转换为 /mnt/c/' {
            Convert-WindowsPathToWsl 'C:\' | Should -Be '/mnt/c/'
        }

        It '应将 D:\ 盘路径转换为 /mnt/d/' {
            Convert-WindowsPathToWsl 'D:\' | Should -Be '/mnt/d/'
        }

        It '应将多级路径正确转换' {
            Convert-WindowsPathToWsl 'C:\Windows\System32' | Should -Be '/mnt/c/Windows/System32'
        }

        It '应转换深层路径' {
            Convert-WindowsPathToWsl 'D:\spaces\SpecWeave\apps\caffe-ffi-jupyter\scripts' |
                Should -Be '/mnt/d/spaces/SpecWeave/apps/docker-images/caffe-ffi-jupyter/scripts'
        }

        It '应将盘符转为小写' {
            $result = Convert-WindowsPathToWsl 'C:\Users'
            $driveChar = $result.Substring(5, 1)
            $driveChar | Should -BeExactly 'c'
        }
    }

    Context '反斜杠处理' {
        It '应将所有反斜杠替换为正斜杠' {
            $result = Convert-WindowsPathToWsl 'C:\a\b\c\d'
            $result | Should -Not -Match '\\'
            $result | Should -Be '/mnt/c/a/b/c/d'
        }
    }

    Context '相对路径解析' {
        It '应能解析相对路径（使用当前工作目录）' {
            $result = Convert-WindowsPathToWsl '.'
            $result | Should -Match '^/mnt/[a-z]/'
            $result | Should -Not -Match '\\'
        }
    }
}

Describe 'Get-ScriptDirectory' {
    It '应返回非空路径' {
        $dir = Get-ScriptDirectory
        $dir | Should -Not -BeNullOrEmpty
        Test-Path $dir -PathType Container | Should -BeTrue
    }

    It '返回路径应为绝对路径' {
        $dir = Get-ScriptDirectory
        [System.IO.Path]::IsPathRooted($dir) | Should -BeTrue
    }
}

Describe 'Get-ProjectRoot' {
    It '应返回项目根目录（scripts/ 的上级）' {
        $root = Get-ProjectRoot
        $root | Should -Not -BeNullOrEmpty
        Test-Path $root -PathType Container | Should -BeTrue
    }

    It '项目根目录应包含 deploy.ps1' {
        $root = Get-ProjectRoot
        $deployPath = Join-Path $root 'scripts/deploy.ps1'
        Test-Path $deployPath -PathType Leaf | Should -BeTrue
    }

    It '项目根目录应包含 scripts/lib/ 子目录' {
        $root = Get-ProjectRoot
        $libDir = Join-Path $root 'scripts/lib'
        Test-Path $libDir -PathType Container | Should -BeTrue
    }
}

Describe 'Get-FileHashString' {
    BeforeAll {
        $script:TempFile = Join-Path $TestDrive 'hash-test.txt'
        'Hello, World!' | Set-Content -Path $script:TempFile -NoNewline -Encoding utf8
    }

    It '应返回非空哈希字符串' {
        $hash = Get-FileHashString -Path $script:TempFile
        $hash | Should -Not -BeNullOrEmpty
        $hash.Length | Should -BeGreaterThan 0
    }

    It 'SHA256 哈希应为64个十六进制字符' {
        $hash = Get-FileHashString -Path $script:TempFile -Algorithm SHA256
        $hash.Length | Should -Be 64
        $hash | Should -Match '^[0-9a-f]{64}$'
    }

    It 'MD5 哈希应为32个十六进制字符' {
        $hash = Get-FileHashString -Path $script:TempFile -Algorithm MD5
        $hash.Length | Should -Be 32
        $hash | Should -Match '^[0-9a-f]{32}$'
    }

    It 'SHA1 哈希应为40个十六进制字符' {
        $hash = Get-FileHashString -Path $script:TempFile -Algorithm SHA1
        $hash.Length | Should -Be 40
        $hash | Should -Match '^[0-9a-f]{40}$'
    }

    It '相同文件应产生相同哈希（幂等性）' {
        $h1 = Get-FileHashString -Path $script:TempFile
        $h2 = Get-FileHashString -Path $script:TempFile
        $h1 | Should -Be $h2
    }

    It '不同内容应产生不同哈希' {
        $otherFile = Join-Path $TestDrive 'hash-test2.txt'
        'Different content!' | Set-Content -Path $otherFile -NoNewline -Encoding utf8
        $h1 = Get-FileHashString -Path $script:TempFile
        $h2 = Get-FileHashString -Path $otherFile
        $h1 | Should -Not -Be $h2
    }

    It '不存在的文件应返回 $null' {
        $hash = Get-FileHashString -Path (Join-Path $TestDrive 'nonexistent.xxx')
        $hash | Should -BeNullOrEmpty
    }
}

Describe 'Test-PythonVersion' -Skip:(-not (Get-Command python -ErrorAction SilentlyContinue)) {
    It '系统 Python 应满足最低版本要求 3.0' {
        Test-PythonVersion -PythonPath $script:PyExe -MinVersion '3.0' | Should -BeTrue
    }

    It '极高版本要求应返回 false' {
        Test-PythonVersion -PythonPath $script:PyExe -MinVersion '99.99' | Should -BeFalse
    }

    It '不存在的 Python 路径应返回 false' {
        Test-PythonVersion -PythonPath 'C:\nonexistent\python.exe' -MinVersion '3.0' | Should -BeFalse
    }
}

Describe 'Get-PythonVersion' -Skip:(-not (Get-Command python -ErrorAction SilentlyContinue)) {
    It '应返回有效的版本对象' {
        $ver = Get-PythonVersion -PythonPath $script:PyExe
        $ver | Should -Not -BeNullOrEmpty
        $ver | Should -BeOfType [version]
    }

    It '版本号主版本应不小于3' {
        $ver = Get-PythonVersion -PythonPath $script:PyExe
        $ver.Major | Should -BeGreaterOrEqual 3
    }

    It '不存在的 Python 路径应返回 $null' {
        $ver = Get-PythonVersion -PythonPath 'C:\nonexistent\python.exe'
        $ver | Should -BeNullOrEmpty
    }
}

Describe 'Test-WslAvailable' {
    It '应返回布尔值' {
        $result = Test-WslAvailable
        $result | Should -BeOfType [bool]
    }

    It '在 WSL 内运行时应返回 false（不递归调用 wsl.exe）' {
        if ($env:WSL_DISTRO_NAME) {
            Test-WslAvailable | Should -BeFalse
        }
    }
}

Describe 'Get-WslDefaultDistro' {
    It '返回值应为 null 或非空字符串' {
        $result = Get-WslDefaultDistro
        if ($null -ne $result) {
            $result | Should -BeOfType [string]
            $result | Should -Not -BeNullOrEmpty
        }
    }
}

Describe 'Test-DockerAvailable' {
    It '应返回布尔值' {
        $result = Test-DockerAvailable
        $result | Should -BeOfType [bool]
    }

    It '无 Docker 时应返回 false（不抛异常）' {
        { Test-DockerAvailable } | Should -Not -Throw
    }
}

Describe 'Test-DockerContainerRunning' {
    It '检查不存在的容器应返回 false' {
        Test-DockerContainerRunning -ContainerName '__nonexistent_container_test_xyz__' | Should -BeFalse
    }
}

Describe 'Test-DockerImageExists' {
    It '检查不存在的镜像应返回 false' {
        Test-DockerImageExists -ImageName '__nonexistent_image_test_xyz__:latest' | Should -BeFalse
    }
}

Describe 'Invoke-WslCommand' -Skip:(-not (Get-Command wsl.exe -ErrorAction SilentlyContinue)) {
    It '在 WSL 可用时能执行简单命令并返回退出码 0' {
        if ($script:HasWsl) {
            $result = Invoke-WslCommand -Command 'echo hello-from-wsl' -PassThru
            $result | Should -Be 0
        } else {
            Set-ItResult -Skipped -Because 'wsl.exe 存在但无可用 WSL 发行版'
        }
    }
}

Describe 'Invoke-WslCommand (no WSL)' -Skip:([bool](Get-Command wsl.exe -ErrorAction SilentlyContinue)) {
    It '在 WSL 不可用时不应抛出终止错误' {
        { Invoke-WslCommand -Command 'echo test' -PassThru -ErrorAction SilentlyContinue } | Should -Not -Throw
    }
}
