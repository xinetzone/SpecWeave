# 图片物理归档到 dist/_static + tkinterx 路径统一 + 三束图片对账
$ErrorActionPreference = 'Stop'
$raw  = 'd:\spaces\SpecWeave\.trae\specs\tkinter-okf-wiki\raw'
$dist = 'd:\spaces\SpecWeave\.trae\specs\tkinter-okf-wiki\dist'
$map  = Get-Content (Join-Path $raw 'image-map.json') -Raw | ConvertFrom-Json
$mapHashes = @{}
foreach ($p in $map.PSObject.Properties) { $mapHashes[$p.Name] = $p.Value }

function Get-LocalName([string]$url) {
    if ($mapHashes.ContainsKey($url)) { return $mapHashes[$url] }
    $base = $url -replace '\?.*$',''
    if ($mapHashes.ContainsKey($base)) { return $mapHashes[$base] }
    return $null
}

$bundles = @{
    'tkinter-gui-design'  = 'tkinter-gui-design-chapters.json'
    'tkinter-handbook'    = 'tkinter-handbook-chapters.json'
    'tkinterx-handbook'   = 'tkinterx-handbook-chapters.json'
}

foreach ($b in $bundles.Keys) {
    $stageDir = Join-Path $dist "_static\bundles\jishu\gui\$b\images"
    New-Item -ItemType Directory -Force -Path $stageDir | Out-Null
    $chapters = Get-Content (Join-Path $raw $bundles[$b]) -Raw | ConvertFrom-Json
    # chapters 为数组（避免数组成员枚举陷阱：$arr.prop 会返回 null 数组）
    $items = if ($chapters -is [System.Array]) { $chapters } elseif ($chapters.chapters) { $chapters.chapters } else { $chapters.articles }
    $copied = 0; $missing = @()
    foreach ($ch in $items) {
        $slug = $ch.slug
        if (-not $slug) { $url = $ch.url; if ($url) { $slug = ($url -split '/')[-1] } }
        $mdFile = Get-ChildItem (Join-Path $raw 'md') -Filter "*-$slug.md" -ErrorAction SilentlyContinue | Select-Object -First 1
        if (-not $mdFile) { $missing += "MD NOT FOUND: $slug"; continue }
        $artSlug = ($mdFile.Name -replace '^\d+-','') -replace '\.md$',''
        $md = Get-Content $mdFile.FullName -Raw
        $ms = [regex]::Matches($md, '!\[[^\]]*\]\((https?://[^)]+)\)')
        foreach ($m in $ms) {
            $u = $m.Groups[1].Value
            $local = Get-LocalName $u
            if (-not $local) { $missing += "NO MAP: $u"; continue }
            $src = Join-Path $raw "images\$local"
            if (-not (Test-Path $src)) { $missing += "SRC MISSING: $local"; continue }
            $dstName = "$artSlug-$local"
            Copy-Item $src (Join-Path $stageDir $dstName) -Force
            $copied++
        }
    }
    Write-Host "[$b] staged=$copied unique=$((Get-ChildItem $stageDir -File).Count) missing=$($missing.Count)"
    $missing | Select-Object -Unique | ForEach-Object { Write-Host "  $_" }
}

# ---- tkinterx 路径统一：../images/ -> ../../../../../_static/...（concepts/examples 层）----
$tx = Join-Path $dist 'bundles\jishu\gui\tkinterx-handbook'
$fixed = 0
foreach ($sub in @('concepts','examples')) {
    Get-ChildItem (Join-Path $tx $sub) -Filter *.md | ForEach-Object {
        $t = Get-Content $_.FullName -Raw
        $n = $t -replace [regex]::Escape('](../images/'), '](../../../../../_static/bundles/jishu/gui/tkinterx-handbook/images/'
        if ($n -ne $t) { [System.IO.File]::WriteAllText($_.FullName, $n, [System.Text.UTF8Encoding]::new($false)); $fixed++ }
    }
}
# 根层 index.md 若引用图片用 4 级前缀
Get-ChildItem $tx -Filter *.md | ForEach-Object {
    $t = Get-Content $_.FullName -Raw
    $n = $t -replace [regex]::Escape('](images/'), '](../../../../_static/bundles/jishu/gui/tkinterx-handbook/images/'
    if ($n -ne $t) { [System.IO.File]::WriteAllText($_.FullName, $n, [System.Text.UTF8Encoding]::new($false)); $fixed++ }
}
Write-Host "[tkinterx] path-fixed files: $fixed"

# ---- 全量对账：每个 bundle 文档引用的图片是否都已物理归档 ----
foreach ($b in $bundles.Keys) {
    $bDir = Join-Path $dist "bundles\jishu\gui\$b"
    $stageDir = Join-Path $dist "_static\bundles\jishu\gui\$b\images"
    $staged = @{}; Get-ChildItem $stageDir -File | ForEach-Object { $staged[$_.Name] = $true }
    $refs = @(); $bad = @()
    Get-ChildItem $bDir -Recurse -Filter *.md | ForEach-Object {
        $t = Get-Content $_.FullName -Raw
        foreach ($m in [regex]::Matches($t, '!\[[^\]]*\]\(([^)]+)\)')) {
            $p = $m.Groups[1].Value
            if ($p -match '^https?://') { $bad += "REMOTE: $p"; continue }
            if ($p -match '^file:///') { $bad += "FILEABS: $p"; continue }
            $refs += $p
            if ($p -match '_static/bundles/jishu/gui/[^/]+/images/(.+)$') {
                $fn = $Matches[1]
                if (-not $staged.ContainsKey($fn)) { $bad += "MISSING STAGED: $fn in $($_.Name)" }
            } else {
                $bad += "BAD PATH: $p in $($_.Name)"
            }
        }
    }
    $unreferenced = $staged.Keys | Where-Object { $f = $_; -not ($refs | Where-Object { $_ -like "*/$f" }) }
    Write-Host "[$b] refs=$($refs.Count) staged=$($staged.Count) bad=$($bad.Count) unreferenced=$(@($unreferenced).Count)"
    $bad | Select-Object -Unique | ForEach-Object { Write-Host "  BAD: $_" }
    $unreferenced | Select-Object -First 10 | ForEach-Object { Write-Host "  UNREF: $_" }
}
Write-Host 'STAGE DONE'
