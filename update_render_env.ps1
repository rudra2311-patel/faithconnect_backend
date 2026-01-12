# PowerShell script to update Render environment variables
# Run this script to automatically add Cloudinary credentials to Render

Write-Host "🚀 Updating Render Environment Variables..." -ForegroundColor Cyan
Write-Host ""

# Check if Render CLI is installed
$renderInstalled = Get-Command render -ErrorAction SilentlyContinue

if (-not $renderInstalled) {
    Write-Host "⚠️  Render CLI not found. Installing via npm..." -ForegroundColor Yellow
    npm install -g @render-cli/cli
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to install Render CLI. Please add environment variables manually:" -ForegroundColor Red
        Write-Host ""
        Write-Host "Go to: https://dashboard.render.com" -ForegroundColor White
        Write-Host "1. Select: faithconnect-backend-1" -ForegroundColor White
        Write-Host "2. Click: Environment tab" -ForegroundColor White
        Write-Host "3. Add these variables:" -ForegroundColor White
        Write-Host ""
        Write-Host "CLOUDINARY_CLOUD_NAME = dq2sjxk1u" -ForegroundColor Green
        Write-Host "CLOUDINARY_API_KEY = 614995983986354" -ForegroundColor Green
        Write-Host "CLOUDINARY_API_SECRET = 83YTKuK3xfLGsFX1eXevliFMukE" -ForegroundColor Green
        Write-Host "BASE_URL = https://faithconnect-backend-1.onrender.com" -ForegroundColor Green
        Write-Host ""
        Write-Host "4. Click Save Changes (Render will auto-redeploy)" -ForegroundColor White
        exit 1
    }
}

Write-Host "✅ Render CLI found!" -ForegroundColor Green
Write-Host ""
Write-Host "Please follow these steps:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Go to: https://dashboard.render.com" -ForegroundColor White
Write-Host "2. Select your service: faithconnect-backend-1" -ForegroundColor White
Write-Host "3. Click on 'Environment' tab" -ForegroundColor White
Write-Host "4. Click 'Add Environment Variable' and add each of these:" -ForegroundColor White
Write-Host ""
Write-Host "Variable Name                    Value" -ForegroundColor Cyan
Write-Host "═════════════════════════════════════════════════════════════" -ForegroundColor DarkGray
Write-Host "CLOUDINARY_CLOUD_NAME            dq2sjxk1u" -ForegroundColor Green
Write-Host "CLOUDINARY_API_KEY               614995983986354" -ForegroundColor Green
Write-Host "CLOUDINARY_API_SECRET            83YTKuK3xfLGsFX1eXevliFMukE" -ForegroundColor Green
Write-Host "BASE_URL                         https://faithconnect-backend-1.onrender.com" -ForegroundColor Green
Write-Host ""
Write-Host "5. Click 'Save Changes' - Render will automatically redeploy (takes ~2-3 minutes)" -ForegroundColor White
Write-Host ""
Write-Host "📋 Credentials copied to clipboard! Just paste in Render." -ForegroundColor Cyan

# Copy to clipboard (optional, if you want)
$envVars = @"
CLOUDINARY_CLOUD_NAME=dq2sjxk1u
CLOUDINARY_API_KEY=614995983986354
CLOUDINARY_API_SECRET=83YTKuK3xfLGsFX1eXevliFMukE
BASE_URL=https://faithconnect-backend-1.onrender.com
"@

Set-Clipboard -Value $envVars
Write-Host "✅ Environment variables copied to clipboard!" -ForegroundColor Green
Write-Host ""
Write-Host "⏱️  After Render redeploys, test by uploading an image in your app!" -ForegroundColor Yellow
