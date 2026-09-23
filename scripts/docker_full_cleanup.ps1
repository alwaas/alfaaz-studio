# # docker_full_cleanup.ps1
# Write-Host "🧹 Starting complete Docker cleanup..." -ForegroundColor Cyan

# # Stop containers
# docker-compose down -v
# Write-Host "✅ Containers stopped" -ForegroundColor Green

# # Remove all containers
# docker stop $(docker ps -aq) 2>$null
# docker rm $(docker ps -aq) 2>$null
# Write-Host "✅ Containers removed" -ForegroundColor Green

# # Remove all images
# docker image prune -a --force
# Write-Host "✅ Images cleaned" -ForegroundColor Green

# # Remove all volumes
# docker volume prune -a --force
# Write-Host "✅ Volumes cleaned" -ForegroundColor Green

# # Remove build cache
# docker builder prune -a --force
# Write-Host "✅ Build cache cleaned" -ForegroundColor Green

# # System cleanup
# docker system prune -a --volumes --force
# Write-Host "✅ System cleaned" -ForegroundColor Green

# # Show free space
# $drive = Get-PSDrive C
# Write-Host "`n💾 C: Drive Free Space: $([math]::Round($drive.Free/1GB, 2)) GB" -ForegroundColor Yellow

# Write-Host "`n🎉 Cleanup complete!" -ForegroundColor Green