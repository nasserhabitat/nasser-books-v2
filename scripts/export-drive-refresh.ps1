param([Parameter(Mandatory=$true)][string]$WorkRoot,[int[]]$OnlyNumbers=@())
$ErrorActionPreference='Stop'
$plan=Get-Content (Join-Path $PSScriptRoot 'drive-refresh-plan-2026-10-27.json') -Raw | ConvertFrom-Json
$utf8=[Text.UTF8Encoding]::new($false)
$word=$null
try {
 foreach($e in $plan) {
  if($OnlyNumbers.Count -and $e.number -notin $OnlyNumbers){continue}
  $folder=Join-Path $WorkRoot "$($e.number)/$($e.language)"
  $source=Join-Path $folder 'source.docx'
  $pdf=Join-Path $folder 'export.pdf'
  $txt=Join-Path $folder 'export.txt'
  $receipt=Join-Path $folder 'export.json'
  if(Test-Path -LiteralPath $receipt){continue}
  if(!(Test-Path -LiteralPath $source)){continue}
  $doc=$null;$result=[ordered]@{number=$e.number;language=$e.language;status='failed'}
  try {
   if((Get-Item -LiteralPath $source).Length -ne $e.word_size){throw 'Source size mismatch'}
   $before=(Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash
   if(!$word){
    $word=New-Object -ComObject Word.Application
    $word.Visible=$false;$word.DisplayAlerts=0;$word.ScreenUpdating=$false;$word.AutomationSecurity=3
    $word.Options.UpdateLinksAtOpen=$false
   }
   $doc=$word.Documents.Open($source,$false,$true,$false)
   $pages=$doc.ComputeStatistics(2)
   $doc.ExportAsFixedFormat($pdf,17,$false,0,0,1,1,0,$false,$true,1,$true,$true,$false)
   # Save a separate UTF-8 text copy with Word's own numbering/table conversion.
   $doc.SaveAs2($txt,7,$false,'',$false,'',$false,$false,$false,$false,$false,65001)
   $doc.Close(0)
   [void][Runtime.InteropServices.Marshal]::ReleaseComObject($doc);$doc=$null
   if((Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash -ne $before){throw 'Source changed'}
   if((Get-Item -LiteralPath $pdf).Length -lt 500 -or (Get-Item -LiteralPath $txt).Length -lt 10){throw 'Empty export'}
   $result.status='exported';$result.word_sha256=$before;$result.word_pages=$pages
   $result.pdf_sha256=(Get-FileHash -LiteralPath $pdf -Algorithm SHA256).Hash
   $result.txt_sha256=(Get-FileHash -LiteralPath $txt -Algorithm SHA256).Hash
   [IO.File]::WriteAllText($receipt,($result|ConvertTo-Json),$utf8)
   Write-Output "$($e.number)/$($e.language): exported $pages pages"
  } catch {
   $result.error=$_.Exception.Message
   [IO.File]::WriteAllText((Join-Path $folder 'error.json'),($result|ConvertTo-Json),$utf8)
   Write-Output "$($e.number)/$($e.language): FAILED $($_.Exception.Message)"
   if($word){try{$word.Quit(0)}catch{};$word=$null}
  } finally {if($doc){try{$doc.Close(0)}catch{};try{[void][Runtime.InteropServices.Marshal]::ReleaseComObject($doc)}catch{}}}
 }
} finally {if($word){try{$word.Quit(0)}catch{};try{[void][Runtime.InteropServices.Marshal]::ReleaseComObject($word)}catch{}}}
