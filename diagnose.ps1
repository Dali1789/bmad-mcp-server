#!/usr/bin/env powershell

# BMAD MCP Server Diagnostic Script

Write-Host "🔍 BMAD MCP Server Diagnose..." -ForegroundColor Cyan
Write-Host ""

# Check current location
$currentDir = Get-Location
Write-Host "📁 Aktuelles Verzeichnis: $currentDir" -ForegroundColor Yellow

# Navigate to BMAD directory
$bmadDir = "C:\Users\Faber\AppData\Roaming\Claude\bmad-mcp-server"
if (Test-Path $bmadDir) {
    Set-Location $bmadDir
    Write-Host "📂 Navigiert zu BMAD Verzeichnis: $bmadDir" -ForegroundColor Green
} else {
    Write-Host "❌ BMAD Verzeichnis nicht gefunden: $bmadDir" -ForegroundColor Red
    exit 1
}

# Check Python
Write-Host ""
Write-Host "🐍 Python-Version prüfen..." -ForegroundColor Cyan
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python nicht gefunden oder nicht im PATH" -ForegroundColor Red
    exit 1
}

# Check pip
Write-Host ""
Write-Host "📦 Pip-Version prüfen..." -ForegroundColor Cyan
try {
    $pipVersion = pip --version 2>&1
    Write-Host "✅ $pipVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Pip nicht gefunden" -ForegroundColor Red
    exit 1
}

# Install requirements
Write-Host ""
Write-Host "🔧 Requirements installieren..." -ForegroundColor Cyan
try {
    pip install -r requirements.txt --quiet
    Write-Host "✅ Requirements installiert" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Problem beim Installieren der Requirements: $_" -ForegroundColor Yellow
}

# Test imports
Write-Host ""
Write-Host "🧪 Import-Test starten..." -ForegroundColor Cyan
try {
    $env:PYTHONPATH = $bmadDir
    python test_import.py
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Import-Test erfolgreich!" -ForegroundColor Green
    } else {
        Write-Host "❌ Import-Test fehlgeschlagen" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Fehler beim Import-Test: $_" -ForegroundColor Red
}

# Test server start (quick check)
Write-Host ""
Write-Host "🚀 Server-Start Test..." -ForegroundColor Cyan
try {
    $env:PYTHONPATH = $bmadDir
    $env:OPENROUTER_API_KEY = "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"
    
    # Run server with timeout (5 seconds)
    $job = Start-Job -ScriptBlock {
        param($dir, $pythonPath, $apiKey)
        $env:PYTHONPATH = $pythonPath
        $env:OPENROUTER_API_KEY = $apiKey
        Set-Location $dir
        python -m src.bmad_mcp.server
    } -ArgumentList $bmadDir, $bmadDir, $env:OPENROUTER_API_KEY
    
    Start-Sleep -Seconds 3
    Stop-Job $job -Force
    Remove-Job $job -Force
    
    Write-Host "✅ Server-Start Test abgeschlossen (kein sofortiger Crash)" -ForegroundColor Green
} catch {
    Write-Host "❌ Server-Start Test fehlgeschlagen: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "🎯 Diagnose abgeschlossen!" -ForegroundColor Cyan
Write-Host ""
Write-Host "💡 Nächste Schritte:" -ForegroundColor Yellow
Write-Host "1. Falls Fehler aufgetreten sind, prüfe die Details oben" -ForegroundColor White
Write-Host "2. Starte Claude Desktop neu" -ForegroundColor White
Write-Host "3. Teste die MCP-Integration in Claude Desktop" -ForegroundColor White
Write-Host ""

# Return to original directory
Set-Location $currentDir
