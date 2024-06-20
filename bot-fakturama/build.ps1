$exclude = @("venv", "bot-fakturama.zip")
$files = Get-ChildItem -Path . -Exclude $exclude
Compress-Archive -Path $files -DestinationPath "bot-fakturama.zip" -Force