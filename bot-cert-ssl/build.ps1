$exclude = @("venv", "bot-cert-ssl.zip")
$files = Get-ChildItem -Path . -Exclude $exclude
Compress-Archive -Path $files -DestinationPath "bot-cert-ssl.zip" -Force