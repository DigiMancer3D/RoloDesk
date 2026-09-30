$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Py = Get-Command py -ErrorAction SilentlyContinue
if ($Py) { & py -3 "$Root\rolodesk_local.py" serve @args; exit $LASTEXITCODE }
$Python = Get-Command python -ErrorAction SilentlyContinue
if ($Python) { & python "$Root\rolodesk_local.py" serve @args; exit $LASTEXITCODE }
Write-Error "Python 3 is required for local-server mode. You can still open RoloDesk_v0.3.4.html directly."
