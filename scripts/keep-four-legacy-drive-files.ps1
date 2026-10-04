param([switch]$Apply)
$ErrorActionPreference = 'Stop'
$sourceRoot = 'G:\Mon Drive\كتبي'
$archiveRoot = 'G:\Mon Drive\أرشيف الملفات الزائدة من كتبي'
$siteRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
$catalog = Get-Content -LiteralPath (Join-Path $siteRoot 'ai-index.json') -Raw -Encoding UTF8 | ConvertFrom-Json
$resolvedSource = (Resolve-Path -LiteralPath $sourceRoot).Path.TrimEnd('\')
$resolvedArchive = (Resolve-Path -LiteralPath $archiveRoot).Path.TrimEnd('\')
if ($resolvedSource -eq $resolvedArchive -or -not $resolvedArchive.StartsWith('G:\Mon Drive\', [StringComparison]::OrdinalIgnoreCase)) { throw 'Unsafe archive root' }
$normalizations = @(
    @{relative='shattering-the-false-mountains\en\content.docx';name='25-shattering-the-false-mountains-en.docx'},
    @{relative='shattering-the-false-mountains\en\content.pdf';name='25-shattering-the-false-mountains-en.pdf'},
    @{relative='sultan-of-insight\en\cover-ar.png';name='cover-en.png'}
)
$coverCopies = @(
    @{number=11;language='ar'},
    @{number=59;language='en'}
)
$report = [ordered]@{date='2026-10-04';source=$resolvedSource;archive=$resolvedArchive;mode=$(if($Apply){'apply'}else{'preview'});renamed=@();covers_added=@();moved=@();checks=@();preserved_image_folders=@()}
if ($Apply) {
    foreach ($row in $normalizations) {
        $source = Join-Path $resolvedSource $row.relative
        $target = Join-Path (Split-Path -LiteralPath $source) $row.name
        if (Test-Path -LiteralPath $target) { continue }
        if (-not (Test-Path -LiteralPath $source -PathType Leaf)) { throw "Missing normalization source: $source" }
        $before = Get-Item -LiteralPath $source
        $beforeLength = $before.Length
        $beforeTime = $before.LastWriteTimeUtc
        Rename-Item -LiteralPath $source -NewName $row.name
        $after = Get-Item -LiteralPath $target
        if ($beforeLength -ne $after.Length -or $beforeTime -ne $after.LastWriteTimeUtc) { throw "Changed file metadata: $target" }
        $report.renamed += @{source=$source;target=$target;bytes=$beforeLength}
    }
    foreach ($row in $coverCopies) {
        $book = $catalog.books | Where-Object {$_.book_number -eq $row.number}
        $target = Join-Path $resolvedSource "$($book.id)\$($row.language)\cover-$($row.language).png"
        if (Test-Path -LiteralPath $target) { continue }
        $source = Join-Path $siteRoot $book.($row.language).cover
        if (-not (Test-Path -LiteralPath $source -PathType Leaf)) { throw "Missing site cover: $source" }
        Copy-Item -LiteralPath $source -Destination $target
        if ((Get-FileHash -LiteralPath $source).Hash -ne (Get-FileHash -LiteralPath $target).Hash) { throw "Cover copy mismatch: $target" }
        $report.covers_added += @{source=$source;target=$target}
    }
}
$plan = @()
foreach ($book in $catalog.books | Where-Object {$_.book_number -le 69}) {
    foreach ($language in @('ar','en')) {
        $folder = Join-Path $resolvedSource "$($book.id)\$language"
        $resolvedFolder = (Resolve-Path -LiteralPath $folder).Path
        if (-not $resolvedFolder.StartsWith($resolvedSource+'\',[StringComparison]::OrdinalIgnoreCase)) { throw "Folder outside scope: $folder" }
        $keep = @("$($book.book_number)-$($book.id)-$language.docx","$($book.book_number)-$($book.id)-$language.pdf","$($book.book_number)-$($book.id)-$language.txt","cover-$language.png")
        $files = @(Get-ChildItem -LiteralPath $resolvedFolder -File -Force)
        $missing = @($keep | Where-Object {$_ -notin $files.Name})
        if ($missing.Count -gt 0) { throw "Four-file set is incomplete: $folder $($missing -join ', ')" }
        $report.preserved_image_folders += @(Get-ChildItem -LiteralPath $resolvedFolder -Directory | ForEach-Object {$_.FullName})
        foreach ($file in $files | Where-Object {$_.Name -notin $keep}) {
            $destinationFolder = Join-Path $resolvedArchive "$($book.id)\$language"
            $target = Join-Path $destinationFolder $file.Name
            if (Test-Path -LiteralPath $target) { throw "Archive target exists; no overwrite: $target" }
            $plan += [pscustomobject]@{number=$book.book_number;id=$book.id;language=$language;source=$file.FullName;target=$target;bytes=$file.Length;modified_utc=$file.LastWriteTimeUtc}
        }
    }
}
$report.planned = $plan.Count
if ($Apply) {
    $done = 0
    foreach ($entry in $plan) {
        $absoluteSource = (Resolve-Path -LiteralPath $entry.source).Path
        $absoluteTarget = [IO.Path]::GetFullPath($entry.target)
        if (-not $absoluteSource.StartsWith($resolvedSource+'\',[StringComparison]::OrdinalIgnoreCase) -or -not $absoluteTarget.StartsWith($resolvedArchive+'\',[StringComparison]::OrdinalIgnoreCase)) { throw 'Move outside approved roots' }
        $destinationFolder = Split-Path -LiteralPath $absoluteTarget
        if (-not (Test-Path -LiteralPath $destinationFolder)) { New-Item -ItemType Directory -Path $destinationFolder | Out-Null }
        if (Test-Path -LiteralPath $absoluteTarget) { throw "Target appeared; stopped without overwrite: $absoluteTarget" }
        Move-Item -LiteralPath $absoluteSource -Destination $absoluteTarget
        $after = Get-Item -LiteralPath $absoluteTarget -Force
        if ($after.Length -ne $entry.bytes -or $after.LastWriteTimeUtc -ne $entry.modified_utc) { throw "Move metadata mismatch: $absoluteTarget" }
        $report.moved += $entry
        $done++
        if ($done % 50 -eq 0) { Write-Output "Archived with metadata verified: $done / $($plan.Count)" }
    }
}
foreach ($book in $catalog.books | Where-Object {$_.book_number -le 69}) {
    foreach ($language in @('ar','en')) {
        $folder = Join-Path $resolvedSource "$($book.id)\$language"
        $files = @(Get-ChildItem -LiteralPath $folder -File -Force)
        $report.checks += @{number=$book.book_number;language=$language;file_count=$files.Count;files=$files.Name}
    }
}
$report | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $PSScriptRoot 'four-file-cleanup-report.json') -Encoding UTF8
[pscustomobject]@{mode=$report.mode;planned=$plan.Count;moved=$report.moved.Count;renamed=$report.renamed.Count;covers_added=$report.covers_added.Count;language_folders=$report.checks.Count;exactly_four=@($report.checks | Where-Object {$_.file_count -eq 4}).Count;image_folders_preserved=$report.preserved_image_folders.Count;archive=$resolvedArchive} | ConvertTo-Json -Depth 4
