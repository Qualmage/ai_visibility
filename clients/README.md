# Clients

Each client has their own folder with standardized structure for GTM, GA, and other Google services work.

## Active Clients

| Client | Folder | GA Account | GTM Account |
|--------|--------|------------|-------------|
| Changan Auto | `changan-auto/` | 336425779 | 6257643491 |
| Hisense | `hisense/` | TBD | TBD |

## Adding a New Client

1. Copy the `_template/` folder
2. Rename to client name (lowercase, hyphens)
3. Update the README.md with client details
4. Add to the table above

## Folder Structure

```
clients/
├── _template/           # Template for new clients
├── changan-auto/        # Changan Auto
│   ├── gtm/            # GTM configs, exports
│   ├── ga/             # GA reports, queries
│   ├── looker/         # Looker Studio
│   └── docs/           # Client documentation
├── hisense/             # Hisense
│   ├── gtm/
│   ├── ga/
│   ├── looker/
│   └── docs/
└── README.md           # This file
```
