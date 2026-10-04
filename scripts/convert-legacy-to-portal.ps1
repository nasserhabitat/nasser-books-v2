param([switch]$Apply)
$ErrorActionPreference = 'Stop'
$root = 'C:\Users\nasse\OneDrive\Documents\GitHub\nasser-books'
$newRoot = 'C:\Users\nasse\OneDrive\Documents\GitHub\nasser-books-v2'
$backup = 'C:\Users\nasse\OneDrive\Documents\library-backups\nasser-books-before-portal-20261004'
if ((Resolve-Path -LiteralPath $root).Path -ne $root) { throw 'Unexpected source directory' }
if (Test-Path -LiteralPath $backup) { throw 'Backup already exists; inspect before retrying' }
$catalog = Get-Content -LiteralPath (Join-Path $newRoot 'ai-index.json') -Raw | ConvertFrom-Json
if ($catalog.books.Count -ne 112) { throw 'Unexpected catalogue' }
$items = @(Get-ChildItem -LiteralPath $root -Force | Where-Object Name -ne '.git')
$files = @($items | ForEach-Object { if ($_.PSIsContainer) { Get-ChildItem -LiteralPath $_.FullName -Recurse -File -Force } else { $_ } })
$manifest = @($files | ForEach-Object { [pscustomobject]@{path=$_.FullName.Substring($root.Length+1);size=$_.Length;modified=$_.LastWriteTimeUtc.Ticks} })
if (!$Apply) { [pscustomobject]@{backup=$backup;files=$files.Count;bytes=($files|Measure-Object Length -Sum).Sum;books=$catalog.books.Count} | ConvertTo-Json; exit }
New-Item -ItemType Directory -Path $backup -Force | Out-Null
foreach ($item in $items) {
    $source = (Resolve-Path -LiteralPath $item.FullName).Path
    if (![IO.Path]::GetFullPath($source).StartsWith($root+'\',[StringComparison]::OrdinalIgnoreCase)) { throw 'Source outside repository' }
    $dest = Join-Path $backup $item.Name
    if (![IO.Path]::GetFullPath($dest).StartsWith($backup+'\',[StringComparison]::OrdinalIgnoreCase)) { throw 'Destination outside backup' }
    Move-Item -LiteralPath $source -Destination $dest
}
foreach ($entry in $manifest) {
    $saved = Get-Item -LiteralPath (Join-Path $backup $entry.path) -Force
    if ($saved.Length -ne $entry.size -or $saved.LastWriteTimeUtc.Ticks -ne $entry.modified) { throw ('Backup mismatch: '+$entry.path) }
}
$utf8 = [Text.UTF8Encoding]::new($false)
function Save([string]$relative,[string]$text) {
    $dest = Join-Path $root $relative
    New-Item -ItemType Directory -Path ([IO.Path]::GetDirectoryName($dest)) -Force | Out-Null
    [IO.File]::WriteAllText($dest,$text,$utf8)
}
function Portal([string]$url,[bool]$redirect) {
    $safe = [Net.WebUtility]::HtmlEncode($url)
    $refresh = if ($redirect) { '<meta http-equiv="refresh" content="0;url='+$safe+'">' } else { '' }
    return @"
<!doctype html>
<html lang="ar" dir="rtl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>انتقلت المكتبة — ناصر ابن داوود</title><link rel="canonical" href="$safe">$refresh
<style>body{font-family:system-ui,sans-serif;background:#f4f7fa;color:#183249;line-height:1.9;margin:0;padding:24px}main{max-width:760px;margin:8vh auto;background:white;padding:32px;border-radius:16px}a{color:#086b77}.button{display:inline-block;background:#086b77;color:white;padding:12px 24px;border-radius:8px;text-decoration:none}footer{margin-top:28px;font-size:.95rem}</style></head>
<body><main><h1>مكتبة ناصر ابن داوود — انتقلنا إلى الموقع الجديد</h1>
<p>أصبح <strong>nasser-books-v2</strong> المستودع المعتمد لكتبي. تُنشر فيه الكتب الجديدة والتعديلات أولًا بأول، وتُحدَّث المكتبة باستمرار على مدار الساعة.</p>
<p>هذا الموقع القديم مخصّص للإعلان عن الانتقال وتوجيه القراء إلى المكتبة المحدّثة.</p>
<p><a class="button" href="$safe">زيارة المكتبة المحدّثة</a></p>
<p><a href="https://nasserhabitat.github.io/nasser-books-v2/search.html">البحث في الكتب</a> · <a href="https://github.com/nasserhabitat/nasser-books-v2">المستودع الجديد على GitHub</a></p>
<footer lang="en" dir="ltr">The library has moved to nasser-books-v2. New books and ongoing updates are published there. Please update your bookmarks.</footer>
</main></body></html>
"@
}
$base = 'https://nasserhabitat.github.io/nasser-books-v2/'
Save 'index.html' (Portal $base $false)
foreach ($page in (Get-ChildItem -LiteralPath $backup -File -Filter '*.html')) {
    if ($page.Name -in @('index.html','404.html','googlecf8d734095ac1dc2.html')) {continue}
    $target = if (Test-Path -LiteralPath (Join-Path $newRoot $page.Name)) {$base+$page.Name} else {$base}
    Save $page.Name (Portal $target $true)
}
foreach ($book in $catalog.books) {
    foreach ($lang in @('ar','en')) {
        $slug = [string]$book.id
        $oldSlug = if ($slug -eq 'numbers-as-legislation') {'numbers-as-Legislation'} else {$slug}
        Save ('books/'+$oldSlug+'/'+$lang+'/index.html') (Portal ($base+'books/'+$slug+'/'+$lang+'/') $true)
    }
}
$fallback = Portal $base $false
$routing = @'
<script>
const match = location.pathname.match(/^\/nasser-books\/books\/([^/]+)\/(ar|en)(?:\/|$)/);
if (match) {
  const slug = match[1] === 'numbers-as-Legislation' ? 'numbers-as-legislation' : match[1];
  location.replace('https://nasserhabitat.github.io/nasser-books-v2/books/' + encodeURIComponent(decodeURIComponent(slug)) + '/' + match[2] + '/');
}
</script>
'@
Save '404.html' ($fallback.Replace('</body>',$routing+'</body>'))
Save 'README.md' @'
# مكتبة ناصر ابن داوود — المستودع القديم

**انتقلت المكتبة إلى [nasser-books-v2](https://github.com/nasserhabitat/nasser-books-v2).**

المستودع الجديد هو المعتمد لنشر كتبي وتحديثاتها أولًا بأول على مدار الساعة. هذا المستودع القديم بوابة للإعلان عن الانتقال وتوجيه القراء فقط.

- [زيارة المكتبة المحدّثة](https://nasserhabitat.github.io/nasser-books-v2/)
- [الكتب العربية](https://nasserhabitat.github.io/nasser-books-v2/arabic-books.html)
- [English books](https://nasserhabitat.github.io/nasser-books-v2/english-books.html)
- [البحث الداخلي](https://nasserhabitat.github.io/nasser-books-v2/search.html)

يرجى اعتماد روابط الموقع الجديد في المفضلة والإحالات المستقبلية.

The library has moved to **nasser-books-v2**. All new books and ongoing updates are published there. This repository serves as a migration notice and redirects existing book pages.
'@
Save '.nojekyll' ''
Save '.gitignore' "Thumbs.db`ndesktop.ini`n.DS_Store`n"
Save 'robots.txt' "User-agent: *`nAllow: /`nSitemap: https://nasserhabitat.github.io/nasser-books/sitemap.xml`n"
Save 'sitemap.xml' '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>https://nasserhabitat.github.io/nasser-books/</loc></url></urlset>'
foreach ($name in @('googlecf8d734095ac1dc2.html','BingSiteAuth.xml')) {
    if (Test-Path -LiteralPath (Join-Path $backup $name)) { Copy-Item -LiteralPath (Join-Path $backup $name) -Destination (Join-Path $root $name) }
}
$current = @(Get-ChildItem -LiteralPath $root -Force | Where-Object Name -ne '.git' | ForEach-Object {if ($_.PSIsContainer) {Get-ChildItem -LiteralPath $_.FullName -Recurse -File -Force} else {$_}})
[pscustomobject]@{backup=$backup;backupFiles=$manifest.Count;previousBytes=($files|Measure-Object Length -Sum).Sum;portalFiles=$current.Count;portalBytes=($current|Measure-Object Length -Sum).Sum;bookRedirects=224} | ConvertTo-Json
