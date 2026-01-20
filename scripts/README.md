# Scripts

Utility scripts for Google Analytics and GTM management.

## GA User Management

Add or list users on GA4 properties.

### Setup (one-time)

Authenticate with admin permissions:

```powershell
.\scripts\ga_auth_admin.ps1
```

This creates separate admin credentials at `~/ga_admin_credentials.json` (doesn't affect your read-only MCP credentials).

### Usage

**Add a user:**
```powershell
uv run scripts/ga_add_user.py <property_id> <email> [role]

# Examples:
uv run scripts/ga_add_user.py 467150353 user@example.com VIEWER
uv run scripts/ga_add_user.py 467150353 analyst@example.com ANALYST
```

**List users:**
```powershell
uv run scripts/ga_add_user.py list <property_id>

# Example:
uv run scripts/ga_add_user.py list 467150353
```

### Roles

| Role | Description |
|------|-------------|
| `VIEWER` | Can view reports (default) |
| `ANALYST` | Can view reports and create explorations |
| `EDITOR` | Can edit property settings |
| `ADMIN` | Full admin access |

### Changan Auto Property IDs

| Property | ID |
|----------|-----|
| Country Picker | 468301281 |
| Germany | 467150353 |
| United Kingdom | 468326267 |
| Netherlands | 468349772 |
