"""
Parse tv_prompts_semrush_import_v2.csv into structured JSON.

Output format (Option C):
- tagTree: Nested hierarchy for UI rendering with counts
- prompts: Array of prompts with their associated tags
"""

import csv
import json
from pathlib import Path
from collections import defaultdict


def build_tag_tree(all_tags: set) -> dict:
    """
    Build a nested tree structure from flat tags.
    Tags use __ as hierarchy delimiter.

    Example:
        "TV Reviews & Brand__Year Reviews__2026"
        becomes:
        TV Reviews & Brand → Year Reviews → 2026
    """
    tree = {}

    for tag in sorted(all_tags):
        parts = tag.split("__")
        current = tree

        for part in parts:
            if part not in current:
                current[part] = {"children": {}, "count": 0}
            current = current[part]["children"]

    return tree


def count_tags(prompts_data: list, tree: dict) -> dict:
    """
    Add counts to each node in the tree based on prompt associations.
    """
    # Build a flat count map first
    tag_counts = defaultdict(int)

    for prompt in prompts_data:
        for tag in prompt["tags"]:
            # Count this tag and all its ancestors
            parts = tag.split("__")
            for i in range(len(parts)):
                ancestor = "__".join(parts[:i+1])
                tag_counts[ancestor] += 1

    # Now apply counts to tree
    def apply_counts(node: dict, prefix: str = ""):
        for name, data in node.items():
            full_path = f"{prefix}__{name}" if prefix else name
            data["count"] = tag_counts.get(full_path, 0)
            if data["children"]:
                apply_counts(data["children"], full_path)

    apply_counts(tree)
    return tree


def parse_csv(csv_path: Path) -> tuple[list, set]:
    """
    Parse the CSV file and extract prompts with their tags.

    Returns:
        - List of prompt dicts with text and tags
        - Set of all unique tags
    """
    prompts = []
    all_tags = set()

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)  # Skip header row

        for row in reader:
            if not row:
                continue

            prompt_text = row[0].strip()
            tags = []

            # Remaining columns are tags
            for cell in row[1:]:
                tag = cell.strip()
                if tag:
                    tags.append(tag)
                    all_tags.add(tag)

            if prompt_text:
                prompts.append({
                    "text": prompt_text,
                    "tags": tags
                })

    return prompts, all_tags


def main():
    # Paths
    base_dir = Path(__file__).parent.parent
    csv_path = base_dir / "assets" / "tv_prompts_semrush_import_v2.csv"
    json_path = base_dir / "assets" / "tv_prompts.json"

    print(f"Reading: {csv_path}")

    # Parse CSV
    prompts, all_tags = parse_csv(csv_path)

    print(f"Found {len(prompts)} prompts")
    print(f"Found {len(all_tags)} unique tags")

    # Build tree
    tree = build_tag_tree(all_tags)

    # Add counts
    tree = count_tags(prompts, tree)

    # Build output
    output = {
        "meta": {
            "totalPrompts": len(prompts),
            "totalTags": len(all_tags)
        },
        "tagTree": tree,
        "prompts": prompts
    }

    # Write JSON
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"Written: {json_path}")

    # Print summary
    print("\nTag tree summary:")
    for parent in sorted(tree.keys()):
        count = tree[parent]["count"]
        children = len(tree[parent]["children"])
        print(f"  {parent}: {count} prompts, {children} children")


if __name__ == "__main__":
    main()
