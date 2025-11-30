# I heven't run this script yet, because I don't have Windows machine available.
# start.ps1
$ErrorActionPreference = "Stop"

Write-Host "Removing exited containers (if any)..."
$exited = docker ps --filter "status=exited" -q
if ($exited) {
    $exited | ForEach-Object { docker rm $_ }
}

Write-Host "Building Docker image 'slice_api'..."
docker build -t slice_api .

Write-Host "Running container on port 8085..."
docker run -p 8085:8080 slice_api  # Spremeni port, če želiš