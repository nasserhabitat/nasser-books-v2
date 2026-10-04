param([switch]$Apply)
$ErrorActionPreference='Stop'
$sourceRoot='C:\Users\nasse\OneDrive\Documents\GitHub\nasser-books-v2'
$targetRoot='C:\Users\nasse\OneDrive\Documents\GitHub\nasser-books'
if ((Resolve-Path -LiteralPath $targetRoot).Path -ne $targetRoot) {throw 'Unexpected destination'}
if (git -C $targetRoot status --porcelain) {throw 'Destination has uncommitted changes; stop'}
$sourceRevision=(git -C $sourceRoot rev-parse HEAD).Trim()
$beforeRevision=(git -C $targetRoot rev-parse HEAD).Trim()
if (!$Apply) { [pscustomobject]@{source=$sourceRevision;destination=$beforeRevision;policy='Copy committed website; preserve manuscript binaries and old TXT/cover URLs'} | ConvertTo-Json; exit }
$recoveryBranch='codex/backup-before-v2-sync-20261003'
git -C $targetRoot show-ref --verify --quiet ('refs/heads/'+$recoveryBranch)
if ($LASTEXITCODE -ne 0) {
    git -C $targetRoot branch $recoveryBranch $beforeRevision
    if ($LASTEXITCODE -ne 0) {throw 'Could not create recovery branch'}
} elseif ((git -C $targetRoot rev-parse $recoveryBranch).Trim() -ne $beforeRevision) {throw 'Unexpected recovery revision'}
$sourceDirty=@(git -C $sourceRoot diff --name-only)
foreach ($name in $sourceDirty) {if ($name -notin @('search.html','ai-recommendations.html','books/adultery/ar/cover-ar.jpg')) {throw ('Unexpected source change: '+$name)}}
if (git -C $sourceRoot diff --cached --name-only) {throw 'Unexpected staged source edits'}
$sourcePaths=@(git -C $sourceRoot -c core.quotepath=false ls-tree -r --name-only HEAD)
$protected=Get-ChildItem -LiteralPath $targetRoot -Recurse -File | Where-Object {$_.Extension -in '.docx','.pdf'} | ForEach-Object {[pscustomobject]@{path=$_.FullName;size=$_.Length;modified=$_.LastWriteTimeUtc.Ticks}}
$textExtensions=@('.html','.htm','.json','.xml','.js','.cjs','.css','.md','.py','.ps1','.yml','.yaml')
$copied=0;$managed=[Collections.Generic.List[string]]::new()
foreach ($relative in $sourcePaths) {
    $sourceRelative=$relative
    $relative=$relative.Replace('books/numbers-as-legislation/','books/numbers-as-Legislation/').Replace('api/ai-access/metadata/numbers-as-legislation.json','api/ai-access/metadata/numbers-as-Legislation.json')
    $extension=[IO.Path]::GetExtension($relative)
    # Keep the old site's existing build method; never introduce book binaries.
    if ($relative -eq '.nojekyll' -or $relative -match '/content\.files/' -or $relative -eq 'books/adultery/ar/cover-ar.jpg' -or $extension -in '.docx','.pdf','.zip') {continue}
    $source=Join-Path $sourceRoot $sourceRelative
    $dest=Join-Path $targetRoot $relative
    New-Item -ItemType Directory -Path ([IO.Path]::GetDirectoryName($dest)) -Force | Out-Null
    if ($extension -in $textExtensions -or $relative -eq 'robots.txt') {
        $content=if ($sourceRelative -in $sourceDirty) {[string]::Join("`n",@(git -C $sourceRoot show ('HEAD:'+$sourceRelative)))+"`n"} else {[IO.File]::ReadAllText($source)}
        $content=$content.Replace('nasser-books-v2','nasser-books').Replace('/numbers-as-legislation/','/numbers-as-Legislation/')
        [IO.File]::WriteAllText($dest,$content,[Text.UTF8Encoding]::new($false))
    } else {Copy-Item -LiteralPath $source -Destination $dest -Force}
    $copied++;$managed.Add($relative)
}
$catalog=Get-Content -LiteralPath (Join-Path $targetRoot 'ai-index.json') -Raw | ConvertFrom-Json
$aliases=0
foreach ($book in $catalog.books) {
    foreach ($language in @('ar','en')) {
        $legacyId=if($book.id -ceq 'numbers-as-legislation') {'numbers-as-Legislation'} else {$book.id}
        $folder=Join-Path $targetRoot ('books/'+$legacyId+'/'+$language)
        $name=[string]$book.book_number+'-'+$book.id+'-'+$language+'.txt'
        Copy-Item -LiteralPath (Join-Path $folder $name) -Destination (Join-Path $folder 'content.txt') -Force
        Copy-Item -LiteralPath (Join-Path $folder ($book.id+'-cover-'+$language+'.png')) -Destination (Join-Path $folder ('cover-'+$language+'.png')) -Force
        $managed.Add('books/'+$legacyId+'/'+$language+'/content.txt')
        $managed.Add('books/'+$legacyId+'/'+$language+'/cover-'+$language+'.png')
        $aliases+=2
    }
}
foreach ($record in $protected) {
    $current=Get-Item -LiteralPath $record.path
    if ($current.Length -ne $record.size -or $current.LastWriteTimeUtc.Ticks -ne $record.modified) {throw ('Protected book changed: '+$record.path)}
}
$report=[pscustomobject]@{source_revision=$sourceRevision;old_revision=$beforeRevision;recovery_branch=$recoveryBranch;website_files=$copied;compatibility_aliases=$aliases;protected_book_files=$protected.Count;books=$catalog.books.Count;managed_paths=@($managed)}
[IO.File]::WriteAllText((Join-Path $sourceRoot 'scripts/legacy-site-sync-report.json'),($report | ConvertTo-Json -Depth 3),[Text.UTF8Encoding]::new($false))
$report | Select-Object * -ExcludeProperty managed_paths | ConvertTo-Json
