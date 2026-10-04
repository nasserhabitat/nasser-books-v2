param([switch]$Apply)
$ErrorActionPreference = 'Stop'
$taskRoot = 'G:\Mon Drive\كتبي'
$catalogPath = Join-Path $PSScriptRoot '..\ai-index.json'
$catalog = Get-Content -LiteralPath $catalogPath -Raw -Encoding UTF8 | ConvertFrom-Json
$resolvedRoot = (Resolve-Path -LiteralPath $taskRoot).Path.TrimEnd('\')
$reportPath = Join-Path $PSScriptRoot 'legacy-drive-rename-report.json'
$previousFiles = @()
if (Test-Path -LiteralPath $reportPath) { $previousFiles = @((Get-Content -LiteralPath $reportPath -Raw | ConvertFrom-Json).files) }
$plan = @()
$issues = @()
foreach ($book in $catalog.books | Where-Object { $_.book_number -le 69 }) {
    $bookFolders = @(Get-ChildItem -LiteralPath $resolvedRoot -Directory | Where-Object { $_.Name -ieq $book.id })
    if ($bookFolders.Count -ne 1) { $issues += "Book folder missing/ambiguous: $($book.book_number) $($book.id)"; continue }
    foreach ($language in @('ar', 'en')) {
        $folder = Join-Path $bookFolders[0].FullName $language
        if (-not (Test-Path -LiteralPath $folder -PathType Container)) { $issues += "Language folder missing: $folder"; continue }
        foreach ($extension in @('docx', 'pdf', 'txt')) {
            $candidates = @(Get-ChildItem -LiteralPath $folder -File | Where-Object { $_.Name -iin @("content.$extension", "context.$extension") })
            if ($candidates.Count -eq 0) { continue }
            if ($candidates.Count -ne 1) { $issues += "Two source names coexist: $folder $extension"; continue }
            $targetName = "$($book.book_number)-$($book.id)-$language.$extension"
            $target = Join-Path $folder $targetName
            if (Test-Path -LiteralPath $target) { $issues += "Target exists; no overwrite: $target"; continue }
            $source = (Resolve-Path -LiteralPath $candidates[0].FullName).Path
            if (-not $source.StartsWith($resolvedRoot + '\', [StringComparison]::OrdinalIgnoreCase)) { throw "Source outside approved root: $source" }
            $plan += [pscustomobject]@{number=$book.book_number;id=$book.id;language=$language;source=$source;target=$target;new_name=$targetName;bytes=$candidates[0].Length}
        }
    }
}
$allFiles = @(@($previousFiles) + @($plan) | Group-Object source | ForEach-Object {$_.Group[0]})
$report = [ordered]@{root=$resolvedRoot;mode=$(if ($Apply) {'apply'} else {'preview'});planned=$plan.Count;issues=$issues;files=$allFiles}
if ($Apply) {
    $completed = 0
    foreach ($entry in $plan) {
        if (Test-Path -LiteralPath $entry.target) { throw "Target appeared; stopped without overwrite: $($entry.target)" }
        $before = Get-Item -LiteralPath $entry.source
        $beforeBytes = $before.Length
        $beforeTime = $before.LastWriteTimeUtc
        Rename-Item -LiteralPath $entry.source -NewName $entry.new_name
        $after = Get-Item -LiteralPath $entry.target
        if ($beforeBytes -ne $after.Length -or $beforeTime -ne $after.LastWriteTimeUtc) { throw "Metadata verification failed: $($entry.target)" }
        $completed++
        if ($completed % 25 -eq 0) { Write-Output "Renamed and metadata-verified: $completed / $($plan.Count)" }
    }
    $report.renamed = @($allFiles | Where-Object {(Test-Path -LiteralPath $_.target) -and -not (Test-Path -LiteralPath $_.source)}).Count
}
$report | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $reportPath -Encoding UTF8
[pscustomobject]@{mode=$report.mode;files=$plan.Count;docx=@($plan | Where-Object {$_.new_name -like '*.docx'}).Count;pdf=@($plan | Where-Object {$_.new_name -like '*.pdf'}).Count;txt=@($plan | Where-Object {$_.new_name -like '*.txt'}).Count;issues=$issues} | ConvertTo-Json -Depth 4
