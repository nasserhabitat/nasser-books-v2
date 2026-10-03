# Native Word PDF exports and UTF-8 TXT copies. Sources and Drive objects are never changed.
param([int[]]$OnlyNumbers=@(), [string]$OnlyLanguage='', [switch]$TextOnly)
$ErrorActionPreference='Stop'
$siteRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$sourceRoot='C:\Users\nasse\OneDrive\Documents\google_books'
$catalog=[IO.File]::ReadAllText((Join-Path $siteRoot 'ai-index.json')) | ConvertFrom-Json
$reportPath=Join-Path $sourceRoot 'pdf-txt-export-report.json'
$records=@()
if(Test-Path -LiteralPath $reportPath){$records=@([IO.File]::ReadAllText($reportPath)|ConvertFrom-Json)}
$word=$null
$utf8=[Text.UTF8Encoding]::new($false)
function Save-Report { [IO.File]::WriteAllText($reportPath, (ConvertTo-Json -InputObject @($script:records) -Depth 10)+"`n", $script:utf8) }
try {
 if(!$TextOnly){
  $word=New-Object -ComObject Word.Application
  $word.Visible=$false;$word.DisplayAlerts=0;$word.ScreenUpdating=$false;$word.AutomationSecurity=3
  $word.Options.UpdateLinksAtOpen=$false
 }
 foreach($book in $catalog.books | Where-Object { $_.book_number -ge 70 -and (!$OnlyNumbers.Count -or $_.book_number -in $OnlyNumbers) }){
  foreach($lang in @('ar','en')){
   if($OnlyLanguage -and $lang -ne $OnlyLanguage){continue}
   $folder=Join-Path $sourceRoot "$($book.book_number)-$($book.id)\$lang"
   $resolvedFolder=[IO.Path]::GetFullPath($folder)
   if(!$resolvedFolder.StartsWith($sourceRoot+'\',[StringComparison]::OrdinalIgnoreCase)){throw 'Output outside approved book folder'}
   if(!(Test-Path -LiteralPath $folder -PathType Container)){throw "Missing book folder: $folder"}
   $stem="$($book.book_number)-$($book.id)-$lang"
   $sources=@(Get-ChildItem -LiteralPath $folder -File | Where-Object {$_.Extension -eq '.docx' -and !$_.Name.StartsWith('~$')})
   if($sources.Count -ne 1){throw "Ambiguous Word files in $folder"}
   $source=$sources[0].FullName
   $sourceHash=(Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash
   $txt=Join-Path $folder ($stem+'.txt')
   $siteTxt=Join-Path $siteRoot "books\$($book.id)\$lang\$stem.txt"
   if(Test-Path -LiteralPath $txt){
    if((Get-FileHash -LiteralPath $txt).Hash -ne (Get-FileHash -LiteralPath $siteTxt).Hash){throw "Existing TXT differs; not overwritten: $txt"}
   }else{Copy-Item -LiteralPath $siteTxt -Destination $txt}
   $pdf=Join-Path $folder ($stem+'.pdf')
   $status='TXT ready';$message='';$doc=$null
   try {
    if(!$TextOnly){
     if(Test-Path -LiteralPath $pdf){$status='Existing PDF retained'}
     else{
      $pending=Join-Path $folder ($stem+'.pending.pdf')
      if(Test-Path -LiteralPath $pending){throw "Previous incomplete output exists: $pending"}
      if(!$word){
       $word=New-Object -ComObject Word.Application
       $word.Visible=$false;$word.DisplayAlerts=0;$word.ScreenUpdating=$false;$word.AutomationSecurity=3
       $word.Options.UpdateLinksAtOpen=$false
      }
      $doc=$word.Documents.Open($source,$false,$true,$false)
      $doc.ExportAsFixedFormat($pending,17,$false,0,0,1,1,0,$false,$true,1,$true,$true,$false)
      # Some Word builds disconnect after a large PDF export. A close failure
      # must not discard a fully written PDF; final output is checked separately.
      try{$doc.Close(0)}catch{}
      try{[void][Runtime.InteropServices.Marshal]::ReleaseComObject($doc)}catch{}
      $doc=$null
      try{$wordVersionCheck=$word.Version}catch{$word=$null}
      if(!(Test-Path -LiteralPath $pending) -or (Get-Item -LiteralPath $pending).Length -lt 500){throw 'PDF export missing or empty'}
      Move-Item -LiteralPath $pending -Destination $pdf
      $status='PDF and TXT ready'
     }
    }
   }catch{
    $status='PDF failed; TXT ready';$message=$_.Exception.Message
    if($word){try{$word.Quit(0)}catch{};try{[void][Runtime.InteropServices.Marshal]::ReleaseComObject($word)}catch{};$word=$null}
   }
   finally{if($doc){try{$doc.Close(0)}catch{};try{[void][Runtime.InteropServices.Marshal]::ReleaseComObject($doc)}catch{};$doc=$null}}
   if((Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash -ne $sourceHash){throw "Word source changed unexpectedly: $source"}
   $script:records=@($script:records | Where-Object { !($_.number -eq $book.book_number -and $_.language -eq $lang) })
   $script:records+=[pscustomobject]@{number=$book.book_number;id=$book.id;language=$lang;source=$source;source_sha256=$sourceHash;txt=$txt;pdf=$pdf;status=$status;message=$message}
   Save-Report
   Write-Output "$($book.book_number) $lang — $status"
   if($message){Write-Output $message}
  }
 }
}finally{if($word){try{$word.Quit(0)}catch{};try{[void][Runtime.InteropServices.Marshal]::ReleaseComObject($word)}catch{}}}
