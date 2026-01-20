"""Generate dashboard HTML using Kimi K2 from prompt file."""
import sys
from datetime import datetime
from pathlib import Path
from groq_kimi import query_kimi

base_dir = Path(__file__).parent
prompts_dir = base_dir / "prompts"
dashboards_dir = base_dir / "dashboards"

# Usage: python generate_dashboard.py [prompt_name] [version_name]
# Examples:
#   python generate_dashboard.py                          -> uses dashboard-header.md, auto version
#   python generate_dashboard.py ai-overview              -> uses ai-overview-dashboard.md
#   python generate_dashboard.py ai-overview v3-test      -> uses ai-overview-dashboard.md, named v3-test

prompt_name = sys.argv[1] if len(sys.argv) > 1 else "dashboard-header"
version = sys.argv[2] if len(sys.argv) > 2 else datetime.now().strftime("v%Y%m%d-%H%M%S")

# Find prompt file
prompt_file = prompts_dir / f"{prompt_name}.md"
if not prompt_file.exists():
    prompt_file = prompts_dir / f"{prompt_name}-dashboard.md"
if not prompt_file.exists():
    print(f"Error: Prompt file not found: {prompt_name}")
    print(f"Available prompts: {[f.stem for f in prompts_dir.glob('*.md')]}")
    sys.exit(1)

output_file = dashboards_dir / f"{version}.html"

prompt = prompt_file.read_text(encoding="utf-8")
print(f"Generating {version}...")

result = query_kimi(prompt, temperature=0.3)

# Strip markdown code fences if present
if result.startswith("```"):
    result = result.split("\n", 1)[1]
if result.endswith("```"):
    result = result.rsplit("```", 1)[0]

output_file.write_text(result.strip(), encoding="utf-8")
print(f"Done: {output_file}")
