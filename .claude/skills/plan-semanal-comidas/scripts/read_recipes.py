#!/usr/bin/env python3
"""Read every .yaml recipe in a directory and print a table.

Usage: python read_recipes.py <recipes_directory>

Needs PyYAML (pip install pyyaml). Warns about missing or wrongly
typed required fields, so the planner knows which recipes it can
trust.
"""
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("Missing PyYAML. Install it with: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

REQUIRED_FIELDS = [
    "titulo", "tags", "raciones", "kcal_racion", "proteina_racion_g",
    "aceite_cucharillas", "ingredientes", "pasos",
]
NUMERIC_FIELDS = ["raciones", "kcal_racion", "proteina_racion_g", "aceite_cucharillas"]


def read_recipe(path):
    with path.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        return None
    return data


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)
    folder = Path(sys.argv[1])
    files = sorted(folder.rglob("*.yaml"))
    if not files:
        print(f"No .yaml files in {folder}")
        sys.exit(1)

    rows, warnings = [], []
    for f in files:
        try:
            data = read_recipe(f)
        except yaml.YAMLError as e:
            warnings.append(f"{f.name}: invalid YAML ({e}), skipping")
            continue
        if data is None:
            warnings.append(f"{f.name}: empty file or unexpected format, skipping")
            continue
        for field in REQUIRED_FIELDS:
            if field not in data:
                warnings.append(f"{f.name}: missing required field '{field}'")
        for field in NUMERIC_FIELDS:
            if field in data and not isinstance(data[field], (int, float)):
                warnings.append(f"{f.name}: '{field}' should be a number, got '{data[field]}'")
        rows.append((f.name, data))

    print("| file | title | variant_of | momento | kcal | protein_g | oil_tsp | sodio | tags |")
    print("|---|---|---|---|---|---|---|---|---|")
    for name, data in rows:
        momento = ",".join(data.get("momento", [])) or "(not set)"
        tags = ",".join(data.get("tags", [])) if isinstance(data.get("tags"), list) else data.get("tags", "")
        print(f"| {name} | {data.get('titulo', '?')} | {data.get('variante_de', '')} | {momento} | {data.get('kcal_racion', '?')} "
              f"| {data.get('proteina_racion_g', '?')} | {data.get('aceite_cucharillas', '?')} "
              f"| {data.get('sodio', '?')} | {tags} |")

    if warnings:
        print("\nWarnings:")
        for w in warnings:
            print(f"- {w}")


if __name__ == "__main__":
    main()
