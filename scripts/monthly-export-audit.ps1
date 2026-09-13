# Read-only monthly preflight. No copies, deletions or overwrites.
$ErrorActionPreference = 'Stop'
$sourceRoot = 'C:\Users\nasse\OneDrive\Documents\GitHub\nasser-books\books'
$catalog = Get-Content (Join-Path $PSScriptRoot '..\ai-index.json') -Raw | ConvertFrom-Json
foreach ($book in $catalog.books) {
 foreach ($lang in @('ar','en')) {
  $folder = Join-Path $sourceRoot (Split-Path ($book.$lang.txt_direct -replace '^.*/books/','') -Parent)
  foreach ($ext in @('docx','pdf','txt')) {
   $files = @(Get-ChildItem -LiteralPath $folder -File | Where-Object { $_.Extension -eq ".$ext" -and !$_.Name.StartsWith('~$') } | Sort-Object LastWriteTime -Descending)
   $status = 'Ready'
   if (!$files.Count) { $status = 'Missing' }
   elseif ($files.Count -gt 1 -and $files[0].LastWriteTime -eq $files[1].LastWriteTime -and (Get-FileHash -LiteralPath $files[0].FullName).Hash -ne (Get-FileHash -LiteralPath $files[1].FullName).Hash) { $status = 'Ambiguous' }
   [pscustomobject]@{Book=$book.id;Language=$lang;Format=$ext;Status=$status;Source=if($status -eq 'Ready'){$files[0].FullName}else{''};ExportName="$($book.book_number)-$($book.id)-$lang.$ext"}
  }
 }
}
