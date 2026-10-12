# Build every document, GLOSSARY and the unsorted holder in dependency order.
# Repeats full passes until no log reports changed labels, undefined or multiply
# defined references (at most 5 passes), then runs the internal-reference checks.
param([int]$MaxPasses = 5, [switch]$NoCheck)

$root = Split-Path -Parent $PSScriptRoot
$order = python -c "import sys; sys.path.insert(0, r'$PSScriptRoot'); from books import BUILD_ORDER, FOLDER, JOB; print('\n'.join(f'{FOLDER[c]}|{JOB[c]}' for c in BUILD_ORDER))"
$pattern = 'Label\(s\) may have changed|There were undefined references|multiply defined|Reference .* undefined|^No file .*\.aux|has been referenced but does not exist'

for ($pass = 1; $pass -le $MaxPasses; $pass++) {
    $dirty = @()
    foreach ($entry in $order) {
        $folder, $job = $entry -split '\|'
        Push-Location (Join-Path $root $folder)
        latexmk -silent | Out-Null
        $code = $LASTEXITCODE
        Pop-Location
        $log = Join-Path $root "$folder/build/$job.log"
        if ($code -ne 0) { $dirty += "$job (latexmk exit $code)" }
        elseif (Select-String -Path $log -Pattern $pattern -Quiet) { $dirty += $job }
    }
    Write-Host "pass ${pass}: $(if ($dirty) { 'pending: ' + ($dirty -join ', ') } else { 'stable' })"
    if (-not $dirty -and $pass -ge 2) { break }
}

if (-not $NoCheck) {
    python (Join-Path $PSScriptRoot 'check_xrefs.py')
    exit $LASTEXITCODE
}
