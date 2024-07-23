$sd = Split-Path -Parent $MyInvocation.MyCommand.Definition

echo $sd

Set-Location -Path $sd

$vePath = Join-Path $sd "env\Scripts\activate.ps1"

& $vePath

python manage.py uploadParticipant
python manage.py uploadDataprotection