"""Load cited pages JSON data into Supabase via SQL file generation.

Generates SQL INSERT statements that can be run via the Supabase MCP.
"""

import json

INPUT_FILE = "data/cited_pages.json"
OUTPUT_FILE = "data/cited_pages_insert.sql"
BATCH_SIZE = 500  # Rows per INSERT statement


def escape_sql(s: str) -> str:
    """Escape single quotes for SQL."""
    return s.replace("'", "''")


def main():
    # Load JSON data
    with open(INPUT_FILE, "r") as f:
        data = json.load(f)

    metadata = data["metadata"]
    rows = data["rows"]

    print(f"Loaded {len(rows)} rows from {INPUT_FILE}")
    print(f"Metadata: {metadata}")

    # Generate SQL file
    with open(OUTPUT_FILE, "w") as f:
        f.write(f"-- SEMrush Cited Pages Insert Script\n")
        f.write(f"-- Generated for: country={metadata['country']}, category={metadata['category']}\n")
        f.write(f"-- Total rows: {len(rows)}\n\n")

        # Process in batches
        for i in range(0, len(rows), BATCH_SIZE):
            batch = rows[i:i + BATCH_SIZE]
            batch_num = i // BATCH_SIZE + 1

            f.write(f"-- Batch {batch_num} ({len(batch)} rows)\n")
            f.write("INSERT INTO semrush_cited_pages (url, prompts_count, country, category, domain) VALUES\n")

            values = []
            for row in batch:
                url = escape_sql(row["url"])
                prompts_count = row["prompts_count"]
                values.append(f"  ('{url}', {prompts_count}, '{metadata['country']}', '{metadata['category']}', '{metadata['domain']}')")

            f.write(",\n".join(values))
            f.write("\nON CONFLICT (url, country, category) DO UPDATE SET prompts_count = EXCLUDED.prompts_count, fetched_at = NOW();\n\n")

    print(f"\nGenerated SQL file: {OUTPUT_FILE}")
    print(f"Total batches: {(len(rows) + BATCH_SIZE - 1) // BATCH_SIZE}")


if __name__ == "__main__":
    main()
