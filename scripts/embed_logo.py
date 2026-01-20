"""Embed logo into HTML report as base64 data URI."""

import base64
import re
from pathlib import Path


def embed_logo(html_path: str, logo_path: str) -> None:
    """Replace logo src with embedded base64 data URI."""
    html_file = Path(html_path)
    logo_file = Path(logo_path)

    # Read and encode logo
    logo_bytes = logo_file.read_bytes()
    b64_string = base64.b64encode(logo_bytes).decode('utf-8')
    data_uri = f"data:image/jpeg;base64,{b64_string}"

    # Read HTML
    html_content = html_file.read_text(encoding='utf-8')

    # Replace any existing src (relative path or data URI) in the logo img tag
    html_content = re.sub(
        r'<img src="[^"]*" alt="Changan" class="logo">',
        f'<img src="{data_uri}" alt="Changan" class="logo">',
        html_content
    )

    # Write updated HTML
    html_file.write_text(html_content, encoding='utf-8')
    print(f"Logo embedded successfully into {html_path}")


if __name__ == "__main__":
    base_dir = Path(__file__).parent.parent
    html_path = base_dir / "clients/changan-auto/reports/engagement-analysis.html"
    logo_path = base_dir / "clients/changan-auto/logo.jpg"

    embed_logo(str(html_path), str(logo_path))
