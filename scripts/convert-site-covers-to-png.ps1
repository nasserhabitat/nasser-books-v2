# Container-format conversion only: no resize, text edits, or visual regeneration.
# User's source JPEGs outside the website repository remain untouched.
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing
$siteRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$coverPaths = @(
 'books\governance-quranic-knowledge-production\en\governance-quranic-knowledge-production-cover-en.jpg',
 'books\architecture-of-karamah\en\architecture-of-karamah-cover-en.jpg',
 'books\preserved-system\en\preserved-system-cover-en.jpg'
)
$siteCoverConversions = @()
foreach ($coverRelative in $coverPaths) {
 $coverSource = [IO.Path]::GetFullPath((Join-Path $siteRoot $coverRelative))
 if (!$coverSource.StartsWith($siteRoot + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)) { throw 'Invalid image target' }
 $coverTarget = [IO.Path]::ChangeExtension($coverSource, '.png')
 $coverImage = [Drawing.Image]::FromFile($coverSource)
 try { $coverImage.Save($coverTarget, [Drawing.Imaging.ImageFormat]::Png) } finally { $coverImage.Dispose() }
 $coverCheck = [Drawing.Image]::FromFile($coverTarget)
 try { if ($coverCheck.Width -lt 1 -or $coverCheck.Height -lt 1) { throw 'Invalid converted image' } } finally { $coverCheck.Dispose() }
 $oldUrl = $coverRelative.Replace('\','/')
 $newUrl = [IO.Path]::ChangeExtension($oldUrl, '.png')
 $utf8NoBom = [Text.UTF8Encoding]::new($false)
 Get-ChildItem -LiteralPath $siteRoot -Recurse -File | Where-Object { $_.Extension -in '.html','.json' -and !$_.FullName.Contains('\.git\') -and !$_.FullName.Contains('\scripts\') } | ForEach-Object {
  $coverText = [IO.File]::ReadAllText($_.FullName)
  $revisedCoverText = $coverText.Replace($oldUrl, $newUrl).Replace([IO.Path]::GetFileName($oldUrl), [IO.Path]::GetFileName($newUrl))
  if ($coverText -ne $revisedCoverText) { [IO.File]::WriteAllText($_.FullName, $revisedCoverText, $utf8NoBom) }
 }
 # Only the derived website JPEG is removed after the PNG and references exist.
 Remove-Item -LiteralPath $coverSource
 $siteCoverConversions += [pscustomobject]@{Cover=$newUrl;Sha256=(Get-FileHash -LiteralPath $coverTarget -Algorithm SHA256).Hash.ToLowerInvariant()}
 [pscustomobject]@{Cover=$newUrl;Result='PNG ready; source folder unchanged'}
}
$reportPath = Join-Path $PSScriptRoot 'migration-report.json'
$reportData = [IO.File]::ReadAllText($reportPath) | ConvertFrom-Json
$reportData | Add-Member -NotePropertyName site_cover_conversions -NotePropertyValue $siteCoverConversions -Force
$reportData.cover_refresh | Add-Member -NotePropertyName site_png -NotePropertyValue 86 -Force
[IO.File]::WriteAllText($reportPath, ($reportData | ConvertTo-Json -Depth 50) + "`n", [Text.UTF8Encoding]::new($false))
