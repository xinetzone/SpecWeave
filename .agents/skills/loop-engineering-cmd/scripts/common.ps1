function Parse-Arguments {
    param(
        [string[]]$Arguments,
        [hashtable]$Defaults = @{}
    )
    
    $result = @{}
    foreach ($key in $Defaults.Keys) {
        $result[$key] = $Defaults[$key]
    }
    
    $i = 0
    while ($i -lt $Arguments.Count) {
        $arg = $Arguments[$i]
        
        if ($arg -match "^--([a-zA-Z0-9_-]+)=(.+)$") {
            $key = $Matches[1]
            $value = $Matches[2]
            $result[$key] = Convert-Value $value
            $i++
        }
        elseif ($arg -match "^--([a-zA-Z0-9_-]+)$" -or $arg -match "^-([a-zA-Z0-9_-]+)$") {
            $key = $Matches[1]
            if ($i + 1 -lt $Arguments.Count -and -not ($Arguments[$i + 1] -match "^-")) {
                $result[$key] = Convert-Value $Arguments[$i + 1]
                $i += 2
            } else {
                $result[$key] = $true
                $i++
            }
        }
        else {
            $i++
        }
    }
    
    return $result
}

function Convert-Value {
    param([string]$Value)
    
    if ($Value -eq "`$true" -or $Value -eq "true" -or $Value -eq "True" -or $Value -eq "1") {
        return $true
    }
    if ($Value -eq "`$false" -or $Value -eq "false" -or $Value -eq "False" -or $Value -eq "0") {
        return $false
    }
    if ($Value -match "^\d+$") {
        return [int]$Value
    }
    return $Value
}

function Get-Format {
    param([hashtable]$ParsedArgs)
    $format = "markdown"
    if ($ParsedArgs.ContainsKey("format")) {
        $format = $ParsedArgs["format"]
    }
    if ($format -ne "markdown" -and $format -ne "json") {
        $format = "markdown"
    }
    return $format
}

function Get-Config {
    param([hashtable]$ParsedArgs)
    if ($ParsedArgs.ContainsKey("config")) {
        return $ParsedArgs["config"]
    }
    return $null
}

function Load-ConfigFile {
    param([string]$ConfigPath)
    
    if (-not $ConfigPath) { return $null }
    if (-not (Test-Path $ConfigPath)) {
        Write-Host "错误: 配置文件不存在: $ConfigPath" -ForegroundColor Red
        exit 1
    }
    
    try {
        return Get-Content $ConfigPath -Raw -Encoding UTF8 | ConvertFrom-Json
    } catch {
        Write-Host "错误: 无法解析配置文件: $_" -ForegroundColor Red
        exit 1
    }
}
