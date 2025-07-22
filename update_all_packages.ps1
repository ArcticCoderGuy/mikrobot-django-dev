# Hakee kaikki vanhentuneet paketit
$pakat = pip list --outdated --format=json | ConvertFrom-Json

foreach ($paketti in $pakat) {
    $nimi = $paketti.name
    Write-Host "⏫ Päivitetään paketti: $nimi"
    pip install --upgrade $nimi
}

Write-Host "`n✅ Kaikki päivitykset suoritettu!"
