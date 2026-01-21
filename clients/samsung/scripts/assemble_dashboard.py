"""
Assemble dashboard from approved HTML templates.

NO LLM GENERATION - pure template concatenation.

This script reads templates verbatim and assembles them in the order
specified by the config file. Templates are never modified.

Usage:
    uv run scripts/assemble_dashboard.py configs/scom-overview.json
"""

import json
import re
import sys
from pathlib import Path


def extract_section(content: str, marker: str) -> str:
    """
    Extract content between <!-- {marker} --> and <!-- END {marker} --> comments.

    Args:
        content: Full template content
        marker: Section marker (e.g., 'CSS', 'HTML', 'SCRIPT')

    Returns:
        Extracted content or empty string if not found
    """
    pattern = rf'<!--\s*{marker}\s*-->(.*?)<!--\s*END\s*{marker}\s*-->'
    match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)

    if match:
        return match.group(1).strip()
    return ''


def assemble(config_path: Path) -> str:
    """
    Assemble dashboard from templates in config-specified order.

    Args:
        config_path: Path to dashboard config JSON

    Returns:
        Complete HTML document as string
    """
    # Load config
    config = json.loads(config_path.read_text(encoding='utf-8'))

    # Resolve paths relative to samsung client directory
    client_dir = config_path.parent.parent
    templates_dir = client_dir / 'templates'
    output_path = client_dir / config['output']

    print(f"Config: {config_path.name}")
    print(f"Templates dir: {templates_dir}")
    print(f"Output: {output_path}")
    print()

    css_parts = []
    html_parts = []
    script_parts = []

    # Load base templates (fonts, tokens)
    print("Loading base templates:")
    for base_file in config.get('base', []):
        template_path = templates_dir / base_file
        if not template_path.exists():
            print(f"  WARNING: {base_file} not found")
            continue

        content = template_path.read_text(encoding='utf-8')
        css = extract_section(content, 'CSS')
        if css:
            css_parts.append(f'/* === {base_file} === */\n{css}')
            print(f"  [OK] {base_file} (CSS)")

    # Load component templates in ORDER
    print("\nLoading components (in order):")
    for i, component in enumerate(config.get('components', []), 1):
        template_path = templates_dir / component
        if not template_path.exists():
            print(f"  WARNING: {component} not found")
            continue

        content = template_path.read_text(encoding='utf-8')

        css = extract_section(content, 'CSS')
        html = extract_section(content, 'HTML')
        script = extract_section(content, 'SCRIPT')

        if css:
            css_parts.append(f'/* === {component} === */\n{css}')
        if html:
            html_parts.append(f'<!-- === {component} === -->\n{html}')
        if script:
            script_parts.append(f'// === {component} ===\n{script}')

        print(f"  {i}. {component}")
        print(f"     CSS: {'Y' if css else '-'}  HTML: {'Y' if html else '-'}  JS: {'Y' if script else '-'}")

    # Combine scripts (filter empty ones - but keep ones with actual code after comments)
    def has_code(script: str) -> bool:
        """Check if script has actual code, not just comments."""
        lines = script.strip().split('\n')
        for line in lines:
            stripped = line.strip()
            if stripped and not stripped.startswith('//'):
                return True
        return False

    script_content = '\n\n'.join(s for s in script_parts if has_code(s))
    has_scripts = bool(script_content.strip())

    # Build final HTML
    final_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{config.get("title", "Dashboard")}</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
{chr(10).join(css_parts)}
    </style>
</head>
<body>
{chr(10).join(html_parts)}
{"<script>" + chr(10) + script_content + chr(10) + "</script>" if has_scripts else ""}
</body>
</html>
'''

    # Write output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(final_html, encoding='utf-8')

    print(f"\n[OK] Written: {output_path}")
    print(f"  Size: {len(final_html):,} bytes")

    return final_html


def main():
    if len(sys.argv) < 2:
        print("Usage: uv run scripts/assemble_dashboard.py <config.json>")
        print("\nExample:")
        print("  uv run scripts/assemble_dashboard.py configs/scom-overview.json")
        sys.exit(1)

    config_path = Path(sys.argv[1])

    if not config_path.exists():
        # Try relative to script location
        script_dir = Path(__file__).parent.parent
        config_path = script_dir / sys.argv[1]

    if not config_path.exists():
        print(f"Error: Config file not found: {sys.argv[1]}")
        sys.exit(1)

    assemble(config_path)


if __name__ == '__main__':
    main()
