$ErrorActionPreference = "Stop"

$server = "ubuntu@79.72.62.76"
$key = ".\ssh-key-2026-04-27.key"

Write-Host "Creating directory on server..."
ssh -i $key -o StrictHostKeyChecking=no $server "mkdir -p ~/barista_backend"

Write-Host "Copying backend files..."
scp -i $key -o StrictHostKeyChecking=no -r .\backend $server`:~/barista_backend/
scp -i $key -o StrictHostKeyChecking=no .\docker-compose.yml $server`:~/barista_backend/

Write-Host "Starting Docker Compose on server..."
ssh -i $key -o StrictHostKeyChecking=no $server "cd ~/barista_backend && sudo docker-compose down && sudo docker-compose up --build -d"

Write-Host "Deployment completed!"
