# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Documentation Discipline

This project uses a doc-keeper agent to maintain documentation. **Invoke it proactively** after:
- Setup changes or configuration updates
- Completing significant tasks
- Encountering and solving problems
- Adding new clients or scripts

### Documentation Files
- **`DEVELOPMENT.md`** - High-level overview, session summaries, decision log, changelog
- **`docs/build-log.md`** - Detailed technical journal with "Plain English" explanations

### How to Invoke
The doc-keeper agent is defined in `.claude/agents/doc-keeper.md`. Use it via the Task tool with `subagent_type: "doc-keeper"`.

## Package Management

This project uses **uv** as the Python package manager. The virtual environment is located at `.venv`.

```bash
# Install dependencies
uv sync

# Add a package
uv add <package>

# Run a script
uv run <script.py>
```

## MCP Servers

This project has two MCP servers configured in `.mcp.json`:

### Google Tag Manager (`gtm-mcp-server`)
- **Purpose:** Manage GTM containers, tags, triggers, and variables
- **Auth:** Google OAuth (browser-based, handled automatically)
- **Account:** ChanganAuto (ID: 6257643491)

### Google Analytics (`analytics-mcp`)
- **Purpose:** Query GA4 properties, run reports, access real-time data
- **Auth:** Google Cloud Application Default Credentials
- **Project:** changan-gsc

### Re-authenticating

If you need to re-authenticate the Analytics MCP:

```bash
gcloud auth application-default login \
  --scopes https://www.googleapis.com/auth/analytics.readonly,https://www.googleapis.com/auth/cloud-platform \
  --client-id-file="client_secret_335937140210-0b9u8oki65hjd9bcsnc7uic8ov51bp2u.apps.googleusercontent.com.json"
```

To clear GTM MCP credentials:
```bash
rm -rf ~/.mcp-auth
```

## GTM Containers (Changan Auto)

| Country | Container ID | GTM ID |
|---------|--------------|--------|
| Country Picker | 199897711 | GTM-WNQPXL6N |
| Netherlands | 200516618 | GTM-NXD47XWV |
| United Kingdom | 200517971 | GTM-T8C77SQC |
| Germany | 200519277 | GTM-K9W9M2CP |
| Norway | 223438514 | GTM-PV97D2CT |
| Greece | 225792750 | GTM-NQKF32WT |
| Italy | 228802693 | GTM-KN4C3SKX |
| Spain | 228803373 | GTM-NVHNTJG4 |
| Poland | 228804673 | GTM-WQ57LP24 |
| Luxembourg | 237366763 | GTM-MZ2GB5XQ |
| Belgium | 237368834 | GTM-TZBH8HLQ |
