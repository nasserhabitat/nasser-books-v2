# Read-only inventory of local working files and streamed Drive directory metadata.
$ErrorActionPreference='Stop'
$siteRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$roots=@('C:\Users\nasse\OneDrive\Documents\google_books','G:\Mon Drive\كتبي','G:\Mon Drive\google_books','G:\Mon Drive\كتب جديدة')
$inventory=@()
foreach($root in $roots){
 $files=@(Get-ChildItem -LiteralPath $root -Recurse -File -Force | Where-Object {$_.Extension.ToLowerInvariant() -in '.docx','.pdf','.txt','.png','.jpg','.jpeg','.html','.htm'})
 $inventory+=[pscustomobject]@{root=$root;files=@($files|ForEach-Object{[pscustomobject]@{relative=$_.FullName.Substring($root.Length+1);name=$_.Name;extension=$_.Extension.ToLowerInvariant();bytes=$_.Length;modified_utc=$_.LastWriteTimeUtc.ToString('o');attributes=$_.Attributes.ToString()}})}
 Write-Output "$root — $($files.Count) file metadata records; no content downloaded"
}
$output=Join-Path $siteRoot 'scripts/monthly-sync-local-inventory.json'
[IO.File]::WriteAllText($output,(ConvertTo-Json -InputObject $inventory -Depth 8)+"`n",[Text.UTF8Encoding]::new($false))
