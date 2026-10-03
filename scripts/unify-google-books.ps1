# Consolidate book folders without overwriting or deleting any file.
param([switch]$Apply)
$ErrorActionPreference='Stop'
$unifyRoot=[IO.Path]::GetFullPath('C:\Users\nasse\OneDrive\Documents\google_books')
$incomingRoot=Join-Path $unifyRoot 'incoming_70-112'
$siteRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$cat=([IO.File]::ReadAllText((Join-Path $siteRoot 'ai-index.json'))|ConvertFrom-Json).books
if($cat.Count -ne 112){throw 'Expected 112 catalogue books'}
$dirs=@(Get-ChildItem -LiteralPath $unifyRoot -Directory)
if(Test-Path -LiteralPath $incomingRoot){$dirs+=@(Get-ChildItem -LiteralPath $incomingRoot -Directory)}
$plan=@()
foreach($book in ($cat|Sort-Object book_number)){
 $matches=@($dirs|Where-Object {$_.Name -match ('^'+$book.book_number+'-')})
 if($matches.Count -ne 1){throw "Ambiguous/missing folder for book $($book.book_number): $($matches.Count)"}
 $source=[IO.Path]::GetFullPath($matches[0].FullName)
 $target=[IO.Path]::GetFullPath((Join-Path $unifyRoot "$($book.book_number)-$($book.id)"))
 if([IO.Path]::GetDirectoryName($target) -ne $unifyRoot){throw 'Destination escapes the named daily folder'}
 if($source -ne $target){
  if([IO.Path]::GetDirectoryName($source) -ne $incomingRoot){throw "Unexpected source outside incoming folder: $source"}
  if(!$source.StartsWith($incomingRoot+[IO.Path]::DirectorySeparatorChar,[StringComparison]::OrdinalIgnoreCase)){throw 'Unsafe source'}
  if(Test-Path -LiteralPath $target){throw "Destination exists; not overwritten: $target"}
 }
 foreach($lang in @('ar','en')){if(!(Test-Path -LiteralPath (Join-Path $source $lang) -PathType Container)){throw "Missing language folder: $source/$lang"}}
 $plan+=[pscustomobject]@{number=$book.book_number;id=$book.id;source=$source;target=$target;move=($source -ne $target)}
}
if(!$Apply){[pscustomobject]@{books=$plan.Count;folders_to_move=@($plan|Where-Object move).Count;plan=$plan}|ConvertTo-Json -Depth 6;exit}
$verifiedFiles=0
foreach($item in $plan){
 if(!$item.move){continue}
 $before=@(Get-ChildItem -LiteralPath $item.source -Recurse -File|ForEach-Object{[pscustomobject]@{relative=$_.FullName.Substring($item.source.Length+1);sha256=(Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash;bytes=$_.Length}})
 # Both resolved absolute paths were validated against the explicit daily root.
 Move-Item -LiteralPath $item.source -Destination $item.target
 foreach($entry in $before){
  $file=Join-Path $item.target $entry.relative
  if(!(Test-Path -LiteralPath $file) -or (Get-FileHash -LiteralPath $file -Algorithm SHA256).Hash -ne $entry.sha256){throw "Content verification failed: $file"}
  $verifiedFiles++
 }
 Write-Output "$($item.number) moved; $($before.Count) file hashes unchanged"
}
$editions=@()
foreach($item in $plan){foreach($lang in @('ar','en')){
 $files=@(Get-ChildItem -LiteralPath (Join-Path $item.target $lang) -File)
 $editions+=[pscustomobject]@{number=$item.number;id=$item.id;language=$lang;folder=(Join-Path $item.target $lang);word=@($files|Where-Object Extension -eq '.docx').Count;pdf=@($files|Where-Object Extension -eq '.pdf').Count;txt=@($files|Where-Object Extension -eq '.txt').Count;covers=@($files|Where-Object {$_.Extension -in '.png','.jpg','.jpeg'}).Count}
}}
$report=[pscustomobject]@{books=$plan.Count;language_folders=$editions.Count;moved_folders=@($plan|Where-Object move).Count;moved_files_verified=$verifiedFiles;missing_word=@($editions|Where-Object word -eq 0);missing_txt=@($editions|Where-Object txt -eq 0);missing_pdf=@($editions|Where-Object pdf -eq 0);editions=$editions;no_files_deleted=$true;no_existing_file_overwritten=$true}
$utf8=[Text.UTF8Encoding]::new($false)
$reportPath=Join-Path $unifyRoot 'unified-library-report.json'
if(Test-Path -LiteralPath $reportPath){$reportPath=Join-Path $unifyRoot ('unified-library-report-'+[DateTime]::Now.ToString('yyyyMMdd-HHmmss')+'.json')}
[IO.File]::WriteAllText($reportPath,($report|ConvertTo-Json -Depth 8)+"`n",$utf8)
# Preserve the original export log; relocate paths in a new operational copy.
$oldReport=Join-Path $incomingRoot 'pdf-txt-export-report.json'
$newReport=Join-Path $unifyRoot 'pdf-txt-export-report.json'
if((Test-Path -LiteralPath $oldReport) -and !(Test-Path -LiteralPath $newReport)){
 $records=@([IO.File]::ReadAllText($oldReport)|ConvertFrom-Json)
 foreach($r in $records){
  $folder=Join-Path $unifyRoot "$($r.number)-$($r.id)\$($r.language)"
  foreach($key in @('source','txt','pdf')){$r.$key=Join-Path $folder ([IO.Path]::GetFileName($r.$key))}
  if(!(Test-Path -LiteralPath $r.source)){$docs=@(Get-ChildItem -LiteralPath $folder -File -Filter '*.docx');if($docs.Count -eq 1){$r.source=$docs[0].FullName}}
 }
 [IO.File]::WriteAllText($newReport,(ConvertTo-Json -InputObject $records -Depth 8)+"`n",$utf8)
}
[pscustomobject]@{books=$plan.Count;language_folders=$editions.Count;moved_folders=@($plan|Where-Object move).Count;verified_files=$verifiedFiles;word_files=($editions|Measure-Object word -Sum).Sum;pdf_files=($editions|Measure-Object pdf -Sum).Sum;txt_files=($editions|Measure-Object txt -Sum).Sum;report=$reportPath}|ConvertTo-Json
