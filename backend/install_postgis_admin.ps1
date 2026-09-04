# install_postgis_admin.ps1
# Run this script as Administrator to complete PostGIS 3.6.2 installation for PostgreSQL 18
# Right-click PowerShell -> "Run as administrator" then run this script

$postgisBase = "d:\CropShift Sqlx\CropShift Sqlx\backend\postgis_extracted\postgis-bundle-pg18-3.6.2x64"
$pgBase = "C:\Program Files\PostgreSQL\18"

Write-Host "Installing PostGIS 3.6.2 DLL dependencies into PostgreSQL 18..." -ForegroundColor Cyan

# Copy only DLL files from bin/ (skipping postgisgui subdirectory which caused errors)
Write-Host "Copying PostGIS dependency DLLs to PostgreSQL bin..." -ForegroundColor Yellow
Get-ChildItem "$postgisBase\bin\" -Filter "*.dll" -File | ForEach-Object {
    Copy-Item -Path $_.FullName -Destination "$pgBase\bin\" -Force
}
Write-Host "  Done: DLLs copied to PostgreSQL bin" -ForegroundColor Green

# Ensure extension SQL/control files are copied
Write-Host "Copying extension files..." -ForegroundColor Yellow
Copy-Item -Path "$postgisBase\share\extension\*" -Destination "$pgBase\share\extension\" -Force
Write-Host "  Done: extension files" -ForegroundColor Green

# Ensure lib DLLs are copied
Write-Host "Copying PostGIS lib DLLs..." -ForegroundColor Yellow
Get-ChildItem "$postgisBase\lib\" -Filter "*.dll" -File | ForEach-Object {
    Copy-Item -Path $_.FullName -Destination "$pgBase\lib\" -Force
}
Write-Host "  Done: lib DLLs" -ForegroundColor Green

Write-Host ""
Write-Host "Verifying PostGIS is now available in the database..." -ForegroundColor Cyan
$env:PGPASSWORD = "5432"
& "$pgBase\bin\psql.exe" -U postgres -p 5432 -d cropshift -c "SELECT name, default_version FROM pg_available_extensions WHERE name='postgis';"

Write-Host ""
Write-Host "Testing CREATE EXTENSION postgis..." -ForegroundColor Cyan
& "$pgBase\bin\psql.exe" -U postgres -p 5432 -d cropshift -c "CREATE EXTENSION IF NOT EXISTS postgis;"

Write-Host ""
Write-Host "DONE. PostGIS installation complete." -ForegroundColor Green
