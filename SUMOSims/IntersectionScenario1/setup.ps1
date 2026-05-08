# Automatically find the SUMO_HOME if installed via pip
    $pythonPath = python -c "import os, sumo; print(os.path.dirname(sumo.__file__))"
    $env:SUMO_HOME = $pythonPath
    $env:Path += ";$pythonPath\bin"
    
    Write-Host "SUMO_HOME set to: $env:SUMO_HOME" -ForegroundColor Cyan

# --- Generate Routes ---
# Calculate flows from sources to sinks as in map.flow.xml
Write-Host "Generating routes from flow definitions..." -ForegroundColor Yellow
duarouter -n map.net.xml -r map.flow.xml -o map.rou.xml
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: duarouter failed. Check your flow file and network file." -ForegroundColor Red
    exit 1
}

Write-Host "Setup Complete. You can now run: sumo-gui -c map.sumocfg" -ForegroundColor Green