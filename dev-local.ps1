# Local package checks and optional Blender extension build.
param([switch]$Build)
$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
function Run-Python([string[]]$Arguments) {
    & python @Arguments
    if ($LASTEXITCODE -ne 0) { throw "python $($Arguments -join ' ') failed with exit code $LASTEXITCODE" }
}
Push-Location $Root
try {
    Run-Python @('scripts/check_no_em_dashes.py')
    Run-Python @('scripts/check_release.py')
    Run-Python @('scripts/test_smart_budget.py')
    if ($Build) {
        Run-Python @('scripts/build_blender.py')
        Run-Python @('scripts/build_blender_extension.py')
    }
    Write-Host "Local Optimize-Your-Project checks passed. GitHub Actions was not used."
} finally { Pop-Location }
