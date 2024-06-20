$exclude = @("venv", "bot_sicalc_id.zip")
$files = Get-ChildItem -Path . -Exclude $exclude
Compress-Archive -Path $files -DestinationPath "bot_sicalc_id.zip" -Force