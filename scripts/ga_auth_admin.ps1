# Authenticate with GA Admin API (includes user management permissions)
#
# This creates separate credentials for admin operations.
# The regular analytics.readonly credentials are not modified.
#
# Usage: .\scripts\ga_auth_admin.ps1

$clientSecretPath = "C:\Development\General Analytics\client_secret_335937140210-0b9u8oki65hjd9bcsnc7uic8ov51bp2u.apps.googleusercontent.com.json"
$outputPath = "$env:USERPROFILE\ga_admin_credentials.json"

Write-Host "Authenticating with GA Admin API (user management scope)..."
Write-Host ""

# Run gcloud auth with admin scopes
gcloud auth application-default login `
    --scopes="https://www.googleapis.com/auth/analytics.readonly,https://www.googleapis.com/auth/analytics.manage.users,https://www.googleapis.com/auth/cloud-platform" `
    --client-id-file="$clientSecretPath"

# Copy to admin credentials location
if (Test-Path "$env:APPDATA\gcloud\application_default_credentials.json") {
    Copy-Item "$env:APPDATA\gcloud\application_default_credentials.json" $outputPath -Force
    Write-Host ""
    Write-Host "Admin credentials saved to: $outputPath"
    Write-Host ""
    Write-Host "You can now use:"
    Write-Host "  uv run scripts/ga_add_user.py <property_id> <email> [role]"
    Write-Host "  uv run scripts/ga_add_user.py list <property_id>"
} else {
    Write-Host "Error: Credentials file not found after authentication"
    exit 1
}
