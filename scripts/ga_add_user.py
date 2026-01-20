"""
Add users to Google Analytics properties.

Requires authentication with analytics.manage.users scope.
Run ga_auth_admin.py first to set up credentials.

Usage:
    uv run scripts/ga_add_user.py <property_id> <email> [role]

Examples:
    uv run scripts/ga_add_user.py 467150353 user@example.com VIEWER
    uv run scripts/ga_add_user.py 467150353 user@example.com ANALYST

Roles:
    VIEWER   - Can view reports (default)
    ANALYST  - Can view reports and create explorations
    EDITOR   - Can edit property settings
    ADMIN    - Full admin access
"""

import sys
import os

# Use admin credentials if available, otherwise fall back to default
ADMIN_CREDS = os.path.expanduser("~/ga_admin_credentials.json")
DEFAULT_CREDS = os.path.expanduser("~/application_default_credentials.json")

if os.path.exists(ADMIN_CREDS):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = ADMIN_CREDS
else:
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = DEFAULT_CREDS

from google.analytics.admin_v1alpha import (
    AnalyticsAdminServiceClient,
    AccessBinding,
    CreateAccessBindingRequest,
    ListAccessBindingsRequest,
)


VALID_ROLES = {
    "VIEWER": "predefinedRoles/viewer",
    "ANALYST": "predefinedRoles/analyst",
    "EDITOR": "predefinedRoles/editor",
    "ADMIN": "predefinedRoles/admin",
}


def add_user_to_property(property_id: str, email: str, role: str = "VIEWER"):
    """Add a user to a GA4 property with the specified role."""

    if role.upper() not in VALID_ROLES:
        print(f"Error: Invalid role '{role}'")
        print(f"Valid roles: {', '.join(VALID_ROLES.keys())}")
        sys.exit(1)

    role_resource = VALID_ROLES[role.upper()]
    property_resource = f"properties/{property_id}"

    client = AnalyticsAdminServiceClient()

    # Create the access binding
    access_binding = AccessBinding(
        user=email,
        roles=[role_resource],
    )

    request = CreateAccessBindingRequest(
        parent=property_resource,
        access_binding=access_binding,
    )

    try:
        result = client.create_access_binding(request=request)
        print(f"Successfully added {email} to property {property_id} as {role.upper()}")
        print(f"Access binding: {result.name}")
        return result
    except Exception as e:
        print(f"Error adding user: {e}")
        sys.exit(1)


def list_property_users(property_id: str):
    """List all users with access to a GA4 property."""

    property_resource = f"properties/{property_id}"
    client = AnalyticsAdminServiceClient()

    try:
        bindings = client.list_access_bindings(parent=property_resource)
        print(f"\nUsers with access to property {property_id}:")
        print("-" * 60)
        for binding in bindings:
            user = binding.user or "(unknown)"
            roles = [r.split("/")[-1] for r in binding.roles]
            print(f"  {user}: {', '.join(roles)}")
    except Exception as e:
        print(f"Error listing users: {e}")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    command = sys.argv[1]

    if command == "list" and len(sys.argv) >= 3:
        list_property_users(sys.argv[2])
    elif command == "add" and len(sys.argv) >= 4:
        property_id = sys.argv[2]
        email = sys.argv[3]
        role = sys.argv[4] if len(sys.argv) > 4 else "VIEWER"
        add_user_to_property(property_id, email, role)
    elif len(sys.argv) >= 3:
        # Legacy: direct property_id email [role] format
        property_id = sys.argv[1]
        email = sys.argv[2]
        role = sys.argv[3] if len(sys.argv) > 3 else "VIEWER"
        add_user_to_property(property_id, email, role)
    else:
        print(__doc__)
        sys.exit(1)
