$exclude = @("venv", "BotCotacao.zip")
$files = Get-ChildItem -Path . -Exclude $exclude
Compress-Archive -Path $files -DestinationPath "BotCotacao.zip" -Force