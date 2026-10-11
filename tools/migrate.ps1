# Ten-document migration: write the map, move every file, generate the scaffolding.
# Steps: python tools/restructure.py map | migrate | scaffold (see restructure.py).
param([ValidateSet('map', 'migrate', 'scaffold', 'all')][string]$Step = 'all')

$script = Join-Path $PSScriptRoot 'restructure.py'
$steps = if ($Step -eq 'all') { 'map', 'migrate', 'scaffold' } else { , $Step }
foreach ($s in $steps) {
    python $script $s
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}
